# Room-bundle fan firmware publish — recorded successful run

> **Workflow since merged:** this run was executed by the standalone
> `Room-Bundle Fan Firmware Publish` workflow, which has since been merged into
> [`preview-fan-publish.yml`](../.github/workflows/preview-fan-publish.yml)
> (`fan_set: room-bundle`). This historical run record is unchanged.

**Canonical id:** `ROOM-BUNDLE-FAN-PUBLISH-RESULTS-001`
**Date:** 2026-06-04
**Type:** Records the **successful** `Room-Bundle Fan Firmware Publish` workflow run
that published the five full-composition Bathroom / Kitchen fan-control
room-bundle **preview** firmware artifacts — the run queued as
`ROOM-BUNDLE-FAN-PUBLISH-RUN-001`. This is **documentation / config-evidence
only** — it records an already-completed run. It **does not** re-run the
workflow, create another release or tag, build or commit any `.bin`, write
`manifest.json` / `firmware/sources.json`, touch the WebFlash repo, add any
`config/webflash-builds.json` row, promote anything to stable, make any fan
build recommended / default, expose any fan product as buyable, include TRIAC,
change the launch SKU **`S360-KIT-BATH-P`**, change Simple install, complete the
FanDAC I²C address bench verification (`FANDAC-I2C-ADDR-001`), or claim any
hardware / bench / compliance / safety / commercial-availability proof.

## Status

**Firmware-build / release proof only — recorded, GREEN.**

A green build + publish means the five YAMLs compiled on hosted CI, were renamed
to their contract artifact names, passed the room-bundle output + release-note
gates, and were attached to the shared `v1.0.0-preview` prerelease as durable
`-v1.0.0-preview.bin` files. **It is not hardware, bench, safety, or compliance
evidence**, and it does not make any of the five WebFlash-importable, stable,
recommended, a customer default, or buyable.

**Predecessors:**

- `#713` `ROOM-BUNDLE-FAN-CONFIGS-001` authored the five full-composition
  product YAMLs (Bathroom PWM / DAC, Kitchen Relay / DAC / PWM).
- `#714` `COMPILE-VALIDATOR-PROGRESS-LOGGING-001` added per-target compile
  logging and a per-target timeout.
- `#715` `FANDAC-I2C-ADDR-001` added the FanDAC I²C address verification
  checklist ([`docs/hardware/fandac-i2c-address-verification.md`](hardware/fandac-i2c-address-verification.md)) — **still pending**.
- `ROOM-BUNDLE-FAN-COMPILE-RESULTS-001` recorded the hosted full ESPHome compile
  run [`26913592989`](https://github.com/sense360store/esphome-public/actions/runs/26913592989)
  as GREEN firmware-build proof for the five configs
  ([`docs/room-bundle-fan-compile-results.md`](room-bundle-fan-compile-results.md)).
- `#717` `ROOM-BUNDLE-FAN-PUBLISH-PLAN-001` verified the publish inputs / scope
  and queued the workflow + run
  ([`docs/room-bundle-fan-publish-plan.md`](room-bundle-fan-publish-plan.md)).
- `#718` `ROOM-BUNDLE-FAN-PUBLISH-WORKFLOW-001` added the dispatch-only,
  dry-run-default publication workflow
  [`.github/workflows/room-bundle-fan-publish.yml`](../.github/workflows/room-bundle-fan-publish.yml)
  and its validator
  [`scripts/validate_room_bundle_fan_publish.py`](../scripts/validate_room_bundle_fan_publish.py).
- `ROOM-BUNDLE-FAN-PUBLISH-RUN-001` is the run this document records as **done /
  success**.

---

## TL;DR

* **The room-bundle fan publish run is DONE and GREEN.** The `Room-Bundle Fan
  Firmware Publish` workflow ran on a **`workflow_dispatch` (manual dispatch)**
  with `dry_run=false` —
  [run `26947595936`](https://github.com/sense360store/esphome-public/actions/runs/26947595936)
  (run #2, attempt 1; 2026-06-04) — and finished with **conclusion `success`**.
* **The five room-bundle fan artifacts were built and attached.** The matrix
  resolved to exactly the five compile-validated room-bundle fan configs
  (`Ceiling-POE-VentIQ-FanPWM-RoomIQ`, `Ceiling-POE-VentIQ-FanDAC-RoomIQ`,
  `Ceiling-POE-AirIQ-FanRelay-RoomIQ`, `Ceiling-POE-AirIQ-FanDAC-RoomIQ`,
  `Ceiling-POE-AirIQ-FanPWM-RoomIQ`); each compiled `success`, and the publish
  job attached the five durable `-v1.0.0-preview.bin` files plus
  `checksums-sha256.txt`, `checksums-md5.txt`, and a build-info `manifest.json`.
* **TRIAC was excluded.** `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` is **build-blocked
  by `HW-005`**; no TRIAC build job ran and no TRIAC artifact exists.
* **Shared preview release — `v1.0.0-preview` is the single preview release for
  every preview artifact.** The five room-bundle fan `.bin` were attached to the
  shared `v1.0.0-preview` GitHub Release (see §4), which also carries the
  room-bundle / LED previews and the single-driver fan previews. Under
  `RELEASE-PREVIEW-FAN-SHARED-TAG-001` this is the **intended** model — there is
  no separate room-bundle fan release tag. `softprops/action-gh-release` upserted
  the release, so its name + body + checksum/manifest helper files were
  **refreshed** (a release-metadata refresh, **not a release error**). Every
  pre-existing preview `.bin` remains attached with its **SHA256 intact**, so the
  preview artifacts WebFlash already imported are unaffected, and the shared
  release now intentionally co-hosts the room, LED, single-driver fan, and
  room-bundle fan preview artifacts.
* **Posture is unchanged.** All five artifacts are **preview** — not stable, not
  recommended, not a customer default; the fan room-bundle variants stay **hidden
  / not buyable**; the **stable Bathroom PoE release** (`S360-KIT-BATH-P` /
  `Ceiling-POE-VentIQ-RoomIQ`) remains the only customer-default production
  release and Simple install is unchanged. The two FanDAC artifacts were built
  **with the IC2 `0x5A` override**, but the physical DIP-switch mapping is **not
  bench verified** and `FANDAC-I2C-ADDR-001` stays **pending**. **No** hardware /
  bench / compliance / commercial-availability proof is claimed — this is
  **firmware-build / release proof only**.
* **Records, does not republish.** This PR edits only this doc, its guard test,
  the five variants' `publish_evidence` + the document-level `publish_results` in
  [`config/room-bundle-fan-variants.json`](../config/room-bundle-fan-variants.json),
  and the handoff / gates / queue docs. No firmware is built, no `.bin` is
  committed, no `config/webflash-builds.json` / `manifest.json` /
  `firmware/sources.json` is written, and the WebFlash repo is untouched.

---

## 1. The publish run (evidence)

| Field | Value |
|---|---|
| Workflow name | **`Room-Bundle Fan Firmware Publish`** ([`.github/workflows/room-bundle-fan-publish.yml`](../.github/workflows/room-bundle-fan-publish.yml)) |
| Run id | **`26947595936`** (run #2, attempt 1) |
| Run URL | <https://github.com/sense360store/esphome-public/actions/runs/26947595936> |
| Event | **`workflow_dispatch`** (manual dispatch) — **not** a `release` event |
| Input — `dry_run` | **`false`** (the `dry-run` job was **skipped**, confirming a real publish dispatch) |
| Input — `release_target` | `all-room-bundle-fan-previews` (matrix resolved to the five room-bundle fan configs) |
| Input — `version` | `1.0.0` |
| Input — `release_tag` | **`v1.0.0-preview`** (the shared preview release for all preview artifacts; the workflow default) |
| Branch / ref | `main` |
| Commit (`head_sha`) | `ad1d9575e17a1da450f31964401bb485a6b130c7` (`ad1d957`, merge of #718, `ROOM-BUNDLE-FAN-PUBLISH-WORKFLOW-001`) |
| Triggered by | `sense360store` |
| Started → finished | 2026-06-04T10:59:40Z → 2026-06-04T11:04:24Z (≈4.7m) |
| Build count | **5** room-bundle fan artifacts |
| Conclusion | **`success`** |

### 1.1 Job results

Eight jobs were scheduled; the `dry-run` job was correctly **skipped** because
`dry_run=false`. Every other job finished `success`.

| Job | Result |
|---|---|
| `Room-bundle fan matrix` (guard tag + validate metadata + generate matrix) | ✅ **success** |
| `Build room-bundle fan: Ceiling-POE-VentIQ-FanPWM-RoomIQ` | ✅ **success** |
| `Build room-bundle fan: Ceiling-POE-VentIQ-FanDAC-RoomIQ` | ✅ **success** |
| `Build room-bundle fan: Ceiling-POE-AirIQ-FanRelay-RoomIQ` | ✅ **success** |
| `Build room-bundle fan: Ceiling-POE-AirIQ-FanDAC-RoomIQ` | ✅ **success** |
| `Build room-bundle fan: Ceiling-POE-AirIQ-FanPWM-RoomIQ` | ✅ **success** |
| `Room-bundle fan publish dry-run` | ⏭️ **skipped** (`dry_run=false`) |
| `Attach room-bundle fan release assets` | ✅ **success** |

No TRIAC build job exists in the run — `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` is
build-blocked by `HW-005` and is absent from the room-bundle fan matrix.

---

## 2. The five published room-bundle fan artifacts

Every artifact is `channel: preview`, `version: 1.0.0`, full-composition
(base room modules **plus** the fan driver — never a fan-only substitution), and
is backed by its
[`config/room-bundle-fan-variants.json`](../config/room-bundle-fan-variants.json)
variant. Sizes and SHA256 below are the **recorded GitHub Release asset values**
(the release per-asset digest; matching the uploaded `checksums-sha256.txt`).

| # | Config string | Bundle SKU | Artifact (preview `.bin`) | Size (bytes) | SHA256 |
|---|---|---|---|---|---|
| 1 | `Ceiling-POE-VentIQ-FanPWM-RoomIQ` | `S360-KIT-BATH-P-PWM` | `Sense360-Ceiling-POE-VentIQ-FanPWM-RoomIQ-v1.0.0-preview.bin` | 1,010,192 | `6d988708558881d653ffbc7429ef8779a574878ac0ee26d745bf645be85befba` |
| 2 | `Ceiling-POE-VentIQ-FanDAC-RoomIQ` | `S360-KIT-BATH-P-DAC` | `Sense360-Ceiling-POE-VentIQ-FanDAC-RoomIQ-v1.0.0-preview.bin` | 990,112 | `a08c82f735aa058614afda71dbec2d220d23a0a4fbb4cb46088adb82a41d8ef8` |
| 3 | `Ceiling-POE-AirIQ-FanRelay-RoomIQ` | `S360-KIT-KITCHEN-P-REL` | `Sense360-Ceiling-POE-AirIQ-FanRelay-RoomIQ-v1.0.0-preview.bin` | 1,090,656 | `97e54930f26074e38326fbeaff7a222c828df38a33be509327e77a0b0f24a83f` |
| 4 | `Ceiling-POE-AirIQ-FanDAC-RoomIQ` | `S360-KIT-KITCHEN-P-DAC` | `Sense360-Ceiling-POE-AirIQ-FanDAC-RoomIQ-v1.0.0-preview.bin` | 1,090,400 | `903a37dc2faf3e1f87016c435e6076752b8c776e7a862f8986d5b5a4b19a994b` |
| 5 | `Ceiling-POE-AirIQ-FanPWM-RoomIQ` | `S360-KIT-KITCHEN-P-PWM` | `Sense360-Ceiling-POE-AirIQ-FanPWM-RoomIQ-v1.0.0-preview.bin` | 1,113,872 | `0ca10a2f3e867ae5693e36149276b0176294b2391fa9ef02ba7059d9c853a1cc` |

### 2.1 Workflow (CI) artifacts

The build jobs also uploaded the five intermediate workflow artifacts (7-day
retention, `expires_at: 2026-06-11`) the publish job consumed. (The
`-compile-only` suffix is the build job's upload-artifact naming pattern; this
was a real publish run, and these zip artifacts are not the durable release
assets.)

| Workflow artifact name | Artifact id | Compressed size (bytes) |
|---|---|---|
| `room-bundle-fan-firmware-ceiling-poe-ventiq-fanpwm-roomiq-compile-only` | `7409767629` | 699,690 |
| `room-bundle-fan-firmware-ceiling-poe-ventiq-fandac-roomiq-compile-only` | `7409768691` | 686,910 |
| `room-bundle-fan-firmware-ceiling-poe-airiq-fanrelay-roomiq-compile-only` | `7409768038` | 756,541 |
| `room-bundle-fan-firmware-ceiling-poe-airiq-fandac-roomiq-compile-only` | `7409772798` | 756,442 |
| `room-bundle-fan-firmware-ceiling-poe-airiq-fanpwm-roomiq-compile-only` | `7409770313` | 771,737 |

The durable `-preview.bin` files in §2 are the published deliverables.

---

## 3. Gate + step results (the `Attach room-bundle fan release assets` job)

The publish job is the only job granted `contents: write` and runs only on a
non-dry-run `workflow_dispatch`. Every step finished `success`.

| Step | Result |
|---|---|
| `Download room-bundle fan firmware artifacts` | ✅ success |
| **`Validate room-bundle fan output set`** (exact non-TRIAC `.bin` set) | ✅ **success** |
| `Generate checksums and build-info manifest` (`checksums-sha256.txt`, `checksums-md5.txt`, `manifest.json`) | ✅ success |
| **`Generate and validate release notes`** (`scripts/validate-webflash-release-notes.py … --channel preview`) | ✅ **success** |
| **`Upload room-bundle fan release assets`** (`softprops/action-gh-release`) | ✅ **success** |
| `Publish summary` | ✅ success |

The build-info `manifest.json` attached by this run records `channel: preview`,
`delivery_lane: manual-preview`, `target_count: 5`, `webflash_importable: false`,
the git SHA `ad1d957…`, ESPHome `2026.4.5`, and the per-file SHA256 / size for the
five fan `.bin` — it is **not** the WebFlash production-signed manifest.

---

## 4. Release vehicle — the shared `v1.0.0-preview` preview release

Under `RELEASE-PREVIEW-FAN-SHARED-TAG-001`, `v1.0.0-preview` is the **single,
shared preview release** for every preview firmware artifact — the room-bundle
and LED previews, the single-driver FanRelay / FanPWM / FanDAC manual-preview
artifacts, and now these five room-bundle fan previews. There is **no** dedicated
room-bundle fan release tag; that dedicated-vehicle concept is **retired**. The
run attached the five room-bundle fan `.bin` to that shared release via
`softprops/action-gh-release`, which upserts (creates-or-updates) the release.
Recorded:

| Field | Value |
|---|---|
| Release tag used | **`v1.0.0-preview`** (the shared preview release for all preview artifacts) |
| Release id | `333373906` |
| Release name (now) | `Sense360 room-bundle fan preview firmware 1.0.0` (refreshed by the upsert) |
| Release body (now) | the room-bundle fan release notes (refreshed) |
| Prerelease / draft | `true` / `false` |
| `target_commitish` (now) | `ad1d9575e17a1da450f31964401bb485a6b130c7` |
| Release URL | <https://github.com/sense360store/esphome-public/releases/tag/v1.0.0-preview> |

**Effect of the upsert (a release-metadata refresh, not a release error):**

* The five room-bundle fan `.bin` (created `2026-06-04T11:04:20Z`) were **added**
  as new assets; `checksums-sha256.txt` / `checksums-md5.txt` / `manifest.json`
  were **refreshed** by the upsert, and the release name / body now describe the
  room-bundle fan preview artifacts.
* Every pre-existing preview asset **remains attached** with its **SHA256
  intact** — the four room / LED previews `Ceiling-POE-AirIQ-RoomIQ`
  (`16565de6…`), `Ceiling-POE-RoomIQ` (`2c7d691c…`), `Ceiling-POE-RoomIQ-LED`
  (`d4f18824…`), `Ceiling-POE-VentIQ-RoomIQ-LED` (`9e513b47…`), and the three
  single-driver fan previews `Ceiling-POE-VentIQ-FanRelay-RoomIQ` (`f9600a6b…`),
  `Ceiling-POE-FanPWM` (`4ef9f353…`), `Ceiling-POE-FanDAC` (`151894c1…`). These
  match the SHA256 values WebFlash pinned, so the previews WebFlash already
  imported are **unaffected** by this run.
* The shared release therefore now **intentionally co-hosts** twelve `.bin` —
  four room / LED previews + three single-driver fan previews + five room-bundle
  fan previews — exactly as the shared-tag model intends.

This is a **release-metadata refresh only** — no artifact was deleted, no SHA256
changed, and no WebFlash import broke. Presence of a fan artifact in the shared
release does **not** make it WebFlash-importable: **WebFlash import** eligibility
is **controlled separately** by WebFlash import policy (the fan-token guardrail
keeps fan rows out of `config/webflash-builds.json`), so a fan preview in the
shared release is never implied to be a WebFlash one-click import, a
Simple-install build, or stable / recommended / default / buyable.

---

## 5. FanDAC IC2 `0x5A` address note (`FANDAC-I2C-ADDR-001` stays pending)

The two FanDAC room-bundle artifacts — `Ceiling-POE-VentIQ-FanDAC-RoomIQ`
(Bathroom DAC) and `Ceiling-POE-AirIQ-FanDAC-RoomIQ` (Kitchen DAC) — were built
**with the FanDAC IC2 address override** `fan_dac_2_i2c_address: "0x5A"`. This
relocates the second GP8403 (IC2) off its `0x59` package default so it does not
collide with the air-quality SGP41 at `0x59` on the shared `core_i2c` bus.

| Address | Role |
|---|---|
| GP8403 IC1 | `0x58` (package default) |
| GP8403 IC2 | `0x5A` (relocated off the `0x59` default) |
| GP8403 `0x59` | **Forbidden** with VentIQ / AirIQ (collides with the SGP41 @ `0x59`) |
| SGP41 | `0x59` |

This is a **firmware / compile-time configuration only**. The physical IC2
DIP-switch (SW2) → I²C address mapping is **NOT bench verified**; the
DIP-position → address truth table stays owed by `FANDAC-I2C-ADDR-001`, which
remains **pending**. A successful build / publish proves the firmware composes
with the `0x5A` override applied; **it does not prove the installer's DIP-switch
setting**, and **no FanDAC hardware verification is claimed**.

---

## 6. Posture preserved

| Posture claim | State after this run |
|---|---|
| Channel | all five artifacts are **preview** (never stable) |
| Recommended / default | **not recommended, not a customer default** |
| Fan room-bundle variants (Bathroom PWM/DAC, Kitchen Relay/DAC/PWM) | **hidden / not buyable** — unchanged, `commercial_availability: waitlist-only` |
| Customer-default production release | the **stable Bathroom PoE** kit (`S360-KIT-BATH-P` / `Ceiling-POE-VentIQ-RoomIQ` / `Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin`) remains the **only** one |
| Simple install | **unchanged** — stable Bathroom PoE build only |
| Launch SKU | **`S360-KIT-BATH-P`** — unchanged |
| TRIAC (`S360-320`) | **excluded** — build-blocked by `HW-005`; no build job, no artifact, off the room-bundle fan matrix |
| FanDAC hardware verification | **pending** — `FANDAC-I2C-ADDR-001` not completed; only the compile-time `0x5A` override is recorded |
| WebFlash import | **not done** — no fan row added to `config/webflash-builds.json`; the fan-token guardrail is intact |
| Hardware / bench / compliance / commercial-availability | **none claimed** |

---

## 7. What is proven (and what is not)

* **Proven (firmware-build / release proof only):** the five buildable
  full-composition room-bundle fan product YAMLs
  (`products/sense360-ceiling-poe-ventiq-fanpwm-roomiq.yaml`,
  `products/sense360-ceiling-poe-ventiq-fandac-roomiq.yaml`,
  `products/sense360-ceiling-poe-airiq-fanrelay-roomiq.yaml`,
  `products/sense360-ceiling-poe-airiq-fandac-roomiq.yaml`,
  `products/sense360-ceiling-poe-airiq-fanpwm-roomiq.yaml`) compiled on hosted
  CI, were renamed to their contract artifact names, passed the room-bundle
  output + release-note gates, and were attached to a real GitHub prerelease —
  i.e. durable `-v1.0.0-preview.bin` room-bundle fan artifacts now exist.
* **Not proven / not claimed:** any FanTRIAC compile (build-blocked by `HW-005`),
  hardware operation, bench verification, a verified schematic, the FanDAC
  DIP-switch → address mapping (`FANDAC-I2C-ADDR-001` stays pending), electrical /
  mains-safety / EMC compliance, commercial availability, or any stable-promotion
  readiness. Stable / full release of every fan-control variant stays gated on
  hardware, bench evidence, and compliance sign-off (and, for FanDAC,
  `FANDAC-I2C-ADDR-001`). A published **preview** artifact is **not** a stable
  release and **not** a hardware / compliance claim.

---

## 8. Validation

All commands run from the repo root and pass (this PR records results and adds
`publish_evidence` / `publish_results` to the five room-bundle fan variants only;
it adds no `config/webflash-builds.json` row, no product YAML, and no firmware,
so the existing counts are unchanged):

| Command | Result |
|---|---|
| `python3 tests/validate_configs.py` | `✅ All configuration files are valid!` |
| `python3 scripts/validate_compile_targets.py --metadata-only` | `✅ Metadata validation passed.` |
| `python3 scripts/validate_preview_release_targets.py --metadata-only` | `✅ … validation passed.` |
| `python3 scripts/validate_room_bundle_fan_publish.py --metadata-only` | `Room-bundle fan publish metadata validated (5 target(s)…)` |
| `python3 tests/test_room_bundle_fan_variants.py` | `OK` |
| `python3 tests/test_product_catalog.py` | `OK` |
| `python3 tests/test_room_bundle_fan_publish_results.py` | `OK` (this PR's guard) |
| `python3 -m unittest discover -s tests -p "test_*.py"` | `OK` |

---

## 9. Follow-up

* **WebFlash import — intentionally out of scope.** WebFlash one-click import of
  the room-bundle fan preview artifacts is **not** performed here. It remains a
  separately gated downstream WebFlash-repo follow-up, contingent on a deliberate
  WebFlash policy decision. No fan row is added to `config/webflash-builds.json`;
  the fan-token guardrail stays intact.
* **FanDAC bench verification — still owed.** `FANDAC-I2C-ADDR-001` (the physical
  S360-312 DIP-position → I²C address truth table) stays **pending**; this run
  records only the compile-time `0x5A` override.
* **FanTRIAC `HW-005`** — unchanged buildability defect; FanTRIAC stays
  advanced-manual-preview, build-blocked, excluded from every publish surface.
* **Stable / full release** of every fan-control room-bundle variant stays gated
  on hardware, bench evidence, and compliance sign-off — see
  [`docs/sense360-room-bundles.md`](sense360-room-bundles.md),
  [`docs/pre-hardware-room-bundle-release-handoff.md`](pre-hardware-room-bundle-release-handoff.md),
  and [`docs/first-release-gates.md`](first-release-gates.md).

---

## Guardrails — what this PR did and did NOT do

This PR **records** a successful, already-completed publish run. It did **not**,
and must not be read as having done, any of:

* re-run the publish workflow or create another release / tag / checksum;
* build or commit any `.bin` (none is in this diff);
* write `manifest.json` or `firmware/sources.json`, or add/modify any
  `config/webflash-builds.json` row (the fan-token guardrail stays intact);
* touch the WebFlash repo or change any WebFlash manifest / source metadata;
* flip anything to `stable`; mark any fan build recommended / default; expose any
  fan product as buyable; change the launch SKU away from `S360-KIT-BATH-P`;
  change Simple install or the stable Bathroom PoE build;
* include TRIAC (FanTRIAC stays advanced-manual-preview, blocked by `HW-005`);
* complete `FANDAC-I2C-ADDR-001` (FanDAC bench verification stays **pending**);
* claim hardware, bench, compliance, safety, or commercial-availability proof.

The files changed by the PR carrying this record are this document, the guard
test
[`tests/test_room_bundle_fan_publish_results.py`](../tests/test_room_bundle_fan_publish_results.py),
the five room-bundle fan variants' `publish_evidence` + the document-level
`publish_results` in
[`config/room-bundle-fan-variants.json`](../config/room-bundle-fan-variants.json)
(TRIAC untouched — stays build-blocked with no compile / publish evidence), and
the handoff / gates / queue docs ([`docs/sense360-room-bundles.md`](sense360-room-bundles.md),
[`docs/pre-hardware-room-bundle-release-handoff.md`](pre-hardware-room-bundle-release-handoff.md),
[`docs/first-release-gates.md`](first-release-gates.md), `UPCOMING_PR.md`).

---

## Cross-references

- Publish plan (pre-run record): [`docs/room-bundle-fan-publish-plan.md`](room-bundle-fan-publish-plan.md) (`ROOM-BUNDLE-FAN-PUBLISH-PLAN-001`)
- Publish workflow: [`.github/workflows/room-bundle-fan-publish.yml`](../.github/workflows/room-bundle-fan-publish.yml) · validator [`scripts/validate_room_bundle_fan_publish.py`](../scripts/validate_room_bundle_fan_publish.py) · doc [`docs/room-bundle-fan-publish-workflow.md`](room-bundle-fan-publish-workflow.md)
- Compile proof: [`docs/room-bundle-fan-compile-results.md`](room-bundle-fan-compile-results.md) (`ROOM-BUNDLE-FAN-COMPILE-RESULTS-001`, run `26913592989`)
- Canonical source of truth: [`config/room-bundle-fan-variants.json`](../config/room-bundle-fan-variants.json) (`ROOM-BUNDLE-FAN-VARIANTS-002`)
- FanDAC I²C address verification (pending): [`docs/hardware/fandac-i2c-address-verification.md`](hardware/fandac-i2c-address-verification.md) (`FANDAC-I2C-ADDR-001`)
- Sibling single-driver fan publish results: [`docs/release-preview-fan-publish-results.md`](release-preview-fan-publish-results.md) (`RELEASE-PREVIEW-FAN-PUBLISH-RESULTS-001`)
- WebFlash release-eligibility source of truth: [`config/webflash-builds.json`](../config/webflash-builds.json)
- Commercial source of truth: [`docs/shop-commercial-source-of-truth.md`](shop-commercial-source-of-truth.md)
