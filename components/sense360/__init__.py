"""Sense360 foundation external component (SENSE360-CANONICALISATION-001 PR 08).

This is the base ESPHome external component for the Sense360 platform. It has
two jobs and deliberately no third:

1. **Deliver the canonical shared logic engines.** The header-only engines in
   this directory are the exact files exercised by the native C++ unit tests
   (``tests/unit/test_*.cpp``), so tested logic and shipped logic cannot
   drift. Loading ``sense360:`` emits an ``#include`` for every shared header
   so framework lambdas compiled elsewhere in the build can reference the
   ``sense360::*`` namespaces. This subsumes the former
   ``include/sense360/__init__.py`` delivery-only component
   (REMOTE-PACKAGE-HEADER-RESOLUTION-001): the same mechanism, now living in
   the real ``components/`` tree alongside the radar components, with the
   headers physically inside the component so they travel with any git
   package fetch regardless of the consumer's config directory.

2. **Establish the component schema conventions for the domain components.**
   The optional identity keys below validate against the canonical hardware
   catalog literals and surface as compile-time defines only. They are the
   schema pattern the PR 09..12 domain components (``sense360_roomiq``,
   ``sense360_presence``, ``sense360_airiq`` / ``sense360_ventiq``,
   ``sense360_led``) extend; this foundation component declares **no
   entities, no pins, no buses and no platforms** and changes no firmware
   behaviour.

Boundary (the no-fork rule, machine-enforced by
``tests/test_external_components.py``): raw sensor communication uses
built-in ESPHome drivers (or the separately vendored driver components,
each recorded in ``config/external-components.json`` with provenance).
Sense360 product behaviour lives in these shared engines and the coming
domain components — never in a forked copy of an upstream sensor driver.

Canonical identity axes (see ``docs/hardware-catalog.md`` /
``config/hardware-catalog.json``): the board axis is the ``S360-*`` SKU;
the firmware-configuration axis is the WebFlash config string. The
``BOARD_SKUS`` literal below is pinned equal to the machine-readable
catalog by ``tests/test_external_components.py`` — the catalog decides,
this literal follows.
"""

import esphome.codegen as cg
import esphome.config_validation as cv

CODEOWNERS = ["@sense360store"]

# The canonical shared, header-only logic engines. Order is irrelevant: every
# header is ``#pragma once`` guarded and self-contained (standard library
# only), and each is the exact file exercised natively by the C++ unit tests,
# so nothing here can drift from the tested implementation.
SHARED_HEADERS = (
    "sense360_runtime.h",
    "airiq_engine.h",
    "ventiq_engine.h",
    "roomiq_engine.h",
    "roomiq_climate_compensation.h",
    "presence_fusion.h",
    "led_controller.h",
    "led_logic.h",
    "blower_controller.h",
    "thresholds.h",
    "calibration.h",
    "time_utils.h",
)

# Canonical board SKUs — pinned equal to config/hardware-catalog.json by
# tests/test_external_components.py (the catalog is the source of truth; a
# consumer build cannot read repository config files, so the component
# carries the literal and the guard keeps it fresh).
BOARD_SKUS = (
    "S360-100",
    "S360-200",
    "S360-210",
    "S360-211",
    "S360-300",
    "S360-310",
    "S360-311",
    "S360-312",
    "S360-320",
    "S360-400",
    "S360-410",
)

CONF_BOARD_SKU = "board_sku"
CONF_CONFIG_STRING = "config_string"

# Foundation schema: an empty mapping (or bare `sense360:`) is all that is
# needed to load the component and deliver the engines. The identity keys are
# optional compile-time declarations that validate against the canonical
# axes; they emit preprocessor defines only (no runtime behaviour, no
# hardware autodetection claim).
CONFIG_SCHEMA = cv.Schema(
    {
        cv.Optional(CONF_BOARD_SKU): cv.one_of(*BOARD_SKUS, upper=True),
        cv.Optional(CONF_CONFIG_STRING): cv.string_strict,
    }
)


async def to_code(config):
    # Emit an #include for every shared header so framework lambdas compiled
    # elsewhere in the build can reference the sense360::* namespaces. The
    # component directory is copied to src/esphome/components/sense360/, so a
    # self-referential include path is used (matching how ESPHome ships any
    # external component's own headers).
    for header in SHARED_HEADERS:
        cg.add_global(
            cg.RawStatement(f'#include "esphome/components/sense360/{header}"')
        )
    if CONF_BOARD_SKU in config:
        cg.add_define("SENSE360_BOARD_SKU", config[CONF_BOARD_SKU])
    if CONF_CONFIG_STRING in config:
        cg.add_define("SENSE360_CONFIG_STRING", config[CONF_CONFIG_STRING])
