# v1.0.2 — Room cleaning actually works

**Read the breaking changes before upgrading.** This release fixes the bug that made room cleaning silently do the wrong thing for this project's entire history, and correcting it changes room names, fan-speed tiers, and how `vacuum.start` behaves.

35 commits since v1.0.1, drawn from four contributor forks. 225 tests passing, and the whole integration verified running on a live Home Assistant instance.

---

## ⚠️ Breaking changes

### 1. Room names change ([#48](https://github.com/sjmotew/NarwalIntegration/pull/48))

The room-type lookup table was misaligned from index 5 **for every model**, so unnamed rooms displayed the wrong type — a bathroom could show as "Study". Names now come verbatim from the Narwal app's own strings.

**What to check:** any automation, script, or dashboard that refers to a room by its generated name. Rooms you named yourself in the Narwal app are unaffected — only type-derived names moved. If you use `vacuum.clean_area` with HA segment mappings, re-check those mappings after upgrading.

Closes [#22](https://github.com/sjmotew/NarwalIntegration/issues/22).

### 2. Fan speed values and tiers change ([#49](https://github.com/sjmotew/NarwalIntegration/pull/49))

The suction scale was **off by one tier for this project's entire history**. The enum had four values starting at 0; the robot's actual `SweepMode` has five starting at 1.

The `fan_speed` list is now the app's own labels: **Quiet, Standard, Strong, Super powerful, Ultra powerful**.

Your existing `quiet` / `normal` / `strong` / `max` values still work as aliases, so automations will not error — **but they now map to the correct tier, so actual suction may differ from what you were getting.** If you tuned a value by ear, re-check it.

> **Open question:** the AX26 app UI shows only four tiers where the proto defines five. `Super powerful` may need model-gating. Captures welcome on [#70](https://github.com/sjmotew/NarwalIntegration/issues/70).

### 3. `vacuum.start` now requires the dock ([#69](https://github.com/sjmotew/NarwalIntegration/issues/69))

Whole-house start previously sent a payload to `clean/plan/start` and returned as soon as the robot answered anything other than `NOT_APPLICABLE`. On newer firmware the robot answers `SUCCESS` and does nothing, so **the integration reported a successful start that never happened.**

`vacuum.start` now enumerates every room on the active map and issues `clean/start_clean`, matching the app's own whole-house path.

**Consequence:** `clean/start_clean` only works from the dock. Starting a whole-house clean while the robot is parked off-dock now returns `NOT_READY` instead of appearing to succeed. Send the robot home first. This is a real failure surfacing, not a new restriction — the old path was not starting the clean either.

It also means whole-house start cleans **every room**, rather than re-running whatever plan was last stored on the robot.

---

## Fixed

| Fix | Issue |
|---|---|
| **Room cleaning sends the rooms you selected.** `clean/plan/start` is a plan-runner that discards payloads and re-runs the plan stored on the robot, while still returning success — which is why every earlier fix appeared to work and changed nothing. `clean/start_clean` is the correct command. | [#37](https://github.com/sjmotew/NarwalIntegration/issues/37), [#25](https://github.com/sjmotew/NarwalIntegration/issues/25), [#55](https://github.com/sjmotew/NarwalIntegration/issues/55) |
| `vacuum.start` no longer silently no-ops on newer firmware | [#69](https://github.com/sjmotew/NarwalIntegration/issues/69) |
| Vacuum state no longer freezes at `docked` while the robot is cleaning — live `working_status` telemetry now overrides a stale `robot_base_status` | [#73](https://github.com/sjmotew/NarwalIntegration/issues/73) — **needs field confirmation, see below** |
| Wrong room-type labels on all models | [#22](https://github.com/sjmotew/NarwalIntegration/issues/22) |
| Cleaning-area sensor read a station timer instead of covered area | [#51](https://github.com/sjmotew/NarwalIntegration/pull/51) |
| Unknown status values flooded the log; now warn once per distinct value | [#46](https://github.com/sjmotew/NarwalIntegration/issues/46) |
| `asyncio.get_event_loop` deprecation on Python 3.12 | [#71](https://github.com/sjmotew/NarwalIntegration/pull/71) |
| Config-flow translations out of sync | [#47](https://github.com/sjmotew/NarwalIntegration/pull/47) |

## Added

**Clean settings are now HA entities** ([#50](https://github.com/sjmotew/NarwalIntegration/pull/50)) — room and whole-house cleans no longer hardcode max suction / wet mop / single pass:

- `select` — work mode, water level, mop strength
- `number` — passes (1–3)

**New sensors and diagnostics:**

- `sensor.current_room` — the room being cleaned right now ([#24](https://github.com/sjmotew/NarwalIntegration/pull/24))
- `sensor.last_clean_result` — why the last task ended, as an enum ([#53](https://github.com/sjmotew/NarwalIntegration/pull/53))
- `binary_sensor.maintenance_required` / `binary_sensor.replacement_required` — consumable alerts with per-item attribute lists ([#54](https://github.com/sjmotew/NarwalIntegration/pull/54))
- Station and consumable diagnostics from a full `base_status` field audit ([#52](https://github.com/sjmotew/NarwalIntegration/pull/52))

**Map and dock:**

- Map display options as switches — room labels, furniture, furniture labels ([#62](https://github.com/sjmotew/NarwalIntegration/pull/62))
- Carpet-map camera image; `working_status 7` mapped to remapping ([#67](https://github.com/sjmotew/NarwalIntegration/pull/67))
- `light.dock_light` — base station ambient light, on models that have one ([#61](https://github.com/sjmotew/NarwalIntegration/pull/61))

**Models:** Freo Z10 Pro / Turbo (AX26) added to the selector ([#40](https://github.com/sjmotew/NarwalIntegration/issues/40), [#70](https://github.com/sjmotew/NarwalIntegration/issues/70)); Narwal JX product key added, still unconfirmed ([#42](https://github.com/sjmotew/NarwalIntegration/issues/42)).

**Docs:** [`docs/PROTOCOL.md`](PROTOCOL.md) — the local WebSocket protocol reference, including a Corrections section recording the assumptions this project got wrong and how they were caught ([#4](https://github.com/sjmotew/NarwalIntegration/issues/4), [#5](https://github.com/sjmotew/NarwalIntegration/issues/5)).

---

## Entity count

You will see substantially more entities after upgrading. New platforms: `select`, `number`, `switch`, `light`.

Verified on a Flow (AX12, v01.08.03.07): **28 entities**, up from 9 on v1.0.1 — 1 vacuum, 9 sensors, 9 binary sensors, 2 cameras, 3 selects, 1 number, 3 switches. Models with a dock light get a 29th (`light.dock_light`); it is created only for product keys known to have one, so the Flow correctly does not get it.

---

## Needs confirmation

**The frozen-state fix ([#73](https://github.com/sjmotew/NarwalIntegration/issues/73)) is unvalidated on affected hardware and the issue stays open.**

The bug does not reproduce on the development unit — a 150-second listen on a Flow (AX12, v01.08.03.07) showed `robot_base_status` arriving every ~1.5 s while docked, so the entity never freezes there. The fix is correct against the described root cause, but nobody has yet confirmed it on a robot that exhibits the freeze.

If your vacuum entity used to stick at `docked` mid-clean, please report on [#73](https://github.com/sjmotew/NarwalIntegration/issues/73) whether v1.0.2 fixes it.

One related value is also unconfirmed: `working_status = 3` is treated as active cleaning on newer Flow 2 firmware, on a report without a supporting capture. It is marked `UNCONFIRMED` in the source.

---

## Thanks

This release is largely other people's work. [@jgus](https://github.com/jgus) (#47, #48, #50, #51, #52, #53, #54), [@Sean-StarLabs](https://github.com/Sean-StarLabs) (#61, #62, #63), [@wawtor](https://github.com/wawtor) (#67, #71, #72), [@clawtom](https://github.com/clawtom) (#24), and [@sytchi](https://github.com/sytchi) — three of whom independently found the `clean/start_clean` root cause before it was accepted.

Hardware confirmation of the room-clean fix came from [@Zebble](https://github.com/Zebble) (Flow AX12, v01.08.03.07) and [@shin906710](https://github.com/shin906710) (Freo Z10 Pro AX26, v01.02.00.15), and [@northwestsupra](https://github.com/northwestsupra) contributed the topic table in `PROTOCOL.md`.
