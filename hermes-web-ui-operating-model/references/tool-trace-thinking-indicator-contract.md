# Tool trace visibility vs thinking indicator

## Contract

- The `show/hide tool calling` toggle controls transcript visibility for tool/trace rows.
- The live streaming thinking GIF (`.thinking-video`) is part of run lifecycle feedback and must stay visible while a run or abort state is active, even when tool traces are hidden.
- Do not gate the streaming indicator on `toolTraceVisible`.

## Regression check

- When the toggle is off, named tool rows disappear from the transcript, but the thinking GIF remains present during `chatStore.isRunActive || chatStore.abortState`.

## Test notes

- Unit tests that mount `MessageList` / `HistoryMessageList` may need:
  - a `naive-ui` mock for `useMessage`,
  - a `window.speechSynthesis` stub,
  - a `VirtualMessageList` stub exposing scroll methods when the real child is not mounted.
