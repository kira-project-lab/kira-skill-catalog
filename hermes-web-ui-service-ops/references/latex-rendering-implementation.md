# Hermes Web UI LaTeX rendering implementation notes

Captured from the May 2026 KaTeX implementation/debugging session for `hermes-web-ui`.

## Repo and deployment shape

- Upstream: `EKKOLearnAI/hermes-web-ui`
- Kira fork used for local changes: `kira-project-lab/hermes-web-ui`
- Local working tree: `/home/werserk/2-kira/hermes-web-ui`
- Live global package path: `/home/werserk/.npm-global/lib/node_modules/hermes-web-ui`
- Live service: `hermes-web-ui.service`, port `8648`

## Implementation pattern that worked

Use the existing `markdown-it` renderer instead of adding a separate Markdown stack.

1. Add dependencies:
   - `katex`
   - `@vscode/markdown-it-katex`
2. In `packages/client/src/components/hermes/chat/MarkdownRenderer.vue`, import/use the plugin with the existing `MarkdownIt` instance. **Pass the top-level `katex` engine explicitly** so the browser bundle does not use `@vscode/markdown-it-katex`'s nested KaTeX copy:

   ```ts
   import katex from 'katex'
   import markdownItKatex from '@vscode/markdown-it-katex'

   md.use(markdownItKatex, {
     katex,
     throwOnError: false,
   })
   ```
3. In `packages/client/src/main.ts`, import `katex/dist/katex.min.css` so generated KaTeX markup is styled.
4. Add regression tests around the client Markdown renderer.

Recommended test cases:

- Inline math: `$E = mc^2$`
- Block math: `$$\int_0^1 x^2\,dx = \frac{1}{3}$$`
- Matrix with line breaks: `\begin{pmatrix} ... \\ ... \end{pmatrix}`
- Currency/plain text guard: `$5` should not be parsed as math.
- Existing Markdown/code blocks should still render normally.

## Verification sequence

After patching:

1. Run the relevant client tests.
2. Run the production build.
3. Install/deploy the built package to the active global prefix.
4. Restart `hermes-web-ui.service`.
5. Verify:
   - service is active;
   - listener exists on `:8648`;
   - `/health` returns OK;
   - built assets contain KaTeX CSS/font references;
   - rendered chat DOM contains `.katex` elements for formulas;
   - browser DOM checks for representative stored formulas report: `hasRed: false`, `hasIntegral: true`, `hasSum: true`, and matrix blocks have `.mtable`/no `.katex-error`.

Node/Vitest can pass while the production browser bundle is broken, so include a real browser DOM smoke test after deployment for math commands (`\\int`, `\\frac`, `\\sum`, `\\pi`, `\\begin{pmatrix}`).

When deploying a local fork with `npm install -g --prefix /home/werserk/.npm-global .`, avoid relying on the current shell's working directory afterwards. Global installs can replace/remove the installed package path and may leave an agent tool session with a stale/deleted `cwd`. Prefer running deployment commands from a stable directory such as `/tmp` or `/home/werserk`, with explicit `cd /home/werserk/2-kira/hermes-web-ui` only inside the command.

## Double-backslash / stale-browser pitfall

If simple formulas render but commands like `\\frac`, `\\int`, `\\sum`, `\\pi`, or `\\begin{pmatrix}` appear red or as raw text, inspect the raw message text before changing CSS or the plugin.

Possible causes:

1. **Actual doubled command backslashes.** The message reaching KaTeX contains doubled command backslashes, e.g. `\\\\frac` in the actual source where LaTeX needs `\\frac`. KaTeX then treats the first `\\\\` as a linebreak/newline command and the following letters as text, so commands fail while plain variables such as `x^2` still work.
2. **Stale browser chunks after deploy.** The stored message and current renderer may be correct, but the open Web UI tab may still be running an old frontend JS/CSS chunk. This can show broken rendering even after the service and installed package are healthy.

Debug priority:

1. Locate the raw stored message in the Web UI DB (`~/.hermes-web-ui/hermes-web-ui.db`, `messages.content`) and inspect character-level backslashes with `repr`/char codes, not JSON-escaped display.
2. Render that exact raw message through the currently installed live package's `markdown-it` + `@vscode/markdown-it-katex` modules to confirm whether KaTeX can produce `∫`, `∑`, `.katex-display`, and matrix `mtable` output.
3. If raw content is correct but the browser DOM shows red KaTeX parser output where commands are split (`\\int` becomes an error on `\\i` + text `nt`, `\\frac` becomes `\\f` + `rac`, `\\sum` becomes `\\s` + `um`), suspect the plugin's bundled/nested KaTeX instance in the production browser bundle. Fix by importing top-level `katex` and passing it explicitly to `@vscode/markdown-it-katex`: `md.use(markdownItKatex, { katex, throwOnError: false })`.
4. If raw content is correct and the browser DOM used to be wrong before deploy, do a browser hard refresh / disable cache and reload, but do not stop there if incognito still reproduces it — inspect the DOM parser symptoms above.
5. If raw content is doubled, check JSON/string serialization boundaries or whether the assistant/test message was authored with extra escaping for Markdown/JSON rather than actual chat text.
6. Only after raw content, live package render, and browser DOM symptoms are understood should you revisit plugin choice or CSS.

Correct raw Markdown for chat text should look like:

```md
$$
\\int_0^1 x^2\\,dx = \\frac{1}{3}
$$

$$
A =
\\begin{pmatrix}
1 & 2 \\\\
3 & 4
\\end{pmatrix}
$$
```

Note: in source-code string literals this same content may require extra escaping, but the stored/rendered Markdown content should contain single command backslashes for LaTeX commands.