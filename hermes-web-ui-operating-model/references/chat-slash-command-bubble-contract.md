# Chat slash-command bubble contract

Use this when a user types a leading-slash request such as `/plan`, `/goal`, or other `/...` commands that are intended as user input rather than system/tool output.

## Rule

- **User slash commands stay semantically user messages.**
- Do **not** render them in the trace/system/command log branch just because the text starts with `/`.
- Reserve `role: 'command'`, `TraceLine`, and similar service/trace UI for **system-generated command events** and runtime instrumentation.

## Rendering pattern

Recommended shape:

- keep the message in the normal bubble/message branch
- add a narrow UI flag for style only, e.g. `uiKind: 'slash-command'` or similar
- visually emphasize the prefix (`/plan`, `/goal`, etc.) with a subtle accent, pill, or monospace span
- keep the rest of the user text readable as a normal bubble

## Why

Slash commands are user intent, not tool telemetry. Rendering them as trace rows makes them look like internal calls and hides them from the transcript semantics.

## Pitfalls

- Do not overload `role: 'command'` for both user slash input and system command events.
- Do not make the preview/title/history pipeline infer that a leading slash means tooling.
- Do not let a command-style visual treatment change the message’s transcript class.
