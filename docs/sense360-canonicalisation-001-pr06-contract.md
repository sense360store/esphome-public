# SENSE360-CANONICALISATION-001 PR 06 — canonical firmware-configuration contract

Programme: `SENSE360-CANONICALISATION-001` (authority: `sense360store/SOT`).
Stacked on PR 05 (`sense360store/esphome-public` #853, head `c0f1dade`),
which is itself recorded against main `301a2ffc`.

Evidence level of everything below: **static inspection of declarations and
the YAML include graph, plus test execution**. No hardware, bench,
compliance, safety or commercial-availability claim is made or implied, no
board `schematic_status` is upgraded, and nothing is built, published,
tagged or promoted.

## 1. What the contract is

The charter's identity chain says a firmware configuration is identified by
its **config string**, and that "one config string maps to exactly one board
composition". Before this PR nothing in the tree computed that mapping.
Composition lived in ESPHome `packages:` includes; the catalogues described
the same hardware again in prose (`hardware_requirements`) and again as
capability tokens (`s360_capabilities`). Three descriptions, no check that
any two agreed.

PR 06 makes the mapping derived and enforced:

| File | Role |
|---|---|
| [`config/board-package-bindings.json`](../config/board-package-bindings.json) | The one declaration of **which package is which board**. Exhaustive over `packages/boards/`, `packages/hardware/` and `packages/expansions/`. |
| [`scripts/generate_config_string_contract.py`](../scripts/generate_config_string_contract.py) | Walks each configuration's include graph and resolves its exact board composition and its lane. `--check` mode for freshness. |
| [`config/config-string-contract.json`](../config/config-string-contract.json) | The generated contract. |
| [`tests/test_config_string_contract.py`](../tests/test_config_string_contract.py) | 38 guards. Wired into `validate.yml`, the per-push/PR gate. |

Two properties matter more than the file count.

**The composition is derived, never written down.** The generator follows
`!include` edges, so a legacy alias contributes the SKU of whatever it
resolves to. PR 07 deletes aliases; every resolved composition must come out
byte-identical, and the freshness gate is what will prove it.

**The binding is exhaustive, not a lookup table with holes.** Every YAML in
the three hardware-layer directories appears exactly once — 57 packages, 28
bound to a board SKU, 29 explicitly bound to none with a recorded reason. A
new package cannot enter the tree unclassified, and no entry may name a file
that does not exist.

## 2. The contract

20 live configurations, 20 distinct compositions, 25 tombstones.

| Config string | Lane | Channel | Board composition |
|---|---|---|---|
| `Ceiling-POE-RoomIQ` | room | stable | S360-100 + S360-200 + S360-410 |
| `Ceiling-POE-VentIQ-RoomIQ` | room | stable | S360-100 + S360-200 + S360-211 + S360-410 |
| `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` | advanced | experimental | S360-100 + S360-200 + S360-211 + S360-320 + S360-410 |
| `Ceiling-POE-AirIQ-FanDAC-RoomIQ` | preview | preview | S360-100 + S360-200 + S360-210 + S360-312 + S360-410 |
| `Ceiling-POE-AirIQ-FanPWM-RoomIQ` | preview | preview | S360-100 + S360-200 + S360-210 + S360-311 + S360-410 |
| `Ceiling-POE-AirIQ-RoomIQ` | preview | preview | S360-100 + S360-200 + S360-210 + S360-410 |
| `Ceiling-POE-FanDAC` | preview | preview | S360-100 + S360-312 + S360-410 |
| `Ceiling-POE-FanPWM` | preview | preview | S360-100 + S360-311 + S360-410 |
| `Ceiling-POE-RoomIQ-LED` | preview | preview | S360-100 + S360-200 + S360-300 + S360-410 |
| `Ceiling-POE-VentIQ-FanDAC-RoomIQ` | preview | preview | S360-100 + S360-200 + S360-211 + S360-312 + S360-410 |
| `Ceiling-POE-VentIQ-FanPWM-RoomIQ` | preview | preview | S360-100 + S360-200 + S360-211 + S360-311 + S360-410 |
| `Ceiling-POE-VentIQ-RoomIQ-LED` | preview | preview | S360-100 + S360-200 + S360-211 + S360-300 + S360-410 |
| `Ceiling-POE-AirIQ-FanRelay-RoomIQ` | experimental | experimental | S360-100 + S360-200 + S360-210 + S360-310 + S360-410 |
| `Ceiling-POE-VentIQ-FanRelay-RoomIQ` | experimental | experimental | S360-100 + S360-200 + S360-211 + S360-310 + S360-410 |
| `Ceiling-Core-AirIQ-Blower` | compile-only | — | S360-100 + S360-210 |
| `Ceiling-POE` | compile-only | — | S360-100 + S360-410 |
| `Ceiling-POE-AirIQ` | compile-only | — | S360-100 + S360-210 + S360-410 |
| `Ceiling-POE-VentIQ` | compile-only | — | S360-100 + S360-211 + S360-410 |
| `Ceiling-USB-RoomIQ` | compile-only | — | S360-100 + S360-200 |
| `Ceiling-USB-VentIQ-RoomIQ` | compile-only | — | S360-100 + S360-200 + S360-211 |

The six lanes are derived in a fixed precedence order, so every
configuration lands in exactly one and none lands in none. `advanced` is
tested before the channel lanes, which is why FanTRIAC reports as `advanced`
rather than as an ordinary experimental build: the advanced / manual-warning
lane is the fact that matters about it.

Two derived facts are worth stating plainly because they were not previously
checkable:

- **Every configuration composes S360-100.** Four bundles reached the Core
  through `packages/hardware/sense360_core_ceiling.yaml` rather than the
  board package, which is why a filename-only survey appeared to show
  Core-less configurations. Following includes shows they are not.
- **`Ceiling-USB-RoomIQ` composes no PSU board.** That is correct, not a
  gap: USB-C is a Core input and there is no USB PSU SKU.

## 3. Reconciliation

The contract's value is the disagreements it can now catch. Three
cross-checks are enforced:

- Each `config/webflash-builds.json` `hardware_requirements` entry is
  resolved to a board SKU (explicit SKU first, else the hardware-catalogue
  friendly name) and the resulting set must equal the resolved composition.
  All 14 build rows agree today.
- Each `config/core-framework.json` capability set is mapped through
  `capability_board_map` and must equal the resolved composition. All 16
  configs agree today.
- `config/feature-entity-matrix.json` is audit-only and stays audit-only,
  but a `canonical_board_package` it names must resolve to that SKU. All 11
  boards agree today.

Recording that they agree is the point: they were never checked before, and
the next composition change is where a silent disagreement would otherwise
appear.

## 4. Deletion — the impossible configuration

`Ceiling-Core-LED-AirIQ` is removed. `Core` is neither a power token nor a
module token in `config/webflash-compatibility.json`, so **no board
composition can make the identifier valid**. Three independent signals
agreed it was not a real configuration:

- absent from the generated `config/firmware-combination-matrix.json`, which
  enumerates the grammar;
- `config/compile-only-targets.json` already carried the same product with
  `config_string` null, so the two catalogues disagreed about whether it had
  an identifier at all;
- the SOT charter classifies the `Core` token `internal-and-removable` with
  `resolved_by_pr: PR-06`.

Status proved before deleting, per the charter's `before_deletion_prove_one_of`:
**internal and removable**. Neither `products/sense360-core-ceiling-led-airiq.yaml`
nor `packages/boards/` exists at the `v1.0.0` release tag (verified against
the tag, not inferred), so no customer path is pinned to it. It was never
WebFlash-shippable — `webflash_build_matrix` false, no `artifact_name`, no
wrapper, no build row — so there is no manifest, `REQUIRED_CONFIGS`, kit or
release exposure to unwind.

Removed together: the product YAML, its `compile-only-targets` row, and a
dead module-level `FIXTURE` constant in `tests/test_led_framework.py` that
named the file but was never used. The catalogue entry becomes a tombstone
in the repository's existing convention. The behaviour the fixture
demonstrated — the LED framework degrading honestly with neither RoomIQ nor
Presence — is pinned by the `core_airiq_led` composition in
`tests/test_led_composition.py`, which needs no catalogued product.

**`Ceiling-Core-AirIQ-Blower` is deliberately NOT removed here.** The
charter assigns the `Blower` token to PR 12 ("remove obsolete blower and fan
wrappers with no valid consumer"). Removing it now would resolve a token the
charter assigned to a later PR. It is classified, recorded as the single
grammar exemption in the guard test, and **the `Core` token therefore
retires from the tree at PR 12, not here**. The exemption list is asserted
to be exactly that one string, so a second impossible configuration cannot
hide beside it.

## 5. Corridor naming — the deferred charter item

The charter's `catalogue_change_rules` records: "The corridor customer-name
disagreement with upstream remains PR 06 work." Resolved here.

SOT holds one record for this hardware (`hallway-landing-poe`, SKU
`S360-KIT-CORRIDOR-P`, name `Sense360 Hallway / Landing Bundle — PoE`), and
the freeze baseline records `S360-KIT-LIVING-P` as deliberately absent
because OD-SOT-006 deleted it. Upstream still declared **both**, with
identical `included_board_skus` and an identical
`likely_firmware_config_target` — the duplicate-composition problem the
programme exists to remove.

Upstream now mirrors SOT: `S360-KIT-LIVING-P` is gone, the surviving record
carries SOT's canonical name, and living room is retained as a
**recommended room**, never as a second product. Every consuming declaration
moved in the same commit — `shop-commercial-source-of-truth`,
`room-bundle-fan-variants`, `release-channel-policy`,
`preview-release-targets`, and the two YAML wrapper comments.

**Nothing commercial moved.** No bundle changed status, visibility or
buyability; the consolidation removes a duplicate candidate record and
leaves every posture where it was. That is asserted by the surrounding tests
in `test_release_preview_unblock_all_bundles.py`, which are unchanged.

The guard was inverted rather than deleted. `test_living_and_corridor_share_board_set`
previously asserted that two bundle SKUs shared a board set — it asserted the
duplicate was legal, which is what let it persist. It is replaced by
`test_identical_hardware_is_never_two_bundle_skus`, which fails if any two
bundles ever declare the same boards and the same firmware target again.

## 6. The two PR 05 inputs, resolved

**`S360-LED-V-C` — the unowned configuration.** Confirmed unowned: no
config string, no catalogue entry, no product and no bundle reaches
`packages/boards/s360-300-led-mic-ceiling.yaml`. It is bound to `S360-300`
(the only LED SKU the catalogue declares) and recorded here.

It is **not deleted in PR 06**, and the reason is a protection, not an
oversight. Its legacy alias `packages/hardware/led_ring_mic_ceiling.yaml`
**is present at the `v1.0.0` tag** (verified against the tag), so it is a
published path, and the charter is explicit that "a lack of repository
references never proves that a stable public path is unused". The board file
is internal and unreleased; the alias pointing at it is published. Resolving
that pair means folding the content into the published path and deleting the
internal file — a zero-alias operation, which is PR 07's named scope. The
status proof is done and carried forward, so PR 07 executes rather than
re-investigates.

**Five catalogued board SKUs with no board package.** Not drift. S360-310,
S360-311, S360-312, S360-320 and S360-400 are exactly the SKUs whose
`schematic_status` is `cataloged_unverified` (S360-320 is
`schematic-backed`), and their firmware lives in authoritative expansion and
hardware packages that the bindings now name explicitly. The configurations
that use them resolve correctly — every fan configuration composes its
driver SKU. Creating board packages for them is a composition change gated
on hardware evidence, and PR 12 owns the fan paths. No fan configuration
ships stable, which is unchanged and re-asserted by
`test_no_fan_configuration_reaches_the_stable_channel`.

## 7. Escalated — one new item, one carried forward

### 7.1 New: two declared artifact names for one config string

Three configurations have **two different declared release-artifact names**:

| Config string | `webflash-builds.json` | `preview-release-targets.json` |
|---|---|---|
| `Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` | `…-v1.0.0-experimental.bin` | `…-v1.0.0-preview.bin` |
| `Ceiling-POE-VentIQ-FanRelay-RoomIQ` | `…-v1.0.0-experimental.bin` | `…-v1.0.0-preview.bin` |
| `Ceiling-POE-AirIQ-FanRelay-RoomIQ` | `…-v1.0.0-experimental.bin` | `…-v1.0.0-preview.bin` |

The artifact filename is the canonical identifier of the release-artifact
layer, so one configuration with two names is an identity conflict. Neither
name is published: `release_state` is `metadata-ready-unpublished` and
`publication_status` is `…-buildable-not-published`. This is also not the
manual lane's naming, which is `{product_stem}-manual-{short_sha}-nonrelease`
and explicitly forbids a release version and channel suffix.

Each catalogue is internally consistent and each is authoritative in its own
stated domain, which is why this is a genuine conflict between authorities
rather than a stale field.

**What I would do, and why I have not done it.** `config/webflash-builds.json`
is the declared sole release-eligibility source of truth (ESP-007) and the
standing gates put FanRelay and FanTRIAC on the experimental channel only,
so `experimental` is authoritative and `preview-release-targets.json` should
follow it — `build_channel`, `expected_artifact_name`, the
`build_channel_mapping` in `release-channel-policy.json`, and the two
validators that enforce the current mapping. That direction tightens rather
than loosens and publishes nothing. I have not done it because it is a
channel-field change on release-lane declarations, and channel changes are
an absolute boundary. The alternative direction — moving `webflash-builds`
to `preview` — is a channel promotion and is not something I would
recommend.

### 7.2 Carried forward: the promotion drift blocks PR 06's exit condition

The 15 pre-existing failures triaged in PR 05 as class (a) are unchanged and
still preserved as evidence. All 15 concern `Ceiling-POE-AirIQ-RoomIQ`,
where the catalogue declares `preview` and the published reality is stable:
GitHub release `v1.0.9` (published 2026-07-06, `draft: false`,
`prerelease: false`) carries `Sense360-Ceiling-POE-AirIQ-RoomIQ-v1.0.9-stable.bin`,
and WebFlash serves it as stable 1.0.9.

PR 06's recorded exit condition is a genuinely green Python suite. **It
cannot be met until the owner decides the promotion**, because both repair
directions are closed to an agent: moving the catalogue to `production` is a
channel promotion (owner-only), and moving the tests to expect `preview`
edits a failing test green and destroys the drift evidence. The dependency is
stated rather than worked around.

## 8. Deliberately out of scope, with reasons

Recorded so a reviewer can see these were decided, not missed.

- **Synthetic config strings in `tests/test_led_composition.py`**
  (`Ceiling-Core-LED`, `Ceiling-Core-RoomIQ-LED` and similar). In-memory
  test compositions, never declared, never built, never served. The contract
  scopes to declared configurations.
- **Example strings in `docs/remote-package-consumption.md` and
  `tests/test_remote_package_consumer.py`** (`Ceiling-Core-LED-AirIQ-Bench`
  and similar). These illustrate a *customer-authored* `s360_config_string`
  on a device the customer composed themselves, which the Sense360
  configuration contract does not govern. Canonicalising them is a
  documentation change and belongs with PR 16.
- **Dangling documentation references** to files that do not exist
  (`s360-200-roomiq-*-wall.yaml`, `sense360_core_voice_ceiling.yaml`,
  `sense360_core_voice_wall.yaml`). Real, recorded, and PR 07 / PR 16 work;
  they are comment text, not composition.
- **`device_sku` substitution** (`S360-CORE-C-POE`, `S360-CORE-C-USB`,
  `S360-CORE-C`). A second, non-canonical identifier for the configuration
  layer, published as a customer-visible "Product SKU" diagnostic. It is a
  real canonicalisation target, but changing it changes a customer-visible
  entity value and it is not named in PR 06's scope. Recorded here as an
  input to PR 07.

## 9. Baseline result

| | |
|---|---|
| Baseline (PR 05 head `c0f1dade`) | 15 failures |
| This branch | 15 failures |
| **Introduced** | **0** |
| Fixed | 0 |
| Suite size | 2465 → 2504 tests (+39) |

Measured by running the full suite on both and diffing sorted failure sets,
per the charter's `interim_baseline` rule. The remaining 15 are the
promotion drift of §7.2, unchanged and unsilenced.

Also green: `yamllint` (only the two pre-existing warnings),
`tests/validate_configs.py` (234 files), `tests/validate_webflash_builds.py`
(14 builds), `scripts/validate_product_catalog_consistency.py` (49 entries),
`scripts/generate_firmware_matrix.py --check`,
`scripts/report_firmware_build_gaps.py --check`,
`scripts/validate_preview_release_targets.py --metadata-only`,
`scripts/validate_compile_targets.py --metadata-only`,
`scripts/validate_preview_fan_triac_build_rows.py`, `black`, `flake8`.

## 10. What this PR does not do

No firmware is built, published, tagged or released. No workflow is
dispatched. No channel, lifecycle status or release posture is promoted. No
bundle becomes visible, buyable or customer-default. Release-One
(`Ceiling-POE-VentIQ-RoomIQ`) remains the production stable customer
baseline, asserted directly by `test_release_one_is_the_stable_room_baseline`.
FanTRIAC stays in the advanced / manual lane and no fan configuration
reaches the stable channel, both asserted directly. OD-SOT-004 (radar
evidence) and OD-SOT-008 (SFA40 fitment) stay open and are decided by
nothing here: the bindings name a connector-attached driver's **host board**
only, and never claim an attachment is supplied.
