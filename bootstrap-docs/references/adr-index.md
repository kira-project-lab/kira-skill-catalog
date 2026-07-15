# Architecture Decision Records

This directory stores durable technical decisions for <PROJECT NAME>. ADRs are canonical when the decision constrains code, deployment, security, data ownership, or release behavior.

## Index

| ADR | Status | Decision |
| --- | --- | --- |
| [0001](0001-slug.md) | Accepted | One-sentence summary of the decision. |

## Rules

- Keep ADRs short: context, decision, consequences, alternatives, validation.
- Add a new ADR when a decision changes runtime behavior, deployment model, permission boundaries, data ownership, or product-critical flow semantics.
- Never rewrite an accepted ADR to mean something new — write a superseding ADR and cross-link both.
- Do not store private operational notes or one-off incident logs here; link from runbooks or audit reports instead of duplicating ADR text.
- Every ADR appears in the index table above with its current status.
