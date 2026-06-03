# Fan-control & TRIAC PREVIEW release-note drafts (dry-run)

**Canonical id:** `RELEASE-PREVIEW-FAN-TRIAC-BUILD-ROWS-001`

This directory holds **dry-run** release-note **drafts** for the four buildable
fan-control and TRIAC preview targets that are delivered on the **non-WebFlash**
preview lanes — the `manual-preview` lane (FanRelay / FanPWM / FanDAC) and the
`advanced-manual-preview` lane (FanTRIAC). They are deliberately kept **separate**
from the WebFlash preview drafts in
[`docs/release-notes/preview/`](../preview/) because these targets are **not**
WebFlash-importable (the fan-token guardrail keeps fan / TRIAC tokens out of
[`config/webflash-builds.json`](../../../config/webflash-builds.json)).

| Config string | Lane | Channel | Draft | Build status |
|---|---|---|---|---|
| `Ceiling-POE-VentIQ-FanRelay-RoomIQ` | `manual-preview` | preview | [`ceiling-poe-ventiq-fanrelay-roomiq.md`](ceiling-poe-ventiq-fanrelay-roomiq.md) | buildable (run `26821900127`) |
| `Ceiling-POE-FanPWM` | `manual-preview` | preview | [`ceiling-poe-fanpwm.md`](ceiling-poe-fanpwm.md) | buildable (run `26821900127`) |
| `Ceiling-POE-FanDAC` | `manual-preview` | preview | [`ceiling-poe-fandac.md`](ceiling-poe-fandac.md) | buildable (run `26821900127`) |
| `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` | `advanced-manual-preview` | advanced-preview | [`ceiling-poe-ventiq-fantriac-roomiq.md`](ceiling-poe-ventiq-fantriac-roomiq.md) | **build-blocked (`HW-005`)** |

## These are drafts, not releases

Each draft is **validated structurally** against the WebFlash release-body
contract with `scripts/validate-webflash-release-notes.py --channel preview`
(the four required H2 sections: `## Changelog`, `## Known Issues`,
`## Features`, `## Hardware Requirements`), and is locked by
[`tests/test_preview_fan_triac_build_rows.py`](../../../tests/test_preview_fan_triac_build_rows.py).

They are **not** attached to any GitHub Release. No firmware binary, GitHub
Release, tag, `manifest.json`, or `firmware/sources.json` is produced; nothing
is promoted to stable; nothing becomes recommended / default / buyable.

* **FanRelay / FanPWM / FanDAC** are **firmware-build proof only** (hosted
  compile run `26821900127`, `proof_class: firmware-build-only`). A green
  compile is **not** hardware proof, bench evidence, compliance, stable
  promotion, or commercial availability.
* **FanTRIAC** is **build-blocked by `HW-005`** — it is **not buildable
  end-to-end**, so **no compile / firmware artifact exists** and **no compile,
  hardware, bench, or compliance proof is claimed**. Its draft carries the
  mandatory **mains-voltage** / AC-load warning and the installer-only,
  advanced-manual posture, and it is never forced into the normal WebFlash
  preview path.

Every draft is explicit that it is **PREVIEW** firmware — not stable, not
recommended, not a customer default, not hardware verified, not compliance
certified, and not buyable as a public shop product — and points normal
customers to the **stable Bathroom PoE release**
(`S360-KIT-BATH-P` / `Ceiling-POE-VentIQ-RoomIQ`).

See [`docs/release-preview-fan-triac-build-rows.md`](../../release-preview-fan-triac-build-rows.md)
for the full build-row readiness record, and
[`config/preview-fan-triac-build-rows.json`](../../../config/preview-fan-triac-build-rows.json)
for the machine-readable build-row ledger.
