#!/usr/bin/env python3
"""
Product Name Mapper for WebFlash Integration

Converts ESPHome product configuration names to WebFlash-compatible firmware
binary names.

Input Format:  sense360-[product]-[variant]
Output Format: Sense360-[Product]-[Variant]-v[Version]-[Channel].bin

Usage:
    python product_name_mapper.py <product_name> <version> <channel>

Example:
    python product_name_mapper.py sense360-core-c-usb 3.0.0 stable
    # Output: Sense360-Core-Ceiling-USB-v3.0.0-stable.bin
"""

import sys
import re

# ============================================================================
# PRODUCT NAME MAPPING
# ============================================================================
# Maps ESPHome product config names to WebFlash-compatible display names.
# Format: "esphome-name": "WebFlash-Name"
# ============================================================================

PRODUCT_MAPPINGS = {
    # -------------------------------------------------------------------------
    # Release-One (production) — WebFlash config: Ceiling-POE-VentIQ-RoomIQ
    # Artifact name: Sense360-Ceiling-POE-VentIQ-RoomIQ-vX.Y.Z-{channel}.bin
    #
    # FanTRIAC is intentionally excluded from production Release-One while
    # HW-005 is open. The FanTRIAC mapping is kept here so legacy references
    # (the blocked/reference product YAML) still resolve correctly, but it is
    # NOT in the WebFlash build matrix at config/webflash-builds.json.
    # See docs/release-one-hardware-audit.md#fantriac-mapping-resolution
    # -------------------------------------------------------------------------
    "sense360-ceiling-poe-ventiq-roomiq": "Sense360-Ceiling-POE-VentIQ-RoomIQ",
    "ceiling-poe-ventiq-roomiq": "Sense360-Ceiling-POE-VentIQ-RoomIQ",
    "sense360-ceiling-poe-ventiq-fantriac-roomiq": "Sense360-Ceiling-POE-VentIQ-FanTRIAC-RoomIQ",
    # -------------------------------------------------------------------------
    # LED-bearing preview sibling — WebFlash config: Ceiling-POE-VentIQ-RoomIQ-LED
    # Artifact name: Sense360-Ceiling-POE-VentIQ-RoomIQ-LED-vX.Y.Z-{channel}.bin
    # Non-stable channel only (preview). Release-One stays LED-less.
    # -------------------------------------------------------------------------
    "sense360-ceiling-poe-ventiq-roomiq-led": "Sense360-Ceiling-POE-VentIQ-RoomIQ-LED",
    "ceiling-poe-ventiq-roomiq-led": "Sense360-Ceiling-POE-VentIQ-RoomIQ-LED",
    # -------------------------------------------------------------------------
    # Core Series - Ceiling Mount with Power Types
    # -------------------------------------------------------------------------
    "sense360-core-c-usb": "Sense360-Core-Ceiling-USB",
    "sense360-core-c-poe": "Sense360-Core-Ceiling-POE",
    "sense360-core-c-pwr": "Sense360-Core-Ceiling-PWR",
    # -------------------------------------------------------------------------
    # Core Series - Wall Mount with Power Types
    # -------------------------------------------------------------------------
    "sense360-core-w-usb": "Sense360-Core-Wall-USB",
    "sense360-core-w-poe": "Sense360-Core-Wall-POE",
    "sense360-core-w-pwr": "Sense360-Core-Wall-PWR",
    # -------------------------------------------------------------------------
    # Core Voice Series - Ceiling Mount with Power Types
    # -------------------------------------------------------------------------
    "sense360-core-v-c-usb": "Sense360-CoreVoice-Ceiling-USB",
    "sense360-core-v-c-poe": "Sense360-CoreVoice-Ceiling-POE",
    "sense360-core-v-c-pwr": "Sense360-CoreVoice-Ceiling-PWR",
    # -------------------------------------------------------------------------
    # Core Voice Series - Wall Mount with Power Types
    # -------------------------------------------------------------------------
    "sense360-core-v-w-usb": "Sense360-CoreVoice-Wall-USB",
    "sense360-core-v-w-poe": "Sense360-CoreVoice-Wall-POE",
    "sense360-core-v-w-pwr": "Sense360-CoreVoice-Wall-PWR",
    # -------------------------------------------------------------------------
    # Core Series - Base Configurations (no power type specified)
    # -------------------------------------------------------------------------
    "sense360-core-ceiling": "Sense360-Core-Ceiling",
    "sense360-core-wall": "Sense360-Core-Wall",
    "sense360-core-ceiling-presence": "Sense360-Core-Ceiling-Presence",
    "sense360-core-wall-presence": "Sense360-Core-Wall-Presence",
    "sense360-core-ceiling-bathroom": "Sense360-Core-Ceiling-Bathroom",
    # -------------------------------------------------------------------------
    # Core Voice Series - Base Configurations
    # -------------------------------------------------------------------------
    "sense360-core-voice-ceiling": "Sense360-CoreVoice-Ceiling",
    "sense360-core-voice-wall": "Sense360-CoreVoice-Wall",
    # -------------------------------------------------------------------------
    # Mini Series - Presence Variants
    # -------------------------------------------------------------------------
    "sense360-mini-presence": "Sense360-Mini-Presence",
    "sense360-mini-presence-basic": "Sense360-Mini-Presence-Basic",
    "sense360-mini-presence-advanced": "Sense360-Mini-Presence-Advanced",
    "sense360-mini-presence-ld2412": "Sense360-Mini-Presence-LD2412",
    "sense360-mini-presence-advanced-ld2412": "Sense360-Mini-Presence-Advanced-LD2412",
    # -------------------------------------------------------------------------
    # Mini Series - AirIQ Variants
    # -------------------------------------------------------------------------
    "sense360-mini-airiq": "Sense360-Mini-AirIQ",
    "sense360-mini-airiq-basic": "Sense360-Mini-AirIQ-Basic",
    "sense360-mini-airiq-advanced": "Sense360-Mini-AirIQ-Advanced",
    "sense360-mini-airiq-ld2412": "Sense360-Mini-AirIQ-LD2412",
    # -------------------------------------------------------------------------
    # Accessory Products
    # -------------------------------------------------------------------------
    "sense360-poe": "Sense360-POE",
    "sense360-fan-pwm": "Sense360-Fan-PWM",
}


def convert_product_name(product_name: str) -> str:
    """
    Convert an ESPHome product name to WebFlash display name.

    Uses explicit mapping table for known products, falls back to
    intelligent conversion for unknown products.

    Args:
        product_name: ESPHome product name (e.g., "sense360-core-c-usb")

    Returns:
        WebFlash display name (e.g., "Sense360-Core-Ceiling-USB")
    """
    # Check explicit mapping first
    if product_name in PRODUCT_MAPPINGS:
        return PRODUCT_MAPPINGS[product_name]

    # Fallback: intelligent conversion for unmapped products
    # This handles any new products that might be added
    return _intelligent_convert(product_name)


def _intelligent_convert(product_name: str) -> str:
    """
    Intelligently convert an unmapped product name to WebFlash format.

    Applies common transformations:
    - sense360- prefix -> Sense360- prefix
    - Capitalize each segment
    - Expand common abbreviations (c->Ceiling, w->Wall, v->Voice)
    - Uppercase power types (usb->USB, poe->POE, pwr->PWR)

    Args:
        product_name: ESPHome product name

    Returns:
        Converted WebFlash display name
    """
    # Abbreviation expansions
    ABBREVIATIONS = {
        "c": "Ceiling",
        "w": "Wall",
        "v": "Voice",
        "usb": "USB",
        "poe": "POE",
        "pwr": "PWR",
        "s3": "S3",
    }

    # Special terms that should be capitalized in specific ways
    SPECIAL_CAPS = {
        "airiq": "AirIQ",
        "ventiq": "VentIQ",
        "roomiq": "RoomIQ",
        "fanrelay": "FanRelay",
        "fanpwm": "FanPWM",
        "fandac": "FanDAC",
        "fantriac": "FanTRIAC",
        "ld2412": "LD2412",
        "pwm": "PWM",
        "triac": "TRIAC",
        "dac": "DAC",
    }

    # Remove sense360- prefix
    if product_name.startswith("sense360-"):
        name = product_name[9:]  # len("sense360-")
    else:
        name = product_name

    # Split by dashes
    parts = name.split("-")

    # Convert each part
    converted_parts = ["Sense360"]
    for part in parts:
        part_lower = part.lower()

        # Check for special capitalizations
        if part_lower in SPECIAL_CAPS:
            converted_parts.append(SPECIAL_CAPS[part_lower])
        # Check for abbreviations (but only single-letter ones in certain contexts)
        elif part_lower in ABBREVIATIONS and len(part) <= 3:
            converted_parts.append(ABBREVIATIONS[part_lower])
        else:
            # Default: capitalize first letter
            converted_parts.append(part.capitalize())

    return "-".join(converted_parts)


def generate_webflash_filename(product_name: str, version: str, channel: str) -> str:
    """
    Generate the full WebFlash-compatible firmware filename.

    Args:
        product_name: ESPHome product name (e.g., "sense360-core-c-usb")
        version: Firmware version (e.g., "3.0.0")
        channel: Release channel (e.g., "stable", "preview", "beta")

    Returns:
        Full filename (e.g., "Sense360-Core-Ceiling-USB-v3.0.0-stable.bin")
    """
    display_name = convert_product_name(product_name)
    return f"{display_name}-v{version}-{channel}.bin"


def main():
    """CLI entry point."""
    if len(sys.argv) < 4:
        print(
            "Usage: python product_name_mapper.py "
            "<product_name> <version> <channel>",
            file=sys.stderr,
        )
        print(
            "Example: python product_name_mapper.py "
            "sense360-core-c-usb 3.0.0 stable",
            file=sys.stderr,
        )
        sys.exit(1)

    product_name = sys.argv[1]
    version = sys.argv[2]
    channel = sys.argv[3]

    filename = generate_webflash_filename(product_name, version, channel)
    print(filename)


if __name__ == "__main__":
    main()
