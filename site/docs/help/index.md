<!--
Knowledge base landing page (SENSE360-CUSTOMER-DOCS-001; FAQ depth
filled in Phase 3). Task-first questions with one-breath answers and a
link to the owning article; keep entries free of repository internals.
The encryption-key answer must stay exactly as honest as the shipped
firmware posture (docs/security/release-firmware-credential-posture.md)
— the security drift gate in tests/test_customer_docs_site.py pins the
wording shape. Zone guidance stays a link to the Zone Studio surface,
never duplicated here.
-->

# Help

Answers organised by what you're trying to do.

## Getting started

- Choose your room from the [home page](../index.md) and follow that
  page top to bottom — box to working device.

## Common questions

**How does the device get online?**
After flashing it opens its own setup hotspot; you join it once and
give it your Wi-Fi. Full steps in [Get it online](get-online.md).

**Will Home Assistant ask for a key or password?**
No. Installer firmware connects without an encryption key, and Home
Assistant shows the connection as unencrypted on your local network.
If you [build your own firmware](../advanced/index.md), your build
carries your own key and Home Assistant asks for it.

**Is there a cloud account or an app?**
No. The device works with your own Home Assistant on your local
network. Flashing and updating happen in an ordinary desktop browser.

**How do I update the firmware?**
Run the installer again — the device keeps its place in Home
Assistant. See [Update or start over](updates-and-recovery.md).

**Something is wrong — how do I reset it?**
Reflash it with the installer; flashing again is always safe and puts
the device back in a known state. See
[Update or start over](updates-and-recovery.md).

**Can I move it to another room?**
Yes — remount it, move it to the new Area in Home Assistant, and
redraw the radar zones. See
[Move it to another room](moving-rooms.md).

**What do the sensor readings mean?**
[What the boards do](sensor-glossary.md) describes every board in
plain language; your room page's "What you'll see" section lists the
exact Home Assistant entities.

**What does the light ring do?**
See [The light ring](light-ring.md) — the room light, status
indications, identify, and night mode, with the full controls table.

**How do I shape where presence is detected?**
With [Zone Studio](../zone-studio.md), the interactive zone editor
that runs as a Home Assistant add-on.

## Still stuck

- [GitHub Discussions](https://github.com/sense360store/esphome-public/discussions)
  — questions and ideas.
- [GitHub Issues](https://github.com/sense360store/esphome-public/issues)
  — something looks broken.
