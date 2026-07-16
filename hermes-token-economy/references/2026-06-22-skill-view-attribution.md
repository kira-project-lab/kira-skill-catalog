# Skill-view attribution notes — 2026-06-22

Use this reference when token reports show `skill_view` dominating tool-result bytes or when Maxim asks whether skills are loaded rationally.

## What to measure

Use Hermes `state.db`; `token-audit` strict no-raw mode may not store skill names, but the message table stores `skill_view` tool results.

Key tables:

- `sessions`: session title/source/model/token buckets and API/tool counts.
- `messages`: tool result messages with `tool_name='skill_view'` and JSON content containing `name`, `success`, `error`, and full payload.

## Minimal probes

Total `skill_view` payload over a recent window:

```sql
SELECT COUNT(*) AS calls,
       SUM(LENGTH(CAST(m.content AS BLOB))) AS bytes
FROM messages m
JOIN sessions s ON s.id = m.session_id
WHERE m.tool_name = 'skill_view'
  AND s.started_at > strftime('%s','now','-3 days');
```

Top sessions by `skill_view` bytes:

```sql
SELECT m.session_id, s.title, s.source,
       COUNT(*) AS calls,
       SUM(LENGTH(CAST(m.content AS BLOB))) AS bytes,
       s.input_tokens, s.output_tokens, s.reasoning_tokens,
       s.tool_call_count, s.api_call_count
FROM messages m
JOIN sessions s ON s.id = m.session_id
WHERE m.tool_name = 'skill_view'
  AND s.started_at > strftime('%s','now','-3 days')
GROUP BY m.session_id
ORDER BY bytes DESC
LIMIT 20;
```

Skill names are inside JSON content. Use Python for per-skill attribution:

```python
import sqlite3, json, collections
con = sqlite3.connect('/home/werserk/.hermes/profiles/kira/state.db')
con.row_factory = sqlite3.Row
by_skill = collections.defaultdict(lambda: collections.Counter())
for r in con.execute("""
  SELECT m.content
  FROM messages m JOIN sessions s ON s.id=m.session_id
  WHERE m.tool_name='skill_view'
    AND s.started_at > strftime('%s','now','-3 days')
"""):
    b = len((r['content'] or '').encode())
    obj = json.loads(r['content'] or '{}')
    name = obj.get('name') or 'FAILED_OR_UNKNOWN'
    by_skill[name]['calls'] += 1
    by_skill[name]['bytes'] += b
for name, c in sorted(by_skill.items(), key=lambda kv: kv[1]['bytes'], reverse=True)[:30]:
    print(name, dict(c), 'avg', round(c['bytes']/c['calls']))
```

For a specific session, print call order and duplicate loads:

```python
import sqlite3, json, collections
sid = '<session_id>'
con = sqlite3.connect('/home/werserk/.hermes/profiles/kira/state.db')
con.row_factory = sqlite3.Row
calls = []
for r in con.execute("""
  SELECT id, content
  FROM messages
  WHERE session_id=? AND tool_name='skill_view'
  ORDER BY id
""", (sid,)):
    obj = json.loads(r['content'] or '{}')
    name = obj.get('name') or obj.get('error', 'FAILED_OR_UNKNOWN')[:80]
    b = len((r['content'] or '').encode())
    calls.append((r['id'], name, b))
for i, (mid, name, b) in enumerate(calls, 1):
    print(f'{i:02d} msg={mid} {name} {b}B')
print('duplicates:', {k:v for k,v in collections.Counter(n for _,n,_ in calls).items() if v > 1})
```

## Interpretation rules

- `skill_view` cost is tool-result/context cost, not model reasoning.
- A large skill can be rational once and wasteful when reloaded unchanged in the same session.
- Repeated cognitive/render skills (`using-superpowers`, `cognitive-loop`, `critical-thinking`, `critical-expert-judgment`, `natural-language-render`, `anti-meta-spotlight`, `stop-slop`) often mean boot/render hygiene is paying full SKILL.md cost repeatedly.
- Domain skills are rational when the task matches the domain, but expensive skills such as `hermes-agent`, `task-first-test-prep`, `kira-obsidian-vault`, `hermes-web-ui-operating-model`, `test-driven-development`, and `skill-creator` should not be reloaded without a reason.
- Failed/ambiguous `skill_view` calls are usually small but indicate library hygiene problems; fix collisions or use qualified skill paths.

## Optimization targets

1. Add or use a per-session skill cache: if a skill was already loaded and its file mtime/hash is unchanged, avoid returning the full payload again.
2. Add compact/runtime summaries for heavy skills and keep long session detail under `references/`.
3. Add safe trace fields to token-audit for `skill_view`: `skill_name`, `success`, `error_type`, `content_bytes`, `cache_hit`, and `linked_files_count` without logging raw content.
4. Clean up duplicate/ambiguous skill names that cause failed calls and retry loops.
5. For short factual answers, avoid loading the full render/cognitive stack unless the governing instructions require it and the added quality matters.
