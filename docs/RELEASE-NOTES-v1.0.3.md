# v1.0.3 — The vacuum entity stops freezing at `docked`

A single-fix release on top of [v1.0.2](RELEASE-NOTES-v1.0.2.md). **If you are on v1.0.2, upgrade** — this is the fix v1.0.2 claimed to ship and did not.

No breaking changes. Everything in the [v1.0.2 notes](RELEASE-NOTES-v1.0.2.md) still applies, including its three breaking changes if you are coming from v1.0.1 or earlier.

---

## What was wrong

The vacuum entity would sit at `docked` while the robot was demonstrably cleaning, the live map would stop moving, and `cleaning_area` / `cleaning_time` would stay `unknown`. Reloading the integration fixed it — for about ten minutes.

**Root cause: the broadcast subscription expired and was never renewed.**

The robot only broadcasts `status/working_status` and `display_map` while an `active_robot_publish` subscription is live. That subscription lasts **600 seconds**. The integration sent it once at setup and never again. Once it lapsed the robot went quiet on both topics — while continuing to flood `status/robot_base_status` — so the entity kept deriving its state from `base_status` alone and reported `docked` indefinitely.

Measured on a Flow (AX12, firmware v01.08.03.07) during a real room clean:

| Broadcasts in a comparable window | `base_status` | `working_status` | `display_map` |
|---|---|---|---|
| Subscription expired | 423 | **1** | **1** |
| Immediately after re-subscribing | 211 | **30** | **30** |
| After this fix, renewing | 411 | **148** | **148** |

With the subscription restored the entity went to `cleaning`, room `Pantry`, area `2.58 m²`, elapsed `312 s` within seconds.

**It was also a deadlock.** The only renewal path was the `display_map` dropout recovery, which is gated on `is_cleaning` — and `is_cleaning` cannot become true without `working_status`. The one mechanism that could have recovered the subscription required the subscription.

## The fix

The poll loop now renews the subscription every 240 s, well inside the 600 s TTL, **unconditionally** — not gated on whether the integration believes the robot is cleaning. That gating was the deadlock.

Five regression tests cover it, including one asserting renewal still happens while the entity believes the robot is docked.

## Correction to the v1.0.2 notes

v1.0.2 said the frozen-state fix "does not reproduce on the development unit" and shipped it unvalidated. **That was wrong.** The probe behind that claim only watched the robot while it was docked; the bug only appears *during* a clean. It reproduces reliably, and it reproduced on the development unit the first time anyone ran a room clean against it.

The [#63](https://github.com/sjmotew/NarwalIntegration/pull/63) work in v1.0.2 is not wrong, but it was not sufficient: it reads fresh `working_status` telemetry to override a stale `docked` from `base_status`, and on this firmware there was no `working_status` telemetry arriving to read. The two changes are complementary — v1.0.3 keeps the telemetry flowing, v1.0.2 interprets it.

`working_status = 3` remains `UNCONFIRMED` in the source; it arrived with #63 without a supporting capture.

---

## Also worth knowing: room cleaning needs an area mapping

Not a code change, but it trips up every first-time user of room cleaning and is not yet documented.

`vacuum.clean_area` in Home Assistant 2026.3+ targets **HA areas**, not robot rooms. Before it will do anything you must map the robot's segments to HA areas, and until you do the service fails with:

> `Area mapping is not configured for vacuum.<entity>. Configure the segment-to-area mapping before using this action`

Configure it from the vacuum entity's settings in Home Assistant. You need an HA area for each room you intend to clean.

---

## Upgrading

HACS will offer v1.0.3. No configuration changes, no entity changes, no breaking changes from v1.0.2.

Closes [#73](https://github.com/sjmotew/NarwalIntegration/issues/73).
