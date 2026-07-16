#!/usr/bin/env python3
"""One-way Hermes Web UI prod -> live-dev state snapshot mirror.

Safety model:
- snapshots prod SQLite DBs with SQLite backup API while prod stays online;
- stops only hermes-web-ui-dev.service;
- backs up dev state under /home/werserk/9-archive;
- copies prod Web UI DB + Hermes profile state/sessions into dev;
- preserves/restores configured dev QA login rows;
- optionally resets dev QA password in both HERMES_WEB_UI_HOME DB and package-local dev DB.

Run from the host as the Web UI service user. Review constants before use.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import secrets
import shutil
import sqlite3
import subprocess
import time

PROD_WEBUI = Path('/home/werserk/.hermes-web-ui')
DEV_WEBUI = Path('/home/werserk/.hermes-web-ui-dev')
PROD_PROFILE = Path('/home/werserk/.hermes/profiles/kira')
DEV_PROFILE = Path('/home/werserk/.hermes/profiles/hermes-web-ui-dev')
DEV_PACKAGE_DB = Path('/home/werserk/2-kira/hermes-web-ui-dev/packages/server/data/hermes-web-ui.db')
DEV_CREDENTIAL_FILE = Path('/home/werserk/.hermes-web-ui-dev/secrets/kira-superadmin-credentials.env')
ARCHIVE_ROOT = Path('/home/werserk/9-archive/hermes-web-ui-dev-prod-state-mirror')


def run(*args: str) -> None:
    print('+', ' '.join(args))
    subprocess.run(args, check=True)


def sqlite_backup(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists():
        dst.unlink()
    src_con = sqlite3.connect(str(src))
    try:
        dst_con = sqlite3.connect(str(dst))
        try:
            src_con.backup(dst_con)
        finally:
            dst_con.close()
    finally:
        src_con.close()


def rows(db: Path, table: str) -> list[dict]:
    if not db.exists():
        return []
    con = sqlite3.connect(str(db)); con.row_factory = sqlite3.Row
    try:
        try:
            return [dict(r) for r in con.execute(f'SELECT * FROM {table}')]
        except sqlite3.OperationalError:
            return []
    finally:
        con.close()


def count(db: Path, table: str) -> int | None:
    if not db.exists():
        return None
    con = sqlite3.connect(str(db))
    try:
        try:
            return int(con.execute(f'SELECT COUNT(*) FROM {table}').fetchone()[0])
        except sqlite3.OperationalError:
            return None
    finally:
        con.close()


def db_counts(label: str, db: Path) -> dict[str, int | None]:
    tables = ['users', 'user_profiles', 'sessions', 'messages', 'session_row_versions',
              'session_usage', 'user_session_browser_prefs', 'user_session_read_state', 'user_ui_preferences']
    return {f'{label}.{table}': count(db, table) for table in tables}


def read_credential_username(default: str = 'kira') -> str:
    if not DEV_CREDENTIAL_FILE.exists():
        return default
    for line in DEV_CREDENTIAL_FILE.read_text().splitlines():
        if line.startswith('HERMES_WEB_UI_DEV_USERNAME='):
            return line.split('=', 1)[1].strip().strip('"\'') or default
    return default


def preserve_access(db: Path, username: str) -> dict[str, list[dict]]:
    user_rows = [r for r in rows(db, 'users') if r.get('username') == username]
    ids = {r['id'] for r in user_rows}
    profile_rows = [r for r in rows(db, 'user_profiles') if r.get('user_id') in ids]
    return {'users': user_rows, 'user_profiles': profile_rows}


def columns(con: sqlite3.Connection, table: str) -> list[str]:
    return [r[1] for r in con.execute(f'PRAGMA table_info({table})')]


def insert_or_replace(con: sqlite3.Connection, table: str, row: dict) -> None:
    cols = columns(con, table)
    data = {key: row[key] for key in cols if key in row}
    if not data:
        return
    con.execute(
        f"INSERT OR REPLACE INTO {table} ({','.join(data)}) VALUES ({','.join('?' for _ in data)})",
        list(data.values()),
    )


def restore_access(db: Path, preserved: dict[str, list[dict]]) -> None:
    if not db.exists() or not preserved.get('users'):
        return
    con = sqlite3.connect(str(db)); con.row_factory = sqlite3.Row
    try:
        id_map = {}
        for user in preserved['users']:
            existing = con.execute('SELECT id FROM users WHERE username = ?', (user['username'],)).fetchone()
            if existing:
                id_map[user['id']] = existing['id']
                continue
            next_id = user['id']
            if con.execute('SELECT 1 FROM users WHERE id = ?', (next_id,)).fetchone():
                next_id = con.execute('SELECT COALESCE(MAX(id), 0) + 1 FROM users').fetchone()[0]
            new_user = dict(user); new_user['id'] = next_id
            insert_or_replace(con, 'users', new_user)
            id_map[user['id']] = next_id
        for profile in preserved.get('user_profiles', []):
            new_profile = dict(profile)
            new_profile['user_id'] = id_map.get(profile['user_id'], profile['user_id'])
            insert_or_replace(con, 'user_profiles', new_profile)
        con.commit()
    finally:
        con.close()


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.scrypt(password.encode(), salt=salt.encode(), n=16384, r=8, p=1, dklen=64).hex()
    return f'scrypt:{salt}:{digest}'


def reset_dev_password(db: Path, username: str, password: str, profile: str = 'kira') -> None:
    if not db.exists():
        return
    con = sqlite3.connect(str(db)); con.row_factory = sqlite3.Row
    try:
        now = int(time.time() * 1000)
        user = con.execute('SELECT id FROM users WHERE username=?', (username,)).fetchone()
        if user:
            uid = user['id']
            con.execute('UPDATE users SET password_hash=?, role=?, status=?, updated_at=? WHERE id=?',
                        (hash_password(password), 'super_admin', 'active', now, uid))
        else:
            con.execute('INSERT INTO users (username,password_hash,role,status,created_at,updated_at,avatar) VALUES (?,?,?,?,?,?,?)',
                        (username, hash_password(password), 'super_admin', 'active', now, now, ''))
            uid = con.execute('SELECT id FROM users WHERE username=?', (username,)).fetchone()['id']
        try:
            if not con.execute('SELECT 1 FROM user_profiles WHERE user_id=? AND profile_name=?', (uid, profile)).fetchone():
                con.execute('INSERT OR REPLACE INTO user_profiles (user_id, profile_name, is_default, created_at) VALUES (?,?,1,?)',
                            (uid, profile, now))
            con.execute('UPDATE user_profiles SET is_default = CASE WHEN profile_name=? THEN 1 ELSE 0 END WHERE user_id=?', (profile, uid))
        except sqlite3.OperationalError:
            pass
        con.commit()
    finally:
        con.close()


def update_credential_file(username: str, password: str) -> None:
    DEV_CREDENTIAL_FILE.parent.mkdir(parents=True, exist_ok=True)
    text = DEV_CREDENTIAL_FILE.read_text() if DEV_CREDENTIAL_FILE.exists() else ''
    def set_line(buf: str, key: str, value: str) -> str:
        line = f'{key}={value}'
        pattern = rf'^{re.escape(key)}=.*$'
        if re.search(pattern, buf, re.M):
            return re.sub(pattern, line, buf, flags=re.M)
        return buf.rstrip() + ('\n' if buf.strip() else '') + line + '\n'
    text = set_line(text, 'HERMES_WEB_UI_DEV_USERNAME', username)
    text = set_line(text, 'HERMES_WEB_UI_DEV_PASSWORD', password)
    DEV_CREDENTIAL_FILE.write_text(text)
    DEV_CREDENTIAL_FILE.chmod(0o600)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--reset-password', action='store_true', help='Generate and set a new dev QA password in both dev auth DBs')
    parser.add_argument('--username', default=read_credential_username())
    args = parser.parse_args()

    stamp = time.strftime('%Y%m%d-%H%M%S', time.gmtime())
    backup = ARCHIVE_ROOT / stamp
    backup.mkdir(parents=True, exist_ok=True)
    print(json.dumps({'backup_root': str(backup), 'username': args.username}, indent=2))

    dev_db = DEV_WEBUI / 'hermes-web-ui.db'
    prod_db = PROD_WEBUI / 'hermes-web-ui.db'
    dev_state = DEV_PROFILE / 'state.db'
    prod_state = PROD_PROFILE / 'state.db'

    preserved = preserve_access(dev_db, args.username)
    (backup / 'preserved-dev-access.json').write_text(json.dumps(preserved, indent=2))
    sqlite_backup(prod_db, backup / 'prod-hermes-web-ui.snapshot.db')
    sqlite_backup(prod_state, backup / 'prod-kira-state.snapshot.db')
    if dev_db.exists(): shutil.copy2(dev_db, backup / 'dev-hermes-web-ui.before.db')
    if DEV_PACKAGE_DB.exists(): shutil.copy2(DEV_PACKAGE_DB, backup / 'dev-package-hermes-web-ui.before.db')
    if dev_state.exists(): shutil.copy2(dev_state, backup / 'dev-profile-state.before.db')
    if (DEV_PROFILE / 'sessions').exists():
        run('rsync', '-a', '--delete', str(DEV_PROFILE / 'sessions') + '/', str(backup / 'dev-profile-sessions.before') + '/')
    print(json.dumps({'before': {**db_counts('prod', prod_db), **db_counts('dev', dev_db)}}, indent=2))

    run('systemctl', '--user', 'stop', 'hermes-web-ui-dev.service')
    shutil.copy2(backup / 'prod-hermes-web-ui.snapshot.db', dev_db)
    restore_access(dev_db, preserved)
    shutil.copy2(backup / 'prod-kira-state.snapshot.db', dev_state)
    if (PROD_PROFILE / 'config.yaml').exists():
        shutil.copy2(PROD_PROFILE / 'config.yaml', DEV_PROFILE / 'config.yaml')
    run('rsync', '-a', '--delete', str(PROD_PROFILE / 'sessions') + '/', str(DEV_PROFILE / 'sessions') + '/')

    generated_password = None
    if args.reset_password:
        generated_password = secrets.token_urlsafe(18).replace('-', '').replace('_', '')[:22]
        reset_dev_password(dev_db, args.username, generated_password)
        reset_dev_password(DEV_PACKAGE_DB, args.username, generated_password)
        update_credential_file(args.username, generated_password)
        (backup / 'new-dev-password.txt').write_text(generated_password)
        (backup / 'new-dev-password.txt').chmod(0o600)

    run('systemctl', '--user', 'start', 'hermes-web-ui-dev.service')
    print(json.dumps({'after': db_counts('dev', dev_db), 'password_reset': bool(generated_password)}, indent=2))
    if generated_password:
        print('NEW_PASSWORD_FILE=' + str(backup / 'new-dev-password.txt'))


if __name__ == '__main__':
    main()
