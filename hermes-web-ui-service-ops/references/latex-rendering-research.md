# Hermes Web UI LaTeX / math rendering research

Use this note when evaluating or implementing LaTeX visualization in `hermes-web-ui` chat messages.

## Findings from May 2026 check

Target repo: `EKKOLearnAI/hermes-web-ui`.

Observed upstream package metadata:

- Package name: `hermes-web-ui`
- Version checked locally/npm: `0.5.35`
- Repository: `https://github.com/EKKOLearnAI/hermes-web-ui`
- Description: self-hosted AI chat dashboard for Hermes Agent.

Searches performed against upstream issues/PRs:

- `latex`
- `LaTeX`
- `math`
- `katex`
- `KaTeX`
- `MathJax`
- `markdown math`
- `markdown-it`

Result at time of check: no relevant upstream issues or PRs were found.

Local installed package check under `/home/werserk/.npm-global/lib/node_modules/hermes-web-ui` found:

- `markdown-it` is present.
- No explicit math-rendering dependency was present for:
  - `katex`
  - `mathjax`
  - `remark-math`
  - `rehype-katex`
  - `markdown-it-texmath`
  - `markdown-it-katex`

Sampled fork check: inspected `package.json` in 150 forks sampled by stargazers/newest/oldest; no math-rendering dependency hits were found.

## Interpretation

If Markdown renders but formulas such as `$x^2$` or `$$...$$` remain plain text, assume LaTeX visualization is not implemented rather than hidden behind settings, unless a newer build proves otherwise.

## Recommended implementation direction

Because the app already uses `markdown-it`, the least invasive implementation is usually:

1. Add a Markdown math plugin compatible with `markdown-it`, for example `markdown-it-texmath` or `markdown-it-katex`.
2. Add `katex` and load KaTeX CSS in the client bundle.
3. Support at minimum:
   - Inline math: `$x^2 + y^2 = z^2$`
   - Block math: `$$ ... $$`
4. Consider support for `\(...\)` and `\[...\]` if the plugin can do this safely.
5. Verify message sanitization does not strip the generated KaTeX HTML/MathML.
6. Verify rendered DOM contains `.katex` / `.katex-mathml` nodes and that CSS is loaded.

## Suggested upstream issue title

`Render LaTeX/math in chat messages`

## Suggested acceptance checks

- Inline formula renders visually in assistant and user messages.
- Block formula renders on its own line with correct spacing.
- Existing Markdown rendering still works.
- Code blocks containing `$...$` are not interpreted as math.
- No raw unsafe HTML execution is introduced by the math plugin configuration.
