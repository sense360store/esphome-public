# Compare products

All four products are PoE-powered ceiling configurations of the Sense360
Core hub — they differ in which sensing modules are fitted and which
firmware channel they ship on.

In one line each:

- **[Room sensing (RoomIQ)](ceiling-poe-roomiq.md)** — presence +
  comfort sensing only; the smallest configuration.
- **[Air quality + room sensing (AirIQ + RoomIQ)](ceiling-poe-airiq-roomiq.md)**
  — RoomIQ plus the AirIQ air-quality module (see that guide for what the
  current firmware exposes).
- **[Bathroom (VentIQ + RoomIQ)](ceiling-poe-ventiq-roomiq.md)** — RoomIQ
  plus bathroom air-quality sensing with shower detection and mould-risk
  warnings.
- **[Bathroom + LED ring (VentIQ + RoomIQ + LED)](ceiling-poe-ventiq-roomiq-led.md)**
  — the bathroom product plus a 12-LED indicator ring (preview channel,
  for testers).

## Comparison matrix

Every cell below is generated from the product catalog and the firmware
source — a capability is ticked only when the product's firmware actually
exposes the matching Home Assistant entity, so this matrix cannot drift
from what the firmware ships.

--8<-- "compare-matrix.md"

Not sure which product you have? Every Sense360 device reports a
**WebFlash Config** text entity in Home Assistant (for example
`Ceiling-POE-VentIQ-RoomIQ`) that names its exact configuration.
