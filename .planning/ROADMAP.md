# Roadmap: Narwal Flow Home Assistant Integration

## Milestones

- ✅ **v0.5 Map Validation & Polish** — Phases 0-8 (shipped 2026-03-08)
- 📋 **Phase 9: Room-Specific Cleaning** — HA 2026.3 clean_area support
- 📋 **Phase 10: Obstacle Mapping** — Furniture/object detection on map
- 🗃️ **Phase 11: Vision Obstacles** — ARCHIVED (raw AI stream unusable for map overlay)
- 📋 **Phase 12: Camera & Patrol** — Snapshot capture, patrol/cruise, LED control, live feed RE
- 📋 **Phase 13: Community Fixes & Multi-Model** — Critical bug fixes, X10 Pro support, room clean investigation
- 🗃️ **Phase 14: Shortcuts & Presets** — ARCHIVED (cloud-only, not accessible via local WS API)
- 📋 **Phase 15: Room-Clean Rewrite & Fork Consolidation** — wrong-topic root cause, five-fork merge, v1.0.2

## Phases

<details>
<summary>✅ v0.5 Map Validation & Polish (Phases 0-8) — SHIPPED 2026-03-08</summary>

- Phase 0: Protocol reverse engineering
- Phase 1: narwal_client standalone library
- Phase 2: Push-mode coordinator + 60s polling fallback
- Phase 3: HA integration (config flow, vacuum entity, sensors)
- Phase 4-5: Map image entity (static floor plan + live overlay)
- Phase 6: HACS installable via custom repo URL
- Phase 7: Map validation & command hardening (room labels, coordinate transform, state mapping)
- Phase 8: Polish and HACS Default (connection resilience, config flow tests, coordinator tests)

</details>

### 📋 Phase 9: Room-Specific Cleaning

**Goal**: Users can select specific rooms to clean from the HA dashboard using the HA 2026.3 vacuum.clean_area service
**Depends on**: Phase 7 (complete — room IDs decoded)
**Success Criteria**:
  1. User can select one or more rooms from the HA UI and start cleaning only those rooms
  2. Room names in HA match the room labels on the map
  3. Robot cleans only the selected rooms and returns to dock
**Requirements:** [ROOM-01, ROOM-02, ROOM-03]
**Plans:** 2 plans

Plans:
- [x] 09-01-PLAN.md — Implement Segment API + start_rooms() + sync copies
- [x] 09-02-PLAN.md — Tests + physical robot validation

**Research**: See ha-vacuum-segments.md in memory for HA 2026.3 API research

### 📋 Phase 10: Obstacle Mapping

**Goal**: Display furniture and obstacle positions as colored rectangles with type labels on the floor map, parsed from local get_map field 2.32 data
**Depends on**: Phase 7 (complete)
**Success Criteria**:
  1. Detected obstacles render on the map at their physical locations
  2. Obstacle types are labeled (furniture, cable, shoe, etc.)
**Requirements:** [OBS-01, OBS-02]
**Plans:** 1 plan

Plans:
- [x] 10-01-PLAN.md — ObstacleInfo model + map rendering + tests + sync

**Research**: See 10-RESEARCH.md — obstacle data is LOCAL in field 2.32 (not cloud-only as previously assumed)

### 🗃️ Phase 11: Vision Obstacles — ARCHIVED

**Goal**: Display transient camera-detected obstacles on the map during cleaning
**Outcome**: ARCHIVED — Feature built, tested live, and removed. display_map field 9/12 provides raw AI detection candidates (every object the camera tentatively identifies), not confirmed objects. The confirmed/filtered set shown in the Narwal app is not accessible via the local WebSocket API.
**Plans:** 2 plans (executed, then reverted)

Plans:
- [x] 11-01-PLAN.md — Probe script + live data capture during cleaning
- [x] 11-02-PLAN.md — VisionObstacleInfo model, parsing, overlay rendering, tests, sync
- Removal commit: 21bbdea

**Key findings**:
- Field 9: raw AI detection stream (3-6x more detections than app shows)
- Detection positions drift with robot (trail endpoints, not fixed positions)
- `get_vision_image` returns NOT_APPLICABLE during cleaning
- Feature recoverable from git history if confirmed data source found later

### 📋 Phase 12: Camera & Patrol

**Goal**: On-demand camera snapshot capture and LED fill light control via local WebSocket API, providing building blocks for "motion detected -> robot goes to room -> takes photos" automation
**Depends on**: Phase 0 (protocol knowledge), Phase 9 (room navigation)
**Success Criteria**:
  1. Take a photo via `/developer/take_picture` and retrieve the image
  2. Control camera LED via `/developer/led_control` for low-light scenarios
  3. Button entity + custom service for snapshot trigger (single + burst mode)
  4. Snapshot camera entity displays latest capture; images saved to HA media directory
**Requirements:** [CAM-01, CAM-02, CAM-03]
**Plans:** 2 plans

Plans:
- [ ] 12-01-PLAN.md — Client commands + button/switch/snapshot camera entities + service + tests
- [ ] 12-02-PLAN.md — Live probe of LED control + snapshot format analysis + physical verification

**Known local topics (from APK)**:
- `/developer/take_picture` — snapshot capture
- `/developer/led_control` — camera fill light
- `/developer/get_robot_debug_image` — debug image retrieval
- `/video_cruise_record` — patrol mission management
- `/video_cruise_edit` — edit patrol waypoints (has `cruisePointRoomId`)
- `/cruise_image_preview` — preview patrol captured images
- `/cruise_album` — patrol photo album
- `/timing_cruise_list` — scheduled patrol tasks
- `/status/video_cruise_task_status` — patrol task status

**Note**: Live video streaming uses Agora P2P via cloud auth (Alibaba IoT REST APIs). PIN auth is cloud-side for live stream only — snapshot and patrol features appear to be separate local commands.

**Update (2026-04-01)**: @northwestsupra shared full APK decompilation (v2.6.81) including .proto files — critical for AES snapshot decryption research in plan 12-02.

### 📋 Phase 13: Community Fixes & Multi-Model

**Goal**: Fix critical bugs reported by community, add X10 Pro model support, investigate room cleaning issues
**Depends on**: Phase 9 (room cleaning), Phase 12 (current)
**Success Criteria**:
  1. Z10 Ultra `last_seen_segments` crash fixed — listener no longer crashes (#11)
  2. Freo X10 Pro recognized in config flow with correct naming (#12)
  3. Room clean CONFLICT (code=3) root cause identified and documented (#10)
  4. Product key annotations updated (AX15 = X10 Pro confirmed)
  5. README compatibility table updated with X10 Pro
**Requirements:** [FIX-01, FIX-02, FIX-03]
**Plans:** 1 plan

Plans:
- [x] 13-01-PLAN.md — X10 Pro model support (FIX-02), room clean error logging (FIX-03); FIX-01 pre-committed

Issues:
- #11 — `last_seen_segments` AttributeError crashes listener (HIGH — breaks Z10 Ultra) -- FIXED (ba53ddb)
- #12 — X10 Pro product key confirmed (CNbforyZWI = AX15), needs config flow + naming
- #10 — Room clean returns CONFLICT or ignores room selection (needs investigation)

### 🗃️ Phase 14: Shortcuts & Presets — ARCHIVED

**Goal**: Discover and expose Narwal app "Shutcut" presets via HA select entity + execute service, enabling automation of robot-stored cleaning configurations
**Outcome**: ARCHIVED — Shortcuts are cloud-managed (Alibaba Alink IoT REST APIs), not exposed via local WebSocket API on port 9002. Probed 8 topic candidates; all shortcut-specific topics timed out, general config/feature topics contain no shortcut data. The feature exists in the Narwal app but definitions and execution are routed through cloud infrastructure.
**Plans:** 2 plans (01 partially executed, 02 not started)

Plans:
- [x] 14-01-PLAN.md — Probe robot for shortcut WS topics (discovery) — **cloud-only confirmed**
- [ ] 14-02-PLAN.md — ShortcutInfo model + SelectEntity — NOT EXECUTED (no local data source)

**Key findings**:
- `shortcut/get`, `clean/shortcut/get`, `robot/shortcut/get` all timeout (topics don't exist)
- `config/get` and `common/get_feature_list` return no shortcut fields
- `clean/cur_plan/get` returns current cleaning plan (per-room MapCleanParamInfo) — room-specific cleaning via Phase 9 already covers this use case
- APK `NrRobotShortcutListGetRequester` confirms cloud REST path
- Shortcuts feature exists in app (user-created presets) but is cloud-only

Issues:
- #13 — Feature request from @ShifuSonny (Flow user) — findings posted

### 📋 Phase 15: Room-Clean Rewrite and Fork Consolidation

**Goal**: Fix room cleaning at the root — it had been sent to the wrong WebSocket topic since Phase 9 — and consolidate the five contributor forks that independently found the bug, ending with a v1.0.2 release.
**Depends on:** Phase 13
**Backfilled:** 2026-08-07. This phase ran as GitHub maintainer work from 2026-07-27 onward and was reconstructed into the roadmap after the fact.
**Plans:** 0 formal plans — executed as issue/PR work, tracked in issue #66

**Root cause (the whole phase turns on this):** `clean/plan/start` is `StartWithPlan{planId, mapId}`. It runs the plan stored in the Narwal app and **discards any payload sent with it**, while returning `SUCCESS`. Every room-clean fix from Phase 9 through 2026-07 corrected the payload schema on a topic that never read it. `clean/start_clean` (`StartClean` → `CleanTask`) is the correct command. Found independently by @jgus (#49), @Sean-StarLabs (#58) and @sytchi (#37) before the maintainer accepted it.

Work completed:
- [x] Triage of 19 open issues and 19 open PRs; merge plan published as #66
- [x] `docs/PROTOCOL.md` published (`35509cd`) — frame format, topic namespace, CleanTask schema, and a public Corrections section
- [x] #47 (`276120d`) config-flow translation sync
- [x] #48 (`17ba151`) room-type names from the app's own strings — closes #22; reverted once, relanded after @jgus supplied a blutter object-pool dump
- [x] #51 (`5a4c2d8`) cleaning area from `coveredArea`
- [x] #52 (`68b5e0d`) `base_status` field audit + station diagnostics
- [x] #71 (`ecc36bb`) asyncio deprecation on Python 3.12
- [x] #72 (`a3edc57`) warn once per unmapped `working_status` — closes #46
- [x] #67 (`029f847`) carpet-map camera + `working_status 7` → REMAPPING
- [x] `64c6edd` AX26 (Freo Z10 Pro / Turbo) in the model selector — #40, #70
- [x] `f0ec580` Narwal JX product key `CGjuB6dzq7` — #42
- [x] **#49 (`05af870`) room clean via `clean/start_clean` — closes #37, #25**
- [ ] v1.0.2 release — README rewrite, manifest bump, breaking-change notes
- [ ] Remaining merge queue: #50, #53, #54, #61, #62, #63, #24, #35

**Success criteria**:
1. Room cleaning cleans the rooms selected in Home Assistant — ✅ confirmed on hardware
2. Confirmed on more than one model and firmware line — ✅ AX26 v01.02.00.15 (@shin906710) and AX12 v01.08.03.07 (@Zebble)
3. Contributor forks consolidated rather than left to diverge — 8 of 9 planned merge steps done
4. The wrong-topic failure documented publicly so it can't be re-derived — ✅ `docs/PROTOCOL.md` §Corrections
5. Shipped to users — ⏳ pending v1.0.2

**Reversals recorded**:
- `clean/plan/start` is **not** the room-clean topic (held from Phase 9 to 2026-07)
- `ROOM_TYPE_NAMES` was misaligned from index 5 for **every** model; naming takes no model argument, so the per-model override added for #22 was entrenching the bug
- `ZoneOption` field 4 is **not** required on any known firmware — a contributor report held the merge ~10 days before two hardware runs disproved it
- `FanLevel` was off by one tier for the project's entire history (`QUIET=0..MAX=3` → the proto's `MUTE=1..SUPER=5`)

Issues: #37 (closed), #22 (closed), #46 (closed), #25, #55, #66, #69, #70, #73

## Progress

**Execution Order:** Phase 9 → Phase 10 → Phase 11 → Phase 12 → Phase 13 → Phase 14 → Phase 15

| Phase | Status | Completed |
|-------|--------|-----------|
| 0-8 (v0.5) | Complete | 2026-03-08 |
| 9. Room-Specific Cleaning | Complete | 2026-03-08 |
| 10. Obstacle Mapping | Complete | 2026-03-09 |
| 11. Vision Obstacles | ARCHIVED | 2026-03-15 |
| 12. Camera & Patrol | In Progress (plan 01 done) | - |
| 13. Community Fixes & Multi-Model | Complete | 2026-04-01 |
| 14. Shortcuts & Presets | ARCHIVED | 2026-04-01 |
| 15. Room-Clean Rewrite & Fork Consolidation | In Progress (#49 merged, v1.0.2 pending) | - |
