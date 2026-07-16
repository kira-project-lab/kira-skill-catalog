# Session title generation and browser tab sync

## When this pattern applies
Use this when adding or revising Hermes Web UI session naming, especially when the canonical `session.title` is generated from chat content, or when a separate UI feature syncs that title into the browser tab.

## Working pattern
- Keep canonical session naming and browser tab sync as separable features. Prefer separate PRs when one change is persistence/generation (`session.title`) and the other is presentation (`document.title`).
- Keep the user-facing control in `Settings -> Session` as one compact block.
- Use a toggle to enable/disable AI-generated titles.
- Keep the non-AI default path intact when the toggle is off.
- Store only minimal session-title-generation config in session settings. Prefer reusing the existing `auxiliary.title_generation` model/provider configuration instead of adding a second provider/model picker for the same class of task.
- Generate titles server-side so the same policy can be reused across clients.
- Prefer **server-owned post-run orchestration**: the run-completion path knows when assistant text exists, whether the current title is replaceable, and can emit one authoritative `title_generation` result with the final run event.
- Keep the client as a consumer of canonical `session.title`; it should not track title-generation request state or decide readiness/replaceability.
- Sync `document.title` from the active session title in the chat view only in the browser-tab feature path; do not couple tab-title changes to AI title generation.

## Implementation notes
- Use a dedicated API endpoint for manual/debug title generation instead of overloading rename endpoints, but prefer server-side automatic generation from the run-completion path so clients do not orchestrate model calls.
- Keep controllers thin: put title prompt building, model resolution, generation, and apply/skip policy in a session-title service rather than in `controllers/hermes/sessions.ts`.
- Reuse existing auxiliary-model/provider resolution where possible (`title_generation`) instead of hand-rolling fetch logic for Anthropic/OpenAI/Codex variants in the controller.
- Make automatic generation idempotent on the server; client-side in-memory guards are only a stopgap and should be removed once run completion owns orchestration.
- Use hybrid naming: create the deterministic first-user-message fallback immediately, then replace it with AI output only after the first non-empty assistant text reply and only if the title is still auto-generated.
- If AI generation fails, preserve the existing deterministic fallback/current title rather than leaving the session untitled or clearing it.
- Keep the prompt concise and avoid duplicating logic that is already implemented in code.
- Centralize fallback helpers (`firstMeaningfulUserMessage`, `firstMeaningfulAssistantMessage`, `buildStandardSessionTitle`, `isReplaceableAutoTitle`) so server creation, client display heuristics, and generation guards cannot drift.
- Use one standard fallback length everywhere. In the current implementation this is 40 characters plus `...` when truncated; drift between 40-char, 100-char, and full-message fallbacks can make the server misclassify an automatic title as manual and skip AI replacement.

## Meaningful-message rule
- Define the source messages by content, not by role alone.
- Ignore empty assistant turns and assistant turns that only contain tool calls when choosing the first assistant reply.
- Ignore empty user turns when choosing the first user message.
- Keep the client-side heuristic and the server-side generator aligned so the same conversation produces the same title candidate everywhere.
- When the first meaningful assistant reply is not the first assistant role turn, update the prompt and the local heuristic together.
- Phrase the prompt explicitly around the first meaningful user message and first meaningful assistant reply so the model does not summarize the wrong slice of the conversation.
- A title generation flow is only expected to run when the session has: one meaningful user message, one non-empty assistant text reply, generation enabled in the active profile, and a provider/model that resolves at runtime.
- If the first assistant turn is empty or tool-only, wait for the first assistant text reply before expecting a generated title.
- If the session already has a manual custom title that differs from the standard first-message fallback, do not expect automatic regeneration to overwrite it.

## User sequence that reliably triggers generation
1. Open the intended profile and confirm Session title generation is enabled in Settings.
2. Keep the title on the standard first-message fallback or create a fresh session so the generator is allowed to replace it.
3. Send a normal, non-empty user message.
4. Wait for the first assistant message that contains actual text content, not only tool calls.
5. Allow the run to complete; the server should trigger generation once from the run-completion path and include a `title_generation` result/reason in the completion payload.
6. If the title still does not change, inspect the server generation reason (`manual_title`, `not_ready`, `disabled`, provider/model failure) before changing the message-selection heuristic.

## Verification
- Confirm the settings UI renders the compact control actually intended for the PR. If provider/model selection is handled by auxiliary config, do not require a duplicate model selector in Session settings.
- Confirm canonical `session.title` changes independently from browser tab behavior; tab-title sync belongs to the presentation PR/path.
- Confirm the tab title changes when the session title changes only when the tab-sync feature is in scope.
- Confirm the default non-AI naming still works when generation is disabled.
- Run the narrow UI test for the settings section and a full build before declaring the feature done.
- If title generation is expected to call the model, verify the request path with a regression test that exercises the exact conversation slice, not just a mocked happy-path helper.
- Add a regression case for the first meaningful user message plus the first non-empty assistant text reply, including an assistant tool-call-only turn before the text reply.
- Add a regression case for long first user messages where an existing fallback title may be 40-char truncated, 100-char truncated, or the full first message; all automatic fallback variants should be replaceable by AI.

## Live runtime verification
- A build, healthy `/health`, and served-bundle token check only prove deployment. They do **not** prove AI title generation works.
- For live verification on `hermes.dev.ops.kiraproject.ru`, exercise the UI end-to-end: authenticate, select the intended profile, create a fresh session, send a normal message, wait for a non-empty assistant reply and run completion, then inspect whether the sidebar/DB title changed from deterministic fallback to AI title.
- If UI login is blocked by password state but local host access is available, create a short-lived user JWT from the Web UI token (`HERMES_WEB_UI_HOME/.token`) using the same HS256 shape as `middleware/user-auth.ts`, set it in `localStorage.hermes_api_key`, and set `localStorage.hermes_active_profile_name` to the test profile before reloading. Use this only for local/dev verification, not as a user-facing auth workaround.
- Do **not** publish JWTs through `dist/client` or any static public path for browser tooling. Prefer injecting the token directly into the browser context/localStorage; if a public temp auth file is unavoidable, replace/delete it immediately and verify the public URL no longer returns token JSON.
- Use the manual/debug endpoint to isolate generation after a completed session: `POST /api/hermes/sessions/:id/generate-title?profile=<profile>` with `Authorization: Bearer <jwt>` and `X-Hermes-Profile`. Treat `{ applied:false, reason:<reason> }` as the ground truth before guessing at UI bugs.
- Cross-check the SQLite session row and messages when needed: the session title should start as the standard fallback, messages should include a non-empty assistant text reply, and the manual endpoint should either apply an AI title or return a concrete skip reason.

## Pitfalls
- Do not preview or duplicate the fallback copy in the settings UI if the goal is to keep the block compact.
- Do not let repeated lifecycle updates trigger multiple title-generation requests for the same session.
- Do not couple browser tab sync to AI title generation. `document.title` should consume the canonical session title; AI generation should only produce/update that canonical title.
- Route-gate browser tab titles: show the session title only on `hermes.session` (or the equivalent session detail route). When the user navigates away to skills, history, settings, or any other section, restore the product title immediately on route change or component unmount.
- Add a regression test that proves both directions: session route displays the session title, and leaving the session route restores the default title.
- Do not change the first-user/first-assistant heuristic before checking provider/runtime alias resolution. A config may say `openai` while the runtime preset expects `openai-api`, and the visible symptom is "title generation does nothing" even though the message selection is fine.
- Use the **hybrid fallback → AI override** contract. Even when AI title generation is enabled, apply the deterministic first-user-message fallback immediately after the first user message so the list/tab is not blank while waiting for the assistant.
- Trigger AI title generation only after the first non-empty assistant text reply. If the model returns a valid title, it may replace the deterministic fallback.
- Do not overwrite manual titles: on the server, allow AI rename only when the current title is a known replaceable automatic state. Comparing to a single `standardTitle` string is fragile if different paths use different truncation lengths.
- Prefer durable title provenance when the schema can change: `title_source`/equivalent (`auto`, `ai`, `manual`) is safer than guessing manual intent from string equality.
- When schema cannot change yet, make `isReplaceableAutoTitle` backward-compatible with historic fallback variants, including empty title, preview-derived title, full first-message title, 40-char fallback, and 100-char fallback.
- Treat `/generate-title` response semantics as authoritative: the client should apply `title` only when `applied === true`; `applied: false` may carry the current fallback/current title for display, but must not rename the session.
- On the server, when title generation fails or returns an empty/invalid title, return `applied: false` and preserve the existing deterministic fallback/current title rather than clearing it.
- Add regression tests for timing and fallback separately: (1) deterministic fallback appears immediately after user send, (2) title generation only after first non-empty assistant reply, (3) failed/empty generation leaves the fallback unchanged, (4) manual title is not overwritten by AI, (5) long fallback variants are still considered auto-generated and replaceable.
- In tests, keep provider aliases, auxiliary config keys (for example `title_generation` vs `session_title_generation`), and fetch/model mocks aligned with the runtime path being exercised; otherwise the regression can fail for the wrong reason.
- Do not assume title generation is broken just because the visible title stays unchanged; it may be blocked by an existing manual title, by drift between fallback algorithms, or by a session that has not yet produced a real assistant text reply.
- Do not assume a successful normal chat response means the title-generation model call works. In dev, normal sessions can answer through the bridge while the title generator's direct provider HTTP call fails separately.
- Be especially careful with `openai-codex`/Codex-style direct HTTP title generation: calling a ChatGPT/Codex backend endpoint directly can receive Cloudflare `403` challenge HTML even when the main chat flow works. If `/generate-title` returns `reason: model_failed` and logs show a 403 Cloudflare challenge from `chatgpt.com/backend-api/codex/chat/completions`, the fix is provider/runtime routing (use an existing bridge/runtime model path or configure `auxiliary.title_generation` to a provider that can be called server-side), not message-selection heuristics.
- When routing title generation through Agent Bridge, verify both layers: the profile worker must implement `action == "auxiliary_llm"`, and the multi-profile broker must also forward `auxiliary_llm` to the correct profile worker. A normal `chat`/`context_estimate` bridge success can still hide `unknown action: auxiliary_llm` at the broker layer.
- Add a broker-level regression test for auxiliary LLM routing when profile workers are involved, not only a session-controller mock. The live symptom is: chat completes, title stays fallback, logs show `unknown action: auxiliary_llm`, and the correct fix is to route that action through the broker using the same profile/worker-key logic as existing LLM-facing actions.
