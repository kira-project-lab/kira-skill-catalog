#!/usr/bin/env node
/**
 * Sanity-check the installed Hermes Web UI Markdown/KaTeX renderer path.
 *
 * This is intentionally a Node/package-level probe, not a replacement for the
 * mandatory browser DOM smoke test after deployment. It catches missing deps,
 * wrong plugin wiring, and raw Markdown/backslash mistakes before restarting
 * the live service.
 *
 * Usage:
 *   node ~/.hermes/profiles/kira/skills/devops/hermes-web-ui-service-ops/scripts/check-installed-katex-rendering.mjs
 *   HERMES_WEB_UI_PACKAGE=/path/to/hermes-web-ui node .../check-installed-katex-rendering.mjs
 */
import { createRequire } from 'node:module'
import path from 'node:path'

const packageRoot = process.env.HERMES_WEB_UI_PACKAGE || '/home/werserk/.npm-global/lib/node_modules/hermes-web-ui'
const requireFromPackage = createRequire(path.join(packageRoot, 'package.json'))

const MarkdownIt = requireFromPackage('markdown-it')
const katex = requireFromPackage('katex')
const markdownItKatexModule = requireFromPackage('@vscode/markdown-it-katex')
const markdownItKatex = markdownItKatexModule.default || markdownItKatexModule

const md = new MarkdownIt({ html: false, breaks: true, linkify: true, typographer: true })
md.use(markdownItKatex, { katex, throwOnError: false })

const sample = `Inline: $E = mc^2$

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

$$
\\sum_{n=1}^{\\infty} \\frac{1}{n^2} = \\frac{\\pi^2}{6}
$$

Price is $5 and $6.
`

const html = md.render(sample)
const failures = []

if (!html.includes('class="katex')) failures.push('missing .katex markup')
if (!html.includes('∫')) failures.push('missing integral symbol')
if (!html.includes('∑')) failures.push('missing summation symbol')
if (!html.includes('mtable')) failures.push('missing matrix table output')
if (html.includes('katex-error') || html.includes('mathcolor="#cc0000"')) failures.push('contains KaTeX error/red parser output')
if (!html.includes('$5 and $6')) failures.push('currency-like dollar text was unexpectedly transformed')

const result = {
  packageRoot,
  katexVersion: katex.version,
  ok: failures.length === 0,
  failures,
}

console.log(JSON.stringify(result, null, 2))

if (failures.length > 0) {
  process.exitCode = 1
}
