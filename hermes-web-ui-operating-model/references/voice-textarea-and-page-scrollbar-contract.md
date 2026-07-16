# Voice textarea and page scrollbar contract

Use this note when changing the Kira Voice Speak surface or any textarea/scrollable control in Hermes Web UI.

## What changed in the session

- The Speak composer's main text field is `textarea#text.textarea-control.textarea-control--primary`.
- The green styled resizer/scrollbar must be applied to the **actual textarea**, not only to an outer wrapper.
- The page-level custom scrollbar overlay (`#page-scrollbar-y`, `#page-scrollbar-x`) should start hidden in markup and only become visible after runtime overflow detection.

## CSS contract

For the primary textarea, style both the base control and browser-specific pseudo-elements:

- `.textarea-control--primary`
- `.textarea-control--primary::-webkit-resizer`
- `.textarea-control--primary::-webkit-scrollbar`
- `.textarea-control--primary::-webkit-scrollbar-track`
- `.textarea-control--primary::-webkit-scrollbar-thumb`
- `.textarea-control--primary::-webkit-scrollbar-corner`
- `scrollbar-width` / `scrollbar-color` for Firefox

Keep the visual language flat and sharp-cornered; use the accent green for the thumb and a dark track.

## Page scrollbar contract

If the custom page scrollbar remains in the product:

- mark it `is-hidden` by default in HTML,
- update it on initial boot,
- refresh it on `resize`, `scroll`, and DOM/content changes,
- show it only when overflow is actually present,
- prefer `display: none` for the hidden state if the overlay should never be clickable or visible by accident.

## Verification

Check both the DOM and computed styles:

- textarea selector/class names are present,
- computed `scrollbar-width` / `scrollbar-color` match the accent palette,
- `::-webkit-resizer` is styled,
- page scrollbar overlay is hidden before the first layout pass,
- page scrollbar visibility matches real overflow.
