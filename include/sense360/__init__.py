"""Sense360 shared-logic external component (REMOTE-PACKAGE-HEADER-RESOLUTION-001).

This ESPHome component exists **only** to deliver the canonical, header-only
``include/sense360/*.h`` logic engines to a build tree and ``#include`` them so
framework lambdas can reference the ``sense360::*`` C++ namespaces. It declares
no entities, pins, buses or platforms and changes no firmware behaviour.

Why it exists
-------------
The framework packages compile their shared engine from
``include/sense360/<engine>.h`` via ``esphome: includes:`` with a path relative
to the ``products/`` config directory (``../include/sense360/...``). That path
only resolves for a *repository-local* build, where the main config lives under
``products/``. When a Home Assistant user consumes a framework through an
ESPHome **git package**, ESPHome resolves the same include against the
*consumer's* config directory (e.g. ``/config/esphome``), so it looks for
``/config/include/sense360/...`` — a file the package never delivers — and
validation fails with "Could not find file".

An ESPHome external component, by contrast, is fetched with the package,
copied into the build's ``src/esphome/components/sense360/`` directory and made
available on the include path regardless of where the consumer's config lives.
This is the same delivery mechanism the repository already uses for its radar
C++ components (``packages/base/external_components.yaml``). The remote-consumer
wrapper packages under ``packages/remote/`` reference this component and remove
the local ``esphome: includes:`` entry, so exactly one copy of each header is
compiled (no duplicate/ODR translation unit) and the *same* canonical file
proven by ``tests/unit/test_*_engine.cpp`` is what ships.

Single source of truth
-----------------------
The headers stay physically in ``include/sense360/`` — the one location the
native C++ unit tests (``#include "../../include/sense360/..."``) and the
repository-local ``esphome: includes:`` builds already use. This package is that
directory; it introduces no second copy of any engine and no YAML
re-implementation of any algorithm.
"""

import esphome.codegen as cg
import esphome.config_validation as cv

CODEOWNERS = ["@sense360store"]

# The canonical shared, header-only logic engines. Order is irrelevant:
# every header is ``#pragma once`` guarded and ``ventiq_engine.h`` pulls in
# ``airiq_engine.h`` itself via a sibling include (both land in the same
# delivered component directory). Every header is self-contained (standard
# library only) and is the exact file exercised natively by the C++ unit
# tests, so nothing here can drift from the tested implementation.
SHARED_HEADERS = (
    "airiq_engine.h",
    "ventiq_engine.h",
    "roomiq_engine.h",
    "presence_fusion.h",
    "led_controller.h",
    "led_logic.h",
    "blower_controller.h",
    "thresholds.h",
    "calibration.h",
    "time_utils.h",
)

# Config-only component: an empty mapping (or bare `sense360:`) is all that is
# needed to load it and run to_code, which emits the header includes.
CONFIG_SCHEMA = cv.Schema({})


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
