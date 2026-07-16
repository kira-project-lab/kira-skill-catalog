# Devices / LAN peer surface

Use this when Maxim asks what the **Devices** tab is, whether it belongs in primary navigation, or how the LAN/multi-device flow works.

## Source-of-truth map

- Route: `packages/client/src/router/index.ts` -> `/hermes/devices`
- UI: `packages/client/src/views/hermes/DevicesView.vue`
- Client API: `packages/client/src/api/hermes/devices.ts`
- Server routes: `packages/server/src/routes/devices.ts`
- UDP discovery: `packages/server/src/services/lan-discovery.ts`
- Remote peer tools: `packages/server/src/services/lan-peer-tools.ts`
- Peer socket: `packages/server/src/services/lan-peer-socket.ts`

## What the tab does

Devices is a technical LAN peer-management surface for Hermes instances on the same network:

1. Scans local/private IPv4 networks for Hermes announcements.
2. Shows discovered Hermes Web UI / Hermes Desktop / custom endpoints with IP, port, OS, Hermes Agent version, Web UI version, latency, and online/offline state.
3. Sends outgoing pairing requests, including manual pairing by URL.
4. Handles incoming requests: approve, reject, block, unblock, or delete request history.
5. After pairing, backend services can open peer connections and expose remote tools: command exec, interactive terminal, upload, and download.

## UX judgment

Treat Devices as an operator / remote-control feature, not a normal chat feature.

If the task is UI simplification, do not assume it belongs in the primary sidebar. Consider one of these outcomes:

- hide it from primary navigation while keeping the route available for operators;
- move it under Settings / Advanced / Developer tools;
- rename it to something explicit such as `LAN Devices`, `Peer Devices`, or `Remote Devices`.

Avoid explaining it as generic browser/audio devices. It is about Hermes peer machines and LAN pairing.
