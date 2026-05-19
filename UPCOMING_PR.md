# Upcoming PRs — esphome-public

This document is the working queue source of truth for `sense360store/esphome-public`
PR work. It tracks upcoming, blocked, deferred, and completed PRs that are
owned by this repository. WebFlash-owned import/runtime work is tracked in
the WebFlash repository's `UPCOMING_PR.md`; only cross-repo dependencies are
mirrored here.

## Maintenance rule

- Update this file in every PR that changes queue state.
- When a PR merges, record the PR number and status in the
  **Completed / merged PRs** table.
- When a PR is deferred, record the blocker (which evidence, which upstream
  PR, or which gating audit must land first).
- When new evidence arrives (schematic PDF, bench result, compliance
  sign-off, etc.), update the relevant evidence item in
  **Recently uploaded evidence** and, if it unblocks a queued PR, update the
  queue row.
- Keep WebFlash-owned import/runtime rows (the `WF-IMPORT-*` series and other
  WebFlash-runtime work) **out of this repo**. Mirror them only under
  **Cross-repo dependencies** so cross-repo coupling stays visible without
  duplicating ownership.

## Current queue summary

- Relay artifact and pinmap work advanced through **HW-ASSETS-310**,
  **HW-PINMAP-310-FOLLOWUP**, and **PACKAGE-RELAY-001**. The S360-310
  schematic is now committed and the Relay pin/package audit is
  schematic-backed partial.
- **PACKAGE-RELAY-001** was a docs-only deferral. `packages/expansions/fan_relay.yaml`
  did not change in that PR.
- The next Relay implementation blocker is **CORE-ABSTRACT-BUS-001**
  (shared Core package variable reconciliation — `relay_pin`, I2C/UART bus
  abstractions, status LED, PIR, expansion GPIO). Relay package
  implementation cannot safely proceed until that lands.
- **S360-400** and **S360-410** schematic evidence is now uploaded in the
  current task context and should move toward **HW-ASSETS-400** /
  **HW-ASSETS-410** artifact ingest PRs.
- **PWM** and **DAC** evidence re-checks (HW-PINMAP-311-FOLLOWUP /
  HW-PINMAP-312-FOLLOWUP) remain insufficient — both audits are still
  partial.
- The **TRIAC** chain remains blocked by **HW-005**, **COMPLIANCE-001**, and
  the **PACKAGE-TRIAC-001** docs-only deferral.
- The **LED stable** chain remains blocked by **S360-300-BENCH-001** (bench
  verification) and the WebFlash-owned operator-proof follow-ups.

## Completed / merged PRs

Only PR numbers verified against the local `git log` are listed here. Do not
add rows without verifying the PR number.

| PR key                       | PR number | Repo            | Status                                 | What merged                                                                          | What did not change                                       | Follow-up impact                                                                  |
|------------------------------|-----------|-----------------|----------------------------------------|--------------------------------------------------------------------------------------|-----------------------------------------------------------|-----------------------------------------------------------------------------------|
| PRODUCT-TRIAC-002            | #501      | esphome-public  | Merged — docs-only deferral             | Recorded deferral of FanTRIAC product implementation until PACKAGE-TRIAC-001 lands   | Product YAML, WebFlash wrapper, build matrix              | Product implementation blocked on PACKAGE-TRIAC-001                                |
| PACKAGE-TRIAC-001            | #502      | esphome-public  | Merged — docs-only deferral             | Recorded deferral until HW-005 / HW-PINMAP-320-FOLLOWUP / COMPLIANCE-001 land        | `packages/expansions/fan_triac.yaml`                       | FanTRIAC package implementation remains blocked on HW + compliance evidence       |
| TRIAC-QUEUE-001              | #503      | esphome-public  | Merged — queue normalization (docs)     | Normalized remaining FanTRIAC follow-up chain after the package deferral             | No functional or catalog files                            | Downstream FanTRIAC queue rows now reflect the deferred package state             |
| S360-100-BENCH-001           | #504      | esphome-public  | Merged — docs-only evidence-pass        | Re-checked Core board bench / manufacturing evidence; status remains pending          | No functional, catalog, or evidence-asset files            | Core bench gate still pending; downstream stable promotions remain blocked        |
| HW-005 / HW-PINMAP-320-FOLLOWUP | #505   | esphome-public  | Merged — docs-only evidence-pass        | Re-checked S360-320 FanTRIAC pin/package evidence; audit remains partial             | `packages/expansions/fan_triac.yaml`, product/WebFlash      | FanTRIAC chain still blocked on HW-005 + COMPLIANCE-001                            |
| COMPLIANCE-001               | #506      | esphome-public  | Merged — docs-only evidence-pass        | Re-checked S360-320 mains-voltage advanced/manual-warning sign-off; remains open     | Compliance status (still not cleared)                      | FanTRIAC product / package release remains blocked on compliance sign-off          |
| HW-PINMAP-311-FOLLOWUP       | #507      | esphome-public  | Merged — docs-only evidence-pass        | Re-checked S360-311 PWM pin/package evidence; audit remains partial                  | `packages/expansions/fan_pwm.yaml`, PWM product/WebFlash    | PWM package/product chain still blocked on additional evidence                     |
| HW-PINMAP-312-FOLLOWUP       | #508      | esphome-public  | Merged — docs-only evidence-pass        | Re-checked S360-312 DAC pin/package evidence; audit remains partial                  | `packages/expansions/fan_gp8403.yaml`, DAC product/WebFlash | DAC package/product chain still blocked on additional evidence                     |
| HW-ASSETS-310                | #509      | esphome-public  | Merged — artifact ingest                | Added S360-310-R4 schematic PDF and curated artifact index                            | No package, product, WebFlash, or release files            | Unblocked HW-PINMAP-310-FOLLOWUP schematic-backed reconciliation                   |
| HW-PINMAP-310-FOLLOWUP       | #510      | esphome-public  | Merged — schematic-backed partial       | Consumed S360-310-R4 schematic; promoted Relay pin/package audit to partial          | `packages/expansions/fan_relay.yaml`, product/WebFlash      | Relay package work surfaced shared-variable mismatches → CORE-ABSTRACT-BUS-001     |
| PACKAGE-RELAY-001            | #511      | esphome-public  | Merged — docs-only deferral             | Recorded deferral until CORE-ABSTRACT-BUS-001 / silkscreen / harness / K1 BOM land   | `packages/expansions/fan_relay.yaml`                        | Relay package implementation now gated by CORE-ABSTRACT-BUS-001                    |

## Active / upcoming esphome-public queue

Listed in working priority order. WebFlash-owned import PRs are kept out of
this table; see **Cross-repo dependencies**. The only `WF-`-prefixed entry
that appears below is **WF-TRIAC-001**, which is the in-repo
wrapper/catalog/build slice (not a WebFlash-runtime import).

1. **CORE-ABSTRACT-BUS-001 — Reconcile Core abstract pin/bus variables**
   - Status: Next / systemic blocker
   - Purpose: Resolve shared Core package variable mismatches such as
     `relay_pin`, I2C bus abstractions, UART bus, status LED, PIR, and
     expansion GPIO variables without destabilizing Release-One.
   - Notes: Needed before Relay package implementation can safely proceed.
     Also affects PWM / DAC / Core abstraction questions surfaced by the
     310-FOLLOWUP and 311 / 312 audits.

2. **HW-ASSETS-400 — Add curated S360-400 power board artifacts**
   - Status: Next / evidence available
   - Purpose: Ingest the uploaded S360-400-R4 schematic PDF and create a
     curated artifact index alongside the existing S360-310 / S360-311 /
     S360-312 / S360-320 entries.
   - Notes: The S360-400 schematic appears to show AC/DC regulation to 5V
     using HLK-10M05, input Live / Neutral / Earth, fuse / MOV / filter,
     and +5VP / GND output. Do not claim compliance or product readiness
     in this artifact PR.

3. **HW-PINMAP-400-FOLLOWUP — Complete S360-400 power board mapping**
   - Status: Planned / after HW-ASSETS-400
   - Purpose: Promote `docs/hardware/s360-400-r4-power.md` from
     "pending evidence" to schematic-backed (partial or complete) using the
     newly ingested S360-400-R4 artifacts.
   - Notes: Cannot start until HW-ASSETS-400 lands the schematic PDF and
     artifact index.

4. **HW-ASSETS-410 — Add curated S360-410 PoE PSU artifacts**
   - Status: Next / evidence available
   - Purpose: Ingest the uploaded S360-410-R4 schematic PDF and create a
     curated artifact index.
   - Notes: The S360-410 schematic appears to show a PoE supply with LAN
     connector, TPS2378, TX4138, isolated F0505S-2WR2, and +5VP / GND Core
     output. Do not requalify Release-One implicitly.

5. **HW-PINMAP-410-FOLLOWUP — Complete S360-410 PoE PSU mapping**
   - Status: Planned / after HW-ASSETS-410
   - Purpose: Promote `docs/hardware/s360-410-r4-poe.md` from
     "pending evidence" to schematic-backed using the newly ingested
     S360-410-R4 artifacts.
   - Notes: Cannot start until HW-ASSETS-410 lands the schematic PDF and
     artifact index.

6. **PACKAGE-POWER-400-001**
   - Status: Planned / after HW-PINMAP-400-FOLLOWUP
   - Purpose: Stand up the S360-400 power board package wiring once the
     pin/package audit is schematic-backed.
   - Notes: Must not destabilize Release-One; coordinate with
     CORE-ABSTRACT-BUS-001 for any shared Core variables.

7. **PRODUCT-POWER-400-001**
   - Status: Planned / after PACKAGE-POWER-400-001
   - Purpose: Add the S360-400 product YAML against the new package.
   - Notes: No WebFlash exposure until WEBFLASH-POWER-400-001.

8. **WEBFLASH-POWER-400-001**
   - Status: Planned / after PRODUCT-POWER-400-001
   - Purpose: Add the WebFlash wrapper, compatibility entry, and build
     matrix row for the S360-400 product.
   - Notes: Pairs with WebFlash-side WF-IMPORT-POWER-400-001 — see
     cross-repo dependencies.

9. **RELEASE-POWER-400-001**
   - Status: Planned / after WEBFLASH-POWER-400-001
   - Purpose: Produce the release artifact + release-proof entries for the
     S360-400 product.
   - Notes: Subject to existing release-artifact readiness gates.

10. **PACKAGE-POE-410-001**
    - Status: Planned / after HW-PINMAP-410-FOLLOWUP
    - Purpose: Stand up the S360-410 PoE PSU package wiring once the
      pin/package audit is schematic-backed.
    - Notes: Must not implicitly requalify Release-One.

11. **PRODUCT-POE-410-001**
    - Status: Planned / after PACKAGE-POE-410-001
    - Purpose: Add the S360-410 product YAML against the new package.
    - Notes: No WebFlash exposure until WEBFLASH-POE-410-001.

12. **WEBFLASH-POE-410-001**
    - Status: Planned / after PRODUCT-POE-410-001
    - Purpose: Add the WebFlash wrapper, compatibility entry, and build
      matrix row for the S360-410 product.
    - Notes: Pairs with WebFlash-side WF-IMPORT-POE-410-001.

13. **RELEASE-POE-410-001**
    - Status: Planned / after WEBFLASH-POE-410-001
    - Purpose: Produce the release artifact + release-proof entries for the
      S360-410 product.
    - Notes: Subject to existing release-artifact readiness gates.

14. **PRODUCT-RELAY-001**
    - Status: Blocked on CORE-ABSTRACT-BUS-001 + PACKAGE-RELAY-001
      implementation
    - Purpose: Add the S360-310 Relay product YAML once the Relay package is
      implemented (not the current docs-only deferral state).
    - Notes: Implementation deferred per PR #511.

15. **WEBFLASH-RELAY-001**
    - Status: Blocked on PRODUCT-RELAY-001
    - Purpose: Add the WebFlash wrapper, compatibility entry, and build
      matrix row for the Relay product.
    - Notes: Pairs with WebFlash-side WF-IMPORT-RELAY-001.

16. **RELEASE-RELAY-001**
    - Status: Blocked on WEBFLASH-RELAY-001
    - Purpose: Produce the release artifact + release-proof entries for the
      Relay product.

17. **PACKAGE-PWM-001**
    - Status: Blocked on HW-PINMAP-311-FOLLOWUP returning sufficient evidence
    - Purpose: Stand up / re-stand up the S360-311 PWM package wiring once
      the pin/package audit is no longer partial.
    - Notes: Also affected by CORE-ABSTRACT-BUS-001 for shared Core
      variables.

18. **PRODUCT-PWM-001**
    - Status: Blocked on PACKAGE-PWM-001
    - Purpose: Add / re-align the S360-311 PWM product YAML.

19. **WEBFLASH-PWM-001**
    - Status: Blocked on PRODUCT-PWM-001
    - Purpose: WebFlash wrapper, compatibility entry, build matrix row.
    - Notes: Pairs with WebFlash-side WF-IMPORT-PWM-001.

20. **RELEASE-PWM-001**
    - Status: Blocked on WEBFLASH-PWM-001
    - Purpose: Release artifact + release-proof entries for the PWM product.

21. **PACKAGE-DAC-001**
    - Status: Blocked on HW-PINMAP-312-FOLLOWUP returning sufficient evidence
    - Purpose: Stand up / re-stand up the S360-312 DAC (GP8403) package
      wiring once the pin/package audit is no longer partial.
    - Notes: Also affected by CORE-ABSTRACT-BUS-001 for shared Core
      variables.

22. **PRODUCT-DAC-001**
    - Status: Blocked on PACKAGE-DAC-001
    - Purpose: Add / re-align the S360-312 DAC product YAML.

23. **WEBFLASH-DAC-001**
    - Status: Blocked on PRODUCT-DAC-001
    - Purpose: WebFlash wrapper, compatibility entry, build matrix row.
    - Notes: Pairs with WebFlash-side WF-IMPORT-DAC-001.

24. **RELEASE-DAC-001**
    - Status: Blocked on WEBFLASH-DAC-001
    - Purpose: Release artifact + release-proof entries for the DAC product.

25. **S360-300-BENCH-001**
    - Status: Pending bench evidence
    - Purpose: LED ring bench / verification gate for S360-300.
    - Notes: Blocks the LED stable chain together with the WebFlash-owned
      operator-proof follow-ups.

26. **RELEASE-007**
    - Status: Planned / promotion of LED stable
    - Purpose: Promote the LED package + product from preview to stable
      once S360-300-BENCH-001 and the WebFlash operator-proof follow-ups
      land.
    - Notes: Subject to preview-to-stable promotion gates.

27. **HW-005 / HW-PINMAP-320-FOLLOWUP**
    - Status: Open / evidence-pass re-checked (PR #505); audit remains
      partial
    - Purpose: Resolve the S360-320 FanTRIAC pin/package collisions and
      provide the schematic/interrupt-capable GPIO evidence needed to
      progress the FanTRIAC chain.
    - Notes: Gating PACKAGE-TRIAC-001 implementation.

28. **COMPLIANCE-001**
    - Status: Open / not cleared (PR #506 re-checked, no sign-off yet)
    - Purpose: Land the S360-320 mains-voltage advanced / manual-warning
      compliance sign-off.
    - Notes: Gating PRODUCT-TRIAC-002 / FanTRIAC release exposure.

29. **PACKAGE-TRIAC-001**
    - Status: Deferred (PR #502 docs-only); blocked on HW-005 /
      HW-PINMAP-320-FOLLOWUP / COMPLIANCE-001
    - Purpose: Implement the FanTRIAC package once the gating HW +
      compliance evidence lands.
    - Notes: `packages/expansions/fan_triac.yaml` retained as-is in the
      meantime.

30. **PRODUCT-TRIAC-002**
    - Status: Deferred (PR #501 docs-only); blocked on PACKAGE-TRIAC-001
    - Purpose: Implement the FanTRIAC product YAML once PACKAGE-TRIAC-001
      lands.

31. **WF-TRIAC-001 — In-repo wrapper/catalog/build slice**
    - Status: Blocked on PRODUCT-TRIAC-002
    - Purpose: Add the in-repo WebFlash wrapper, compatibility entry, and
      build matrix row for the FanTRIAC product. (This is the
      esphome-public-owned slice — the WebFlash-runtime import is tracked
      separately under cross-repo dependencies as WF-IMPORT-TRIAC-001.)
    - Notes: Listed here, not under cross-repo dependencies, because it
      touches `products/webflash/`, `config/`, and the build matrix in this
      repo.

32. **RELEASE-TRIAC-001**
    - Status: Blocked on WF-TRIAC-001 and COMPLIANCE-001
    - Purpose: Release artifact + release-proof entries for the FanTRIAC
      product, contingent on compliance sign-off.

33. **PRODUCT-DEP-002**
    - Status: Planned / housekeeping
    - Purpose: Continue dependency / toolchain alignment work (pre-commit
      tooling, ESPHome pin, Python tooling) without changing functional
      behavior.
    - Notes: Must not destabilize Release-One.

34. **CI-TOOLCHAIN-001**
    - Status: Planned / housekeeping
    - Purpose: CI toolchain alignment follow-ups (workflow images, action
      versions, ESPHome version pinning consistency).
    - Notes: Workflow files are otherwise frozen; this PR scopes only to
      toolchain alignment.

## Cross-repo dependencies

These items are owned by the WebFlash repository and tracked there in its
own `UPCOMING_PR.md`. They are listed here only to keep cross-repo coupling
visible. Do not implement them from this repo.

- **WF-IMPORT-RELAY-001** — WebFlash-side import of the Relay product
- **WF-IMPORT-PWM-001** — WebFlash-side import of the PWM product
- **WF-IMPORT-DAC-001** — WebFlash-side import of the DAC product
- **WF-IMPORT-POWER-400-001** — WebFlash-side import of the S360-400 power
  product
- **WF-IMPORT-POE-410-001** — WebFlash-side import of the S360-410 PoE
  product
- **WF-HW-TEST-002** — WebFlash-side hardware test follow-up
- **WF-LED-STABLE-001** — WebFlash-side LED preview→stable promotion
  follow-up
- **WF-REQUIRED-001** — WebFlash-side REQUIRED_CONFIGS reconciliation
- **WF-KIT-LED-001** — WebFlash-side LED kit follow-up
- **WF-IMPORT-TRIAC-001** — WebFlash-side import of the FanTRIAC product
- **WF-PRODUCT-005** — WebFlash-side product follow-up

## Recently uploaded evidence

- **S360-400-R4.pdf** — uploaded in current task context; candidate for
  **HW-ASSETS-400** ingest.
- **S360-410-R4.pdf** — uploaded in current task context; candidate for
  **HW-ASSETS-410** ingest.

**Note:** These PDFs are not committed in this tracker PR. This PR only
records that the evidence is available. Ingest happens in the dedicated
HW-ASSETS-400 / HW-ASSETS-410 PRs.

## Do-not-change guardrails

This tracking PR must not alter any of the following:

- Functional source files
- Catalogs (hardware, product, WebFlash compatibility, build matrix)
- Packages (`packages/**`)
- Product definitions (`products/**`, excluding `products/webflash/**`
  wrappers below)
- WebFlash wrappers (`products/webflash/**`)
- Build matrices (`config/webflash-builds.json`, related config)
- Release artifacts (firmware binaries, release notes, release-proof files)
- Imports (anything WebFlash-owned)
- Firmware files (`firmware/**`)
- Manifests (`manifest.json`, `firmware/sources.json`)
- Tests (`tests/**`)
- Workflows (`.github/workflows/**`)
- Generated outputs (anything produced by `scripts/**` or test generators)
- Components (`components/**`) and includes (`include/**`)
- `docs/cleanup-audit.md` and any other existing documentation file

The only change introduced by this PR is the creation of this
`UPCOMING_PR.md` file at the repository root.
