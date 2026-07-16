# Live-dev session inventory

Use this reference when you need to inspect what sessions exist on the live-dev host or answer questions about their dates/range.

## Canonical live-dev session DB

- UI/runtime data DB: `/home/werserk/.hermes-web-ui/hermes-web-ui.db`
- Profile-scoped Hermes agent state DB: `/home/werserk/.hermes/profiles/hermes-web-ui-dev/state.db` (not the same thing as the UI session inventory)

## Quick probes

```bash
sqlite3 -header -column /home/werserk/.hermes-web-ui/hermes-web-ui.db \
  "select strftime('%Y-%m', started_at, 'unixepoch') as ym, count(*) as n from sessions group by ym order by ym desc;"

sqlite3 -header -column /home/werserk/.hermes-web-ui/hermes-web-ui.db \
  "select count(*) as total, datetime(min(started_at),'unixepoch','localtime') as first_session, datetime(max(started_at),'unixepoch','localtime') as last_session from sessions;"
```

## Notes

- If the profile-scoped state DB has no session rows, do not assume the host has no sessions; check the UI DB above.
- For date questions, prefer the DB timestamps over the rendered card labels.
