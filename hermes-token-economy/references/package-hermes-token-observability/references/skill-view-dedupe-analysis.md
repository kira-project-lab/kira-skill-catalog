# skill_view dedupe analysis notes

These notes came from diagnosing repeated `skill_view` payloads in Kira's Hermes profile. Use them as patterns, not as fixed claims about every installation.

## What “context loading” means

A Hermes model request can include SOUL/USER/project context, conversation history, tool results, tool schemas, and compressed summaries. A `skill_view` result is just another tool result in history, so every repeated full `SKILL.md` increases later input context.

## Distinguish compression from repeated skill loading

Compression can be expensive, but it may only pay for earlier context growth.

Evidence pattern to check:

- repeated `skill_view` rows in the original session;
- `messages.compacted = 0` and `active = 1` on those rows means the repeats happened before compaction;
- `compress_%` sessions with `tool_call_count = 0` and no `skill_view` rows mean compression did not itself reload skills;
- compression input can still be high because the original history already contained repeated skill payloads.

## SQLite probes

Count recent `skill_view` payload:

```sql
select count(*) as calls,
       sum(length(cast(m.content as blob))) as bytes
from messages m
join sessions s on s.id = m.session_id
where m.tool_name = 'skill_view'
  and s.started_at > strftime('%s','now','-3 days');
```

Find duplicate skill loads by session. Parse `m.content` JSON in Python and group by `obj.name`; failed calls may have no `name` and should be counted separately as lookup noise.

Check compaction state for a session:

```sql
select count(*) as n,
       sum(compacted) as compacted,
       sum(case when active = 0 then 1 else 0 end) as inactive
from messages
where session_id = ?;
```

Check whether compression sessions called skills:

```sql
select s.id, s.title, s.input_tokens, s.output_tokens, s.reasoning_tokens,
       count(m.id) as skill_view_calls
from sessions s
left join messages m on m.session_id = s.id and m.tool_name = 'skill_view'
where s.id like 'compress_%'
group by s.id
order by s.started_at desc
limit 20;
```

Summarize tool payload by byte size:

```sql
select m.tool_name,
       count(*) as calls,
       sum(length(cast(m.content as blob))) as bytes
from messages m
where m.session_id = ?
  and m.tool_name is not null
group by m.tool_name
order by bytes desc;
```

## Interpretation rules

- Repeating the same skill several times with `compacted=0` is a direct duplicate-load problem, not a compression-preservation behavior.
- A first domain skill load can be rational; repeated unchanged loads in the same live session are suspect.
- Repeated render/cognitive skills usually indicate mandatory boot wording is too literal.
- Failed ambiguous skill lookups are small but signal library naming cleanup is needed.
- If post-compaction behavior is the concern, use compact summaries or cache-hit markers rather than full reloads.

## Profile-local mitigation sketch

A `transform_tool_result` plugin can dedupe without core Hermes changes:

1. if `tool_name != 'skill_view'`, return nothing;
2. parse result JSON;
3. ignore failures and linked-file loads unless intentionally tracing them;
4. compute content hash from the full result or `content` field;
5. cache by `session_id + name + file_path`;
6. first load passes through;
7. repeated same hash returns compact JSON with `cached: true` and `full_content_loaded_earlier: true`;
8. changed hash passes through and updates cache;
9. fail open on any exception.

Add token-audit fields for validation: `skill_name`, `cache_hit`, `original_bytes`, `emitted_bytes`, `saved_bytes`, `content_hash_prefix`.
