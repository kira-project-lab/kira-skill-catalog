# Session sidebar launchers

Use this pattern when replacing the top controls in the Hermes Web UI session sidebar.

## Goal

Turn the old header/filter strip into two equal launchers on a single row:

- **Search** on the left
- **New Chat** on the right

## Layout rules

- Use a 2-column grid (or an equivalent equal-width layout) so both buttons take exactly half of the available strip width.
- Keep the launcher strip full-width.
- Remove any inner left/right padding from the launcher strip itself if it makes the buttons appear inset.
- Keep a small gap between the two buttons so they do not visually merge.
- Use concise labels; prefer `Search` over `Search Sessions` when the button already sits in a session sidebar.

## Verification

- Run a production build after the UI change.
- Check the live DOM or browser screenshot to confirm the buttons are equal-width and not clipped by container padding.
- Make sure the old header/filter row is fully gone, but the session list and its actions still work.
