# Mobile web app icons / iOS home-screen shortcut

Use when the mobile browser “Add to Home Screen” icon falls back to a generated letter tile.

## Contract

For iOS/Safari home-screen shortcuts, the document head must expose an Apple touch icon:

```html
<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png" />
```

For broader mobile/PWA install metadata, also expose:

```html
<link rel="manifest" href="/site.webmanifest" />
<meta name="apple-mobile-web-app-title" content="Hermes Studio" />
<meta name="application-name" content="Hermes Studio" />
<meta name="theme-color" content="#141414" />
```

Ship static public assets:

- `packages/client/public/apple-touch-icon.png` — 180×180 PNG;
- `packages/client/public/icons/icon-192.png` — 192×192 PNG;
- `packages/client/public/icons/icon-512.png` — 512×512 PNG;
- `packages/client/public/site.webmanifest` with `name`, `short_name`, `display: standalone`, `start_url`, `scope`, `theme_color`, `background_color`, and matching icon entries.

## Icon generation notes

- Reuse the existing product logo when available (`packages/client/public/logo.png` worked as source).
- Crop to a square before resizing.
- Prefer opaque PNGs for iOS home-screen icons; iOS applies its own mask/rounding.
- Do not rely on favicon alone: iOS home-screen shortcuts prefer `apple-touch-icon`.

## Test and verification pattern

Add a small source/asset contract test that checks:

- `packages/client/index.html` contains the Apple icon, manifest, app-title, application-name, and theme-color tags;
- static icon files exist;
- `site.webmanifest` has the expected app metadata and icons.

After build/deploy, verify public dev serves:

- `/` containing the head tags;
- `/site.webmanifest` with the expected icon sizes;
- `/apple-touch-icon.png`, `/icons/icon-192.png`, `/icons/icon-512.png` as `200 image/png`.
