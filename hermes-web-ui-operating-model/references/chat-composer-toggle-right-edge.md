# Chat composer toggle right-edge contract

When the user asks for the `autoplay` and `show/hide tools` buttons to be on the right, keep them in the same composer header/section as the context info, but pin them to the far right edge of that section.

## Correct pattern

- The section that holds tokens/context info and the toggle buttons must be a full-width flex row.
- Put the text/meta block on the left and the toggle group on the far right within the same row.
- Use `width: 100%` on the row container when the parent would otherwise shrink to content width.
- `margin-left: auto` is valid only on the right-side toggle group inside that full-width row.
- Do **not** move these toggles into the lower composer toolbar just because it also contains action buttons.

## Verification

- Browser/layout check: toggles appear at the right edge of the composer section, not merely to the right of tokens.
- Source contract: row container is full-width; toggle group is the last child in the row.
- Avoid regressing into a bottom-row placement when adjusting sibling controls such as attach/send.
