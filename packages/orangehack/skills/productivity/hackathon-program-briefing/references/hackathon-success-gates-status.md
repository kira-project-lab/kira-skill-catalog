# Hackathon success gates and status tracker

Use this when Maxim asks “what counts as full success?”, “where are the gates?”, “do the gates have status?”, or similar for a hackathon / ML competition / exam-hackathon.

## Goal

Convert scattered event design, case, call brief, rules, run of show, and meeting notes into a single operational gate model.

## Source search pattern

Search the project/vault/workspace for:

- `gate`, `gates`, `acceptance`, `success`, `успех`, `полный успех`, `критерии`, `порог`, `зачёт`, `пересдача`, `дисквалификация`, `статус`;
- source PDFs and faithful Markdown mirrors;
- `Run of Show`, project brief, call brief, org meeting тезисы, rules/regulations, judging criteria.

If no dedicated gate tracker exists, say that directly. Do not pretend scattered criteria are a status plan.

## Full-success frame

For ML-practice / exam-hackathon projects, full success usually means these gates are all defined, communicated, and executable:

1. **Format gate** — event type is agreed: e.g. educational ML competition/practice, not a product hackathon.
2. **Case gate** — final participant case is published with task, data assumptions, metric, submit format, and allowed/disallowed resources.
3. **Platform/access gate** — participants can register, form teams, access materials, submit, and see public leaderboard behavior.
4. **Submission gate** — required bundle is explicit: submit, code/notebook/pipeline, dependencies, run instructions, short solution description, defense materials.
5. **Evaluation gate** — metric, public/private split, threshold or ranking logic, and private-score role are fixed.
6. **Understanding/defense gate** — defense checks pipeline, code, features, model, validation, errors, limitations, and reproducibility.
7. **Fairness gate** — AI tools, external data, plagiarism, manual CSV hacking, shared solutions, and disqualification triggers are stated.
8. **Retake/borderline gate** — borderline teams, weak metric, weak defense, failed reproducibility, and appeals/retakes have a procedure.
9. **Operations gate** — owners, deadlines, commissions, Q&A windows, announcements, and participant next actions are known.
10. **Result gate** — every team can be assigned a defensible final state: pass, borderline/manual review, retake, fail, or disqualified.

## Status tracker shape

Create or recommend one compact project-local note when the user wants status, for example:

```md
# Gates and Status

| Gate | What counts as passed | Status | Evidence/source | Owner | Deadline | Blocker / next action |
| --- | --- | --- | --- | --- | --- | --- |
| Format | Organizers agree on event type and non-goals | done / pending / blocked / open | `source.md:lines` | ... | ... | ... |
```

Recommended statuses:

- `done` — confirmed and ready to publish/execute;
- `pending confirmation` — drafted but needs organizer/stakeholder approval;
- `open question` — no decision yet;
- `blocked` — depends on another artifact/owner;
- `not started` — known required gate with no draft.

## Answering pattern

When answering without creating a tracker:

1. State the verdict: dedicated tracker exists / does not exist.
2. List what “full success” means as gates.
3. Name exact files where the gates currently live.
4. Separate real statuses from implied statuses.
5. If useful, recommend the tracker file path and columns.

Do not overclaim completion from the existence of drafts. Drafted criteria are not passed gates until source status or organizer confirmation supports that.
