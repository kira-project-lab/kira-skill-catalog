---
name: hackathon-program-briefing
description: Use when Maxim asks to design, analyze, summarize, or prepare participant-facing materials for a hackathon, ML competition, case championship, exam-hackathon, org meeting, kickoff, Q&A, final defense, rules/regulations, judging criteria, anti-cheat/fairness process, or hackathon program timeline. Especially relevant for OrangeHack-style work where source materials include Run of Show, project briefs, commercial proposals, rules, evaluation rubrics, platform instructions, and Obsidian/Drive resources.
version: 1.0.0
author: Kira
license: MIT
metadata:
  hermes:
    tags: [hackathon, competitions, participant-briefing, program-design, orangehack, presentation]
---

# Hackathon Program Briefing

For ML-competition/practice events with train/test data, hidden answer keys, public/private leaderboard split, and scoring setup, use `references/ml-competition-data-bundle-and-scoring.md`.

For turning a prepared ML case bundle into a real OrangeHack-style platform competition record, data/scoring repo, split artifacts, sample submission, and launch checklist, use `references/ml-competition-platform-setup.md`.

When Maxim wants to set up an OrangeHack competition manually from an existing bundle and asks for source-faithful wording, do not create a rewritten derived narrative pack. Use `references/orangehack-source-first-platform-pack.md`: create a small `platform-ready/` layer for standardized filenames, participant/organizer separation, and platform-field copy blocks while keeping source wording authoritative.

Use this skill for hackathon/program communication work: turning scattered operational, commercial, legal, case, platform, and evaluation materials into clear participant-facing structure.

The key discipline: **separate internal source truth from participant-facing content**. Participants need the path, rules, deliverables, evaluation logic, help channels, and next actions — not commercial pricing, internal task statuses, contract clauses, or every organizer-side KPI.

## Core workflow

When Maxim asks to create a real event from scattered case/data/material sources, first build a source bundle and readiness checklist before platform entry. Keep raw attachments, Obsidian notes, web decks, and derived summaries separate; identify scoring blockers explicitly. See `references/ml-competition-case-bundle.md`.

1. **Collect source strata before synthesizing.**
   - Canonical event materials: Drive folder, Run of Show, project brief, case statement, rules/regulations, platform docs.
   - Reusable methodology materials: prior hackathon rules, anti-cheat procedures, submission bundle templates, evaluation rubrics.
   - Internal/commercial materials: proposal, contract, budget, delivery plan. Use only for scope/role context, not for participant slides.
   - Adjacent historical context: previous events, progress diaries, benchmarks. Use only to infer reusable patterns; do not mix facts across events.

2. **Classify every source by use.**
   - `participant-facing`: can be shown or converted into slides.
   - `organizer-facing`: useful for planning, not for participants.
   - `commercial/legal`: source of scope or constraints, not a participant handout.
   - `template-only`: reusable structure, not facts for the current event.
   - `adjacent/context`: background only unless confirmed.

3. **Find the participant contract.**
   Extract only what a participant must understand:
   - what the event is for;
   - who can participate and in what format;
   - timeline and hard deadlines;
   - platform/access path;
   - deliverables and submission format;
   - evaluation and defense logic;
   - fairness/anti-cheat rules;
   - communication channel and support process;
   - what happens after results.

4. **Compress to 2–6 briefing blocks.**
   For an org meeting, prefer 4–5 blocks unless the user asks for a full deck:
   1. purpose/context;
   2. participant journey and dates;
   3. task/case and expected result;
   4. submission/platform/deliverables;
   5. evaluation, checks, defense, and communication.

5. **Mark gaps explicitly.**
   Do not invent missing links, case text, platform URLs, registration instructions, jury names, defense slots, or criteria. Put them under “needs confirmation” or phrase as provisional.

6. **Render for the meeting, not for the archive.**
   User-facing output should be short, slide-ready, and operational. Avoid full audit narration unless requested.

## Participant-facing org meeting checklist

Cover these before ending the meeting:

- event purpose and what counts as a successful participant result;
- calendar with timezone and strict deadlines;
- where to register / how access is checked;
- where the case and updates will appear;
- what must be submitted and in what form;
- what materials to keep for reproducibility: code, README, dependencies, data/model notes, presentation;
- what is allowed/disallowed: external data, AI tools, collaboration, copied code, manual submission hacking;
- how evaluation works: metric/leaderboard plus review/defense if applicable;
- if the event is an academic practice/exam, the actual зачёт threshold and formula, not just “leaderboard + defense”;
- support process: channel, Q&A windows, question collection, publication of clarifications;
- next 1–3 actions immediately after the meeting.

## Academic assessment model pattern

When the hackathon doubles as university practice, exam, or зачёт/незачёт, do not default to “leaderboard is the result; defense is only a filter.” Ask/verify the academic rule first, then shape the scoring model around it.

Before finalizing the formula, run a **scenario-first pass**: enumerate how participants may behave and decide who should pass, need review, retake, or fail. Only then derive the numeric rubric. This prevents the formula from rewarding the wrong thing (pretty slides, copied SOTA, or accidental leaderboard luck) and keeps the stated academic purpose central.

For HCK-ALFA, the final useful public shape became a **short one-page assessment regulation**, not a long scenario explanation:

```text
FinalScore = 0.5 * LeaderboardScore + 0.5 * DefenseScore
```

with зачёт only when **both** are true by university/academic rule:

```text
FinalScore >= 3.5
DefenseScore >= 3.5
```

This double threshold keeps a high leaderboard from compensating a failed technical defense. Use scenario matrices as an internal design aid, but publish the concise regulation: formula in LaTeX, leaderboard conversion logic, and a defense criteria table. Do not add a mandatory-artifacts section unless Maxim asks for it; keep artifact/code/submit consistency as an audit layer instead of a main scoring table.

Prefer `DefenseScore` / `technical defense` over `presentation_result` unless the component is actually pitch quality. Add guardrails for non-reproducible work, inability to explain code, mismatch between defense and code, plagiarism/leakage, and no valid submit, but write them as a compact additional-check clause rather than a table of promises. Good public wording: the commission may lower the score, ignore individual results, or annul the team result for critical rule violations such as чужой submit/solution, missing code, irreproducible result with large deviation, forbidden data, leakage, plagiarism, or unexplained AI-generated code.

See `references/hackathon-assessment-models.md` for the reusable scenario matrix, concise regulation template, process-first ML defense rubric, and participant-facing wording.

When Maxim wants ML-practice defense criteria, prefer a **process-first rubric** over generic “presentation/code/submit match” criteria: data analysis, data-informed feature engineering, validation stability / leaderboard-overfitting control, and modeling decisions. Keep code-submit-defense consistency, reproducibility, plagiarism, leakage, and artifact validity as a separate audit layer, not as the main educational scoring criteria.

When a no-baseline ML leaderboard must be converted into float points, prefer robust private-score normalization over rank buckets: use P10/P90 bounds, `0` for no valid submit, and a continuous valid-submit range such as `2 + 8 * q_clipped`. See `references/leaderboard-robust-scoring.md` for formulas, example table, and public-regulation wording.

When writing or cleaning an ML case brief, make the participant-facing file concise and operational: task, context, data, metric, expected materials, reproducibility, AI-tools rule, assessment links, defense focus, and additional-check clause. Remove OCR/source provenance, duplicate deliverables sections, organizer-side scenario logic, and internal audit promises. If preserving the original, create a new refined candidate document and link it from the project index. See `references/ml-case-brief-refinement.md`.

## Anti-cheat and verification: how much to expose

Expose the principles, not the internal risk model:

- results should be reproducible;
- top solutions may be reviewed;
- organizers may request a submission bundle;
- participants must be able to explain their own pipeline and code;
- unauthorized external data, hidden APIs/network use, copied solutions, account/team manipulation, or hand-tuned submissions can lead to annulment or disqualification;
- if there is an appeal/protest process, state its channel and window; if not, do not imply one.

Do not show internal KPI math, residual-risk models, reviewer role acronyms, or draft statuses unless the user explicitly wants an organizer/internal version.

## Participant platform UX

When reviewing or designing a competition platform, separate **organizer console navigation** from **participant journey navigation**.

- Organizer/admin sidebars can expose entity-management panels: settings, cases, invitations, teams, submissions, certificates.
- Participant navigation should be shorter and action-oriented: `Соревнования`, `Моё участие`, `Профиль`, and optionally `Сертификаты`.
- Do not add global participant panels for `Команды`, `Кейсы`, or `Решения` unless there is a real cross-competition task; those usually belong inside competition/case context.
- Do not leave a visible `Dashboard` nav item if it is only a placeholder. Either remove it or make it a real `Моё участие` page with active competitions, team/case/submission status, pending join requests, deadlines, and certificate CTAs.
- Check desktop/mobile nav parity: if mobile has `Профиль`, desktop should not hide the only obvious profile route.
- For real local validation, create durable local participant/admin accounts and verify the exact browser routes under those identities. Anonymous `200` page loads or adjacent API checks are insufficient for participant screen acceptance.
- For OrangeHack local/dev work, checked-in test credentials are acceptable when they are explicitly documented as **public local validation fixtures** and not reused in stage/prod/customer demos. Prefer a canonical repo runbook such as `docs/runbooks/local-validation-accounts.md`, and link it from agent/development/security docs so future agents can find it.

See `references/participant-platform-ux.md` for the reusable participant UX pattern, implementation correctness checks, and OrangeHack-specific session note.
See `references/orangehack-local-validation-accounts.md` for the local account/credential setup, repo documentation pattern, and RBAC materialization pitfall.

## Common pitfalls

- **Mixing adjacent projects.** Alpha Campus Start, Academy AI HCK, NTO, FinamHack, and a current Alfa Magistracy hackathon may share templates but are not factual sources for each other.
- **Overexplaining OrangeHack.** One credibility line is enough for participants; do not turn the org meeting into an agency pitch.
- **Leaving deliverables vague.** If final rules are missing, give a provisional working standard: keep code, README, dependencies, data/source notes, and a defense presentation ready.
- **Treating leaderboard as final truth.** For ML competitions, remind participants that metric score can be followed by review, reproducibility checks, and defense. For academic practice, leaderboard may be only one weighted component; verify whether the defense is meant to compensate weak scores toward зачёт.
- **Writing assessment regulations as essays.** If Maxim asks for an evaluation/regulation file, keep it compact and table-driven: LaTeX formula first, then leaderboard conversion table, defense criteria table, artifact table, and short audit/penalty clause. Avoid explanatory “water”, scenario prose, long rationales, or point-by-point fraud taxonomy in the public file; keep scenario matrices as internal companion docs.
- **Forgetting historical rubrics.** When Maxim says older criteria existed, search session history and the Obsidian archive before inventing new rubric names. In Alfa/OrangeHack work, prior Alpha Campus Start rubrics included “Анализ текущего пользовательского пути” and Trendwatcher criteria such as “Качество отбора и оценки сигналов”; use them as reusable principles, not direct facts for a new event. See `references/hackathon-assessment-models.md`.
- **Ignoring calendar inconsistencies.** Check weekday/date conflicts and surface them before the deck is finalized.
- **Copying legal text into slides.** Translate rules into participant actions; keep contracts and personal/bank data out of participant materials.

## Useful reference notes

- `references/ml-practice-defense-rubric.md` — Maxim's preferred process-first ML practice defense rubric: data analysis, data-informed feature engineering, validation / leaderboard-overfitting stability, and modeling rationale, with audit checks kept separate.
- `references/hck-alfa-org-meeting-synthesis.md` — compact synthesis pattern from the HCK-ALFA / Alfa Magistracy session, including source strata and a recommended 5-block org meeting structure.
- `references/hackathon-success-gates-status.md` — gate/status tracker pattern for questions like “what counts as full success?”, “where are the gates?”, and “do the gates have status?”; separates scattered criteria from a real `gate → status → owner → blocker` plan.
