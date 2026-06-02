# Preview WebFlash release-note drafts (dry-run)

**Canonical id:** `RELEASE-PREVIEW-RELEASE-NOTES-DRYRUN-001`

This directory holds **dry-run** release-note **drafts** for the three
metadata-ready preview WebFlash build rows added by
`RELEASE-PREVIEW-WEBFLASH-BUILD-ROWS-001` (#698):

| Config string | Draft | Consuming candidate bundle(s) |
|---|---|---|
| `Ceiling-POE-AirIQ-RoomIQ` | [`ceiling-poe-airiq-roomiq.md`](ceiling-poe-airiq-roomiq.md) | `S360-KIT-KITCHEN-P` |
| `Ceiling-POE-RoomIQ` | [`ceiling-poe-roomiq.md`](ceiling-poe-roomiq.md) | `S360-KIT-BEDROOM-P` |
| `Ceiling-POE-RoomIQ-LED` | [`ceiling-poe-roomiq-led.md`](ceiling-poe-roomiq-led.md) | `S360-KIT-LIVING-P`, `S360-KIT-CORRIDOR-P` |

## These are drafts, not releases

Each draft is **validated structurally** against the WebFlash release-body
contract with `scripts/validate-webflash-release-notes.py --channel preview`
(the four required H2 sections: `## Changelog`, `## Known Issues`,
`## Features`, `## Hardware Requirements`), and is locked by
[`tests/test_preview_release_notes_drafts.py`](../../../tests/test_preview_release_notes_drafts.py).

They are **not** attached to any GitHub Release by the dry-run PR. No firmware
binary, GitHub Release, tag, `manifest.json`, or `firmware/sources.json` is
produced; nothing is promoted to stable; the consuming candidate bundles stay
hidden / not buyable. Each draft is explicit that it is **PREVIEW** firmware —
not stable, not recommended, not a customer default, not hardware verified, and
not buyable as a public shop product — backed by **firmware-build proof only**
(hosted compile run `26821900127`), with no hardware, bench, compliance, or
commercial-availability proof claimed, and points normal customers to the
**stable Bathroom PoE release** (`S360-KIT-BATH-P` / `Ceiling-POE-VentIQ-RoomIQ`).

The already-published stable Bathroom release (`Ceiling-POE-VentIQ-RoomIQ`,
tag `v1.0.0`) and the already-published VentIQ LED preview
(`Ceiling-POE-VentIQ-RoomIQ-LED`, tag `v1.0.0-led-preview`) are **not** drafted
here — their published release bodies and proof live in
[`docs/webflash-release-proof.md`](../../webflash-release-proof.md) and are
unchanged.

See [`docs/release-preview-webflash-release-notes-dryrun.md`](../../release-preview-webflash-release-notes-dryrun.md)
for the full dry-run record.
