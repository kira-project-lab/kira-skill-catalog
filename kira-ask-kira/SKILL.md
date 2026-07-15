---
name: kira-ask-kira
description: Consult Kira only when the task explicitly asks for her or requires Kira-owned knowledge or memory. Kira advises; she does not implement or replace repository research.
---

# Consulting Kira (advisor)

Kira is a roster agent (`hermes_gateway`) with deep, persistent knowledge of
the owner's life, priorities, and the Kira platform infrastructure. She is an
**advisor, not an executor**: she answers questions and arbitrates; she does
not write code or run tasks.

## When to consult Kira

- The assigned task explicitly asks you to consult Kira.
- The next decision requires knowledge or memory that belongs to Kira and is
  not available in the assigned issue, repository, or authoritative docs.

## When NOT to consult

- Anything the dev pipeline rules already decide.
- Technical questions answerable from the repo or docs — delegate bounded research to
  an engineer instead.
- Ordinary planning, decomposition, review, release, and prioritization within
  the assigned direction.
- A generic desire for a second opinion.
- Pure execution work — never assign implementation issues to Kira.

## How to ask

Create a child issue assigned to Kira (or wake her on an existing one) with:

1. **One concrete question** — not a bundle. One issue per question.
2. **Full context** — she has her own memory but not your run context: state
   the direction, the conflict, what you already tried.
3. **Options if you have them** — she arbitrates best between explicit
   alternatives.

Treat her answer as evidence and advice, not command: you remain accountable
for the technical decision. Close the advisory once its answer is incorporated.
