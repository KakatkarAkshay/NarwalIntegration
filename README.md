# Narwal Robot Vacuum — Home Assistant Integration

A fully **local, cloud-independent** [Home Assistant](https://www.home-assistant.io/) custom integration for Narwal robot vacuums. Communicates directly with your vacuum over your local network via WebSocket — no cloud account or internet connection required.

> **Latest release: v1.0.1** (HACS) · **`master` is 28 commits ahead of it** — room cleaning, `vacuum.start`, and the frozen-state fix all landed there. v1.0.2 is being prepared; see [`docs/RELEASE-NOTES-v1.0.2.md`](docs/RELEASE-NOTES-v1.0.2.md).

> ### ✅ Room cleaning is fixed on `master`
>
> Community reverse-engineering found that **room-specific cleaning had never worked**. The integration sent clean commands to `clean/plan/start`, which is `StartWithPlan{planId, mapId}` — it runs the plan stored in the Narwal app and **discards the rooms we send**, while still returning success. That is why every previous fix appeared to work and changed nothing. `clean/start_clean` is the correct command.
>
> Found independently by [@jgus](https://github.com/sjmotew/NarwalIntegration/pull/49), [@Sean-StarLabs](https://github.com/sjmotew/NarwalIntegration/pull/58) and [@sytchi](https://github.com/sjmotew/NarwalIntegration/issues/37). Merged as [#49](https://github.com/sjmotew/NarwalIntegration/pull/49); [#37](https://github.com/sjmotew/NarwalIntegration/issues/37) is closed.
>
> **Confirmed on hardware, on two independent firmware lines:**
>
> | Reporter | Model | Firmware | Result |
> |---|---|---|---|
> | [@shin906710](https://github.com/sjmotew/NarwalIntegration/issues/70) | Freo Z10 Pro (AX26) | v01.02.00.15 | Two single-room cleans, each cleaned only the selected room |
> | [@Zebble](https://github.com/sjmotew/NarwalIntegration/pull/49) | Flow (AX12) | v01.08.03.07 | Two rooms, correct rooms, correct order, first attempt, ~35 min run |
>
> ### ⚠️ Still broken in the released v1.0.1
>
> If you installed from HACS, you are on v1.0.1 and these still apply:
>
> | Issue | Impact | Fixed by |
> |---|---|---|
> | **Room cleaning ignores your selection** | The robot cleans its last plan or your first Narwal-app shortcut instead of the rooms you picked. On **Flow 2** it can also clear the map stored on the robot ([#55](https://github.com/sjmotew/NarwalIntegration/issues/55)) | [#49](https://github.com/sjmotew/NarwalIntegration/pull/49) — on `master` |
> | **Wrong room type labels** | Unnamed rooms show incorrect types on all models — the lookup table is misaligned from index 5, so a bathroom may display as "Study". Rooms you named in the Narwal app are unaffected | [#48](https://github.com/sjmotew/NarwalIntegration/pull/48) — on `master` |
> | **`vacuum.start` silently no-ops** | On newer firmware, whole-house start reports success and does nothing | [#69](https://github.com/sjmotew/NarwalIntegration/issues/69) — fixed on `master` |
> | **Vacuum state freezes at `docked`** | The entity holds its last state while the robot is demonstrably cleaning; sensors keep updating | [#73](https://github.com/sjmotew/NarwalIntegration/issues/73) — fixed on `master`, awaiting field confirmation |
>
> **Want the fixes now?** Install from the `master` branch instead of the HACS release. Otherwise wait for v1.0.2.
>
> ### 🔜 Coming in v1.0.2 — three breaking changes
>
> Full notes: [`docs/RELEASE-NOTES-v1.0.2.md`](docs/RELEASE-NOTES-v1.0.2.md). Read this before upgrading:
>
> - **Room names will change** ([#48](https://github.com/sjmotew/NarwalIntegration/pull/48)). The room-type table was wrong for every model. If you built automations or scripts on the old (incorrect) names, expect to redo those mappings.
> - **Fan speed values will change** ([#49](https://github.com/sjmotew/NarwalIntegration/pull/49)). The suction scale was off by one tier for this project's entire history. The list becomes the app's own labels — Quiet, Standard, Strong, Super powerful, Ultra powerful. Your existing `quiet` / `normal` / `strong` / `max` automations keep working as aliases, but they now map to the correct tier, so **actual suction may differ from what you were getting**.
> - **`vacuum.start` will require the dock** ([#69](https://github.com/sjmotew/NarwalIntegration/issues/69)). Whole-house start now goes through `clean/start_clean` and cleans every room instead of re-running the robot's saved plan. That command only works from the dock, so starting off-dock now returns `NOT_READY` instead of appearing to succeed — a real failure surfacing, since the old path was not starting the clean either.
>
> You will also see **many more entities** — 28 on a Flow, up from 9 — as clean settings, consumable alerts, map options and the dock light become HA entities. Verified on hardware (AX12, v01.08.03.07).
>
> Release progress is tracked in [#66](https://github.com/sjmotew/NarwalIntegration/issues/66).

## Device Compatibility

This integration uses a **local WebSocket connection on port 9002**. Only models that expose this port are supported.

| Model | Status | Notes |
|-------|--------|-------|
| **Narwal Flow** (AX12) | **Working** | Primary development target. Room cleaning confirmed on firmware v01.08.03.07 with [#49](https://github.com/sjmotew/NarwalIntegration/pull/49). On v01.07.22+, `vacuum.start` needs a loaded map ([#36](https://github.com/sjmotew/NarwalIntegration/issues/36)). |
| **Narwal Flow 2** (QxMSPG6VSO) | **Working** | Room cleaning fixed by [#49](https://github.com/sjmotew/NarwalIntegration/pull/49); on v1.0.1 see the warning above before using `vacuum.clean_area` |
| **Freo Z10 Ultra** (CX4) | **Working** | Community confirmed |
| **Freo Z10 Pro / Turbo** (AX26) | **Working** | Same product key and firmware (v01.02.00.15) reported under both names ([#40](https://github.com/sjmotew/NarwalIntegration/issues/40), [#70](https://github.com/sjmotew/NarwalIntegration/issues/70)). Room cleaning confirmed working with [#49](https://github.com/sjmotew/NarwalIntegration/pull/49). |
| **Freo X10 Pro** (AX15) | **Working** | Community confirmed ([#12](https://github.com/sjmotew/NarwalIntegration/issues/12)) |
| **Narwal JX** | **Unconfirmed** | Product key known, no working report yet — testers welcome ([#42](https://github.com/sjmotew/NarwalIntegration/issues/42)) |
| **Freo Z Ultra** (CX7) | **Not Compatible** | Port 9002 open but no local broadcasts; cloud-only ([#5](https://github.com/sjmotew/NarwalIntegration/issues/5), confirmed by @Folg0re) |
| **Freo X Ultra** (AX18/AX19) | **Not Compatible** | Uses ZeroMQ (port 6789) + Tuya cloud, not WebSocket ([#4](https://github.com/sjmotew/NarwalIntegration/issues/4)) |
| **Freo X Plus** | **Not Compatible** | Cloud-only — no local API |
| **Narwal J-series** (J1/J4/J5) | **Not Compatible** | J1: HTTP-only (port 8080); J4/J5: cloud-only (Tuya) |

Models marked **Not Compatible** use a different protocol or are cloud-only. This is a hardware/firmware limitation.

**Other models?** Check with `nmap -p 9002 <your-vacuum-ip>`. If open, [open an issue](https://github.com/sjmotew/NarwalIntegration/issues/new/choose) with your model and results.

## Features

### Vacuum Control
- **Start / Stop / Pause / Resume** — validated on hardware (see the note above for `start` on newer Flow firmware)
- **Return to dock** / **Locate** (robot announces "Robot is here")
- **Fan speed** — Quiet, Standard, Strong, Super powerful, Ultra powerful (set-only; robot doesn't broadcast current level). On v1.0.1 these are `quiet` / `normal` / `strong` / `max` and are off by one tier — see the breaking-change note above
- **Room-specific cleaning** — exposed in the HA UI (requires HA 2026.3+). **Fixed on `master`** ([#49](https://github.com/sjmotew/NarwalIntegration/pull/49)); broken in v1.0.1

### Clean Settings
On `master` ([#50](https://github.com/sjmotew/NarwalIntegration/pull/50)) — applied to both room and whole-house cleans, which previously hardcoded max suction / wet mop / single pass:
- **Work mode** — vacuum, mop, vacuum then mop, vacuum and mop
- **Water level** — dry, normal, wet
- **Mop strength** — normal, high
- **Passes** — 1 to 3

### Sensors
- Battery level, cleaning time, firmware version
- Docked status (binary sensor), charging state (Charging / Fully Charged / Not Charging)
- Cleaning area — reports real covered area as of v1.0.1 ([#51](https://github.com/sjmotew/NarwalIntegration/pull/51))
- Current room being cleaned ([#24](https://github.com/sjmotew/NarwalIntegration/pull/24), on `master`)
- Last clean result — why the previous task ended ([#53](https://github.com/sjmotew/NarwalIntegration/pull/53), on `master`)
- Dust bag health and detergent remaining ([#52](https://github.com/sjmotew/NarwalIntegration/pull/52), on `master`)
- Station and consumable binary sensors — clean water tank, sewage tank, dust box, dust bag, station bag, error ([#52](https://github.com/sjmotew/NarwalIntegration/pull/52), on `master`)
- Maintenance and replacement alerts, with the affected parts listed as attributes ([#54](https://github.com/sjmotew/NarwalIntegration/pull/54), on `master`)

### Live Map
- Color-coded floor plan with room labels (all rooms — user-named and auto-generated)
- Furniture/obstacle overlay from the robot's stored map data
- Dock marker and live robot trail during cleaning (~1.5s refresh)
- Carpet-map debug image as a second camera ([#67](https://github.com/sjmotew/NarwalIntegration/pull/67), on `master`)
- Display toggles for room labels, furniture and furniture labels ([#62](https://github.com/sjmotew/NarwalIntegration/pull/62), on `master`)

### Dock
- **Ambient light** — off, fireplace, nightlight, purple, on models with a dock light ([#61](https://github.com/sjmotew/NarwalIntegration/pull/61), on `master`)

### Connectivity
- Real-time WebSocket push updates
- Auto-reconnect with exponential backoff
- Wake system for sleeping robots + keepalive heartbeat
- 60-second polling fallback

## Installation

### HACS (Recommended)

1. Open **HACS** > three-dot menu > **Custom repositories**
2. Add: `https://github.com/sjmotew/NarwalIntegration` (category: Integration)
3. Find **Narwal Flow Robot Vacuum** and click **Download**
4. **Restart Home Assistant**

### Manual

1. Copy `custom_components/narwal/` to your HA `config/custom_components/` directory
2. **Restart Home Assistant**

### Setup

1. **Settings > Devices & Services > Add Integration** > search "Narwal"
2. Enter your vacuum's IP address and select your model
3. Entities are created automatically

> **Tip:** Assign a static IP to your vacuum in your router.

## Requirements

- Narwal vacuum on the same local network as Home Assistant
- Port 9002 reachable (no firewall blocking)
- Home Assistant 2025.1.0+ / Python 3.12+

## Known Limitations

- **Wake from deep sleep is unreliable** — robot may not respond after long idle periods. Opening the Narwal app briefly can help.
- **Single connection** — close the Narwal app before using HA to avoid conflicts.
- **Fan speed is set-only** — robot doesn't broadcast its current level.
- **All cleaning requires the dock** — `clean/start_clean` returns `NOT_READY` if the robot is not docked when the command is sent. This applies to whole-house `vacuum.start` as well as room cleans.
- **Vacuum state freeze is fixed but unconfirmed** — the fix for [#73](https://github.com/sjmotew/NarwalIntegration/issues/73) is on `master`, but the bug does not reproduce on the development unit, so it has not been validated on affected hardware. Reports welcome.
- **Map may be stale** — robot can return an old map. A new clean cycle typically refreshes it.

## Future Features (On Hold)

These features have been researched and probed but are **on hold** pending further reverse engineering:

| Feature | Status | Blocker |
|---------|--------|---------|
| **Camera snapshots** | Client method works (robot returns ~170KB) | Image data is **AES-encrypted** — APK reverse engineering needed for decryption key |
| **Camera LED control** | Partial response from robot | Correct payload format unconfirmed; needs idle-state testing |
| **Vision obstacle overlay** | Built, tested, and removed | Robot broadcasts raw AI candidates (3-6x more than app shows), not confirmed detections. Unusable for map overlay. |
| **Patrol / cruise mode** | Topics identified in APK | Not yet probed; depends on camera working first |

Camera snapshot and LED entities will be added once the AES decryption key is extracted from the Narwal APK.

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "Cannot connect" during setup | Verify IP and that port 9002 is reachable. If it still fails, **open the Narwal app on your phone the moment you press Submit** — a sleeping robot may not answer within the setup timeout ([#40](https://github.com/sjmotew/NarwalIntegration/issues/40)). |
| Room cleaning runs the wrong rooms | Fixed on `master` ([#49](https://github.com/sjmotew/NarwalIntegration/pull/49)). If you are on the v1.0.1 HACS release, this is expected — install from `master` or wait for v1.0.2. |
| Room clean returns `NOT_READY` | `clean/start_clean` only works from the dock. Send the robot home first, then start the room clean. |
| Entities show "Unavailable" | Robot may be asleep. Open Narwal app briefly to wake it. |
| Map not showing | Map loads after robot wakes. A new clean refreshes a stale map. |
| Commands not responding | Close the Narwal app — only one WebSocket connection at a time. |
| Z10 Ultra disconnects | Re-add the integration with the correct model selected. |

## Project Status

**Where things stand — updated 2026-08-08.**

`master` is 28 commits ahead of the v1.0.1 release, with **223 tests passing and CI green**. Everything below is merged; none of it has shipped to HACS yet. **The merge queue is empty apart from [#35](https://github.com/sjmotew/NarwalIntegration/pull/35).**

| Merged since v1.0.1 | What it does |
|---|---|
| [#49](https://github.com/sjmotew/NarwalIntegration/pull/49) | **Room cleaning via `clean/start_clean`** — the headline fix. Closes [#37](https://github.com/sjmotew/NarwalIntegration/issues/37) |
| [#48](https://github.com/sjmotew/NarwalIntegration/pull/48) | Room-type names taken from the app's own strings. Closes [#22](https://github.com/sjmotew/NarwalIntegration/issues/22) |
| [#50](https://github.com/sjmotew/NarwalIntegration/pull/50) | Clean settings as HA entities — work mode, water, mop strength, passes |
| [#63](https://github.com/sjmotew/NarwalIntegration/pull/63) | Live state from `working_status`, so the entity stops freezing at `docked` ([#73](https://github.com/sjmotew/NarwalIntegration/issues/73)) |
| [#62](https://github.com/sjmotew/NarwalIntegration/pull/62) | Map rendering options as switches — room labels, furniture, furniture labels |
| [#61](https://github.com/sjmotew/NarwalIntegration/pull/61) | Dock ambient light entity, on models that have one |
| [#24](https://github.com/sjmotew/NarwalIntegration/pull/24) | `sensor.current_room` — the room being cleaned right now |
| [#53](https://github.com/sjmotew/NarwalIntegration/pull/53) / [#54](https://github.com/sjmotew/NarwalIntegration/pull/54) | Last-clean-result sensor; consumable maintenance and replacement alerts |
| [#52](https://github.com/sjmotew/NarwalIntegration/pull/52) | `base_status` field audit; station and consumable diagnostics |
| [#67](https://github.com/sjmotew/NarwalIntegration/pull/67) | Carpet-map camera image; `working_status 7` mapped to remapping |
| [#72](https://github.com/sjmotew/NarwalIntegration/pull/72) | Unknown status values warn once instead of flooding the log. Closes [#46](https://github.com/sjmotew/NarwalIntegration/issues/46) |
| [#71](https://github.com/sjmotew/NarwalIntegration/pull/71) | asyncio deprecation fix for Python 3.12 |
| [#47](https://github.com/sjmotew/NarwalIntegration/pull/47) | Config-flow translation sync |
| [#69](https://github.com/sjmotew/NarwalIntegration/issues/69) | `vacuum.start` routes through `clean/start_clean` instead of silently no-opping |
| — | AX26 in the model selector ([#40](https://github.com/sjmotew/NarwalIntegration/issues/40), [#70](https://github.com/sjmotew/NarwalIntegration/issues/70)); Narwal JX product key ([#42](https://github.com/sjmotew/NarwalIntegration/issues/42)); [`docs/PROTOCOL.md`](docs/PROTOCOL.md) published |

### Next steps

1. **Cut v1.0.2** — see [`docs/RELEASE-NOTES-v1.0.2.md`](docs/RELEASE-NOTES-v1.0.2.md). This is the immediate priority; the room-clean fix has been sitting unreleased and everyone on HACS is running a version where it does not work.
2. **Confirm the [#73](https://github.com/sjmotew/NarwalIntegration/issues/73) fix on affected hardware** — it does not reproduce on the development unit, so it ships unvalidated.
3. **Local discovery** ([#35](https://github.com/sjmotew/NarwalIntegration/pull/35)) — zeroconf and DHCP discovery is the largest outstanding UX win, since [#40](https://github.com/sjmotew/NarwalIntegration/issues/40) shows setup failing outright on the wake timeout. Awaiting a narrowed PR.

### Open protocol questions — help wanted

- **Is there a fifth suction tier?** The proto defines five `FanLevel` values, but the AX26 app UI shows four. A capture of what integer "Super puissant" / "Super powerful" sends would settle it ([#70](https://github.com/sjmotew/NarwalIntegration/issues/70)).
- **What is `CleanParam` tag 8?** The Narwal app sends `8 = 2`; we never send it and cleaning works without it. The best current candidate is the app's two-value coverage-precision toggle ([#25](https://github.com/sjmotew/NarwalIntegration/issues/25)).
- **The complete `WorkingStatus` enum.** Values have been discovered one user bug report at a time. Anyone holding an APK `BuilderInfo` decode can end that ([#46](https://github.com/sjmotew/NarwalIntegration/issues/46)).
- **Narwal JX confirmation.** The product key is known; no working report yet ([#42](https://github.com/sjmotew/NarwalIntegration/issues/42)).

## Reporting Issues

Use the [issue templates](https://github.com/sjmotew/NarwalIntegration/issues/new/choose) — they collect your HA version, model, and debug logs for faster diagnosis.

## Protocol Documentation

[**docs/PROTOCOL.md**](docs/PROTOCOL.md) documents the local WebSocket protocol — frame format, topic reference, message field maps, and the open questions. It also records the assumptions this project got wrong and how they were caught, which is the part most likely to save someone else time.

Corrections and captures are welcome; the doc explains how to take them.

## Disclaimer

This is an **unofficial**, community-developed integration — not affiliated with or endorsed by Narwal. The local protocol was reverse-engineered from network traffic and the Narwal mobile application.

- **Use at your own risk.** No warranty.
- **No cloud dependency.** No external data transmission.
- **Firmware updates** from Narwal may break this integration at any time.

## Contributing

Contributions and testing welcome! If you have a non-Flow Narwal model, testing reports are especially valuable.

## License

MIT
