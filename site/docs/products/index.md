# Product guides

One guide per served Sense360 product. Each guide covers what the product
does, the Home Assistant entities it exposes (derived automatically from the
firmware source), installation via the flasher, updating, and recovery.

## Choose your product

- **[Room sensing (RoomIQ)](ceiling-poe-roomiq.md)**
  <span class="s360-badge s360-badge--stable">stable</span>
  — presence, temperature, humidity, and light sensing for living spaces
  and bedrooms.
- **[Air quality + room sensing (AirIQ + RoomIQ)](ceiling-poe-airiq-roomiq.md)**
  <span class="s360-badge s360-badge--stable">stable</span>
  — adds the AirIQ air-quality module, for kitchens and living areas.
- **[Bathroom (VentIQ + RoomIQ)](ceiling-poe-ventiq-roomiq.md)**
  <span class="s360-badge s360-badge--stable">stable</span>
  — bathroom air-quality sensing with shower detection, mould-risk
  warnings, and ventilation advice.
- **[Bathroom + LED ring (VentIQ + RoomIQ + LED)](ceiling-poe-ventiq-roomiq-led.md)**
  <span class="s360-badge s360-badge--preview">preview</span>
  — the bathroom product plus a 12-LED indicator ring. Preview firmware
  for testers.

Not sure which one you have? Every Sense360 device reports a **WebFlash
Config** text entity in Home Assistant (for example
`Ceiling-POE-VentIQ-RoomIQ`) that names its exact configuration.

See also the [product comparison](compare.md).
