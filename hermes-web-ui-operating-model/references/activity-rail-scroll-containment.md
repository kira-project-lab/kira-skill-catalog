# Activity rail scroll containment

Use this reference when polishing Hermes Web UI's left activity rail, sidebar navigation, collapse-button area, or adjacent session/chat panes.

## Contract

- Treat the activity rail header/collapse area as its own fixed visual region, not as part of the scrollable nav flow.
- The nav list should start below the shared workspace header height. Prefer a real layout separation such as `margin-top: $header-height` plus small internal nav padding, rather than a single enlarged `padding-top` that lets scrollable content visually occupy the header region.
- Position the collapse button independently from the nav list flow so it cannot push, overlap, or appear to scroll with nav items. Absolute positioning inside the rail is acceptable when the rail itself is the containing block.
- In collapsed/icon-only mode, re-center the collapse button explicitly; do not rely on margins inherited from the expanded rail.
- Keep adjacent panes independent: the session dock/header and the activity rail should meet at separators, but neither pane's scrollable content should visually pass through the other's header/separator area.

## Regression checks

- Add/update a source contract for the rail CSS so future edits do not reintroduce the old `padding-top: calc(#{$header-height} + …)` approach on the scrollable nav list.
- Check for both positive and negative expectations:
  - nav has a header-height `margin-top` and small local `padding-top`;
  - collapse button is positioned outside the nav flow;
  - old combined padding/header-offset rule is absent.
- Browser QA should include a forced nav scroll and hit/geometry inspection near the top rail region: nav items should not occupy or intercept the header/collapse area.
- For live-dev UI polish, finish with focused test(s), `git diff --check`, commit/push to `origin/dev`, restart `hermes-web-ui-dev.service`, verify `/health` reports the pushed commit, and visually verify `https://hermes.dev.ops.kiraproject.ru/`.

## Pitfall

If Maxim describes “просвечивание”, “скролл через разделитель”, or a header area not being an independent section, do not solve it by only nudging border height or z-index. First separate fixed header/collapse regions from scrollable content in layout; z-index is only a finishing detail.