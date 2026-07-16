# ML case brief refinement pattern

Use when turning a rough/OCR/imported ML hackathon case into a participant-facing case brief.

## Target shape

A refined case brief should be concise and operational:

1. **Task title and one-sentence goal** — what to predict and what metric to optimize.
2. **Context** — only the domain reason that explains why the prediction matters.
3. **Data** — train/test split, public/private leaderboard role, external-data rule.
4. **Metric** — metric name, optimization direction, and the actual formula when known. Do not use placeholder wording like “formula/submit constraints will be fixed later” when the metric formula is already known.
5. **Expected materials** — submit, code/pipeline, dependencies/run instructions, defense materials.
6. **Reproducibility and understanding** — code runs end-to-end, final submit can be regenerated, participants can explain their own code.
7. **AI tools** — allowed for assistance; not allowed as ununderstood code/solution.
8. **Assessment links** — point to the assessment regulation and any separate scoring example.
9. **Defense focus** — question themes, not a pitch script.
10. **Additional check** — compact clause for mismatch, irreproducibility, leakage, plagiarism, чужой submit/solution, missing code, or unexplained AI-generated code.

Avoid a standalone `Task` / `Задача` section if it only lists generic ML workflow steps; that often reads weak and duplicates requirements/defense. Fold the concrete participant obligation into the opening goal, data, materials, reproducibility, and defense sections instead.

## What to remove from rough source

- OCR/source provenance blurbs from participant-facing text.
- Repeated sections that restate the same deliverable/defense requirements.
- Overlong tables when a paragraph or short list is clearer.
- Internal scenario design, audit logic, and organizer promises.
- Placeholder language like “will be specified later” unless it is truly unresolved; if the metric is known, write the formula directly in LaTeX and explain variables briefly.
- Generic standalone `Задача` sections that only enumerate “analyze data → build features → validate → model → submit → defend”; they dilute the case rather than sharpen it.

## Naming and placement in Obsidian

If the refined case is not yet replacing the original, create a new canonical candidate such as `08 Case Brief Refined.md` and link it from the project `Index.md`. Keep imported/raw markdown in `sources/` and PDFs in `assets/`; do not mix them into the canonical numbered document sequence.
