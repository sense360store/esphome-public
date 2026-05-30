# Sense360 Room Bundles

The Sense360 room bundles are the primary product line for PoE room sensing. Each base room bundle ships as a complete, stable configuration.

## Fan-control variants (planning only)

The following fan-control variants are **planning-only** proposals. They are optional add-ons for the **Bathroom** and **Kitchen** room bundles only. They are not promoted to firmware, are not built as release artifacts, and are not exposed in WebFlash.

| Variant SKU | Base Bundle | Fan Driver | Control Type | Lifecycle |
|---|---|---|---|---|
| `S360-KIT-BATH-P-REL` | `S360-KIT-BATH-P` | `S360-310` | relay | planning |
| `S360-KIT-BATH-P-DAC` | `S360-KIT-BATH-P` | `S360-312` | 0-10V | planning |
| `S360-KIT-BATH-P-PWM` | `S360-KIT-BATH-P` | `S360-311` | pwm | planning |
| `S360-KIT-KITCHEN-P-DAC` | `S360-KIT-KITCHEN-P` | `S360-312` | 0-10V | planning |
| `S360-KIT-KITCHEN-P-REL` | `S360-KIT-KITCHEN-P` | `S360-310` | relay | planning |

Base room bundles remain the main product line. The fan-control variants above are optional add-ons for Bathroom and Kitchen only. Relay, DAC (0-10V), and PWM control are **not interchangeable at runtime** — each variant targets a specific fan driver board. Firmware config strings and bundle SKUs remain separate identifiers. No firmware release or WebFlash promotion is implied by this planning document. The Kitchen variants are framed as extract / MVHR / EC boost control, not generic cooker-hood control.
