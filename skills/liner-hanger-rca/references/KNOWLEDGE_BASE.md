# Liner Hanger Knowledge Base — General Concepts
_Last reviewed: 2026-11-11. This is a non-operational engineering reference; job-specific approved documents control._

## 1. Equipment and assembly map
- **Drill pipe / workstring:** conveyance and a pathway for pumping, torque and axial loading. Surface rig measurements describe behavior at measurement locations, not necessarily instantaneous downhole conditions.
- **Running/setting/release tool:** mechanical interface between workstring and liner system; can contain release or activation features. Hydraulic collet and mechanical right-hand release designs are examples, not universal architectures.
- **Liner hanger:** supports the liner load in previous casing, depending on tool design; conventional slip/cone, hydraulic-set, mechanical-set and expandable architectures cannot be treated as interchangeable.
- **Liner-top packer / PBR (when present):** sealing and access/interface components with their own activation and verification steps. Packer set is not automatically hanger set.
- **Liner, centralizers, landing collar, ball seat, wiper plugs, float equipment and shoe:** present/absent and ordered according to actual job tally and vendor configuration.
- For the playback schematic, render **drill pipe**, **running tool**, and **liner/BHA** as separate identified segments. Use actual tally lengths, MD and position of tool components where known; no invented mechanical states.

## 2. Typical stage vocabulary — not a universal sequence
Pre-job preparation and running tool verification; run in hole; circulate/condition; any planned activation preparation (ball/seat or other mechanism); set hanger; transfer/verify weight; release running tool and verify; cement/displace as applicable; set liner-top packer where used; perform approved tests; retrieve running string.
**Warning:** different systems can combine, omit or reorder these stages. In particular, activation may be hydraulic, mechanical, expandable, or otherwise; no stage may be inferred from generic industry background.

## 3. Mandatory surface telemetry for the initial product
- **Time:** timezone, clock origin, synchronisation, sample interval, rig event annotations.
- **Depth:** measured depth, bit/liner shoe/hanger references, block movement, datum.
- **Hookload:** pickup and slack-off load at corresponding depth, expected string weight, buoyancy, drag, and background trend. Compare under similar operating conditions.
- **Standpipe pressure and pump rate:** examine together and with mud properties and event phase; a pressure increase at unchanged flow may require investigation, but is not by itself evidence of a specific fault.
- **Pump strokes and cumulative pumped volume:** reconcile pump calibration, flow rate integral, planned capacity and event volumes, looking for missing/inconsistent data.
- **Torque and RPM:** compare jointly with axial load and movement; stop/start and connection periods need special handling.
- **Pit/returns data** where supplied: investigate apparent gains/losses only after sensor and operating context checks.

## 4. What event-detection can and cannot say
- Identify **procedure deviation**, **unexpected telemetry pattern**, **sensor/data concern**, or **unresolved state** separately.
- A possible premature set can be a hypothesis when an earlier change in pickup/slack-off response, drag, torque, pressure or ability to advance occurs; no single surface signal verifies slips/packer engagement.
- Differing activation mechanisms and antipreset features require equipment-specific interpretation. Some pressure-balanced systems deliberately decouple deployment circulation pressures from hanger activation.
- Compare events before and after the suspected first departure, account for pump rate and fluid changes, and list plausible alternative causes (hole tightness, obstruction, packoff, fluid hydraulics, sensor offset, setup/assembly discrepancy).
- Distinguish a confirmed physical cause supported by inspection and expert review from a hypothesis inferred from logs.

## 5. Learning design
There are four separate knowledge assets: **public engineering concepts**, **job-specific approved requirements**, **observed job histories**, and **reviewed case outcomes**. Learn the first two by extraction and explicit review; accumulate third through imports; promote only fourth to retrieval-supported prior cases. Future fault-finding should link each comparison to its source case and clearly state differences. Never learn operating setpoints from an unrelated job or generic marketing brochure.

## 6. Public case lessons (not prescriptive limits)
- Halliburton describes floated-liner hydraulic transitions as a context in which premature hanger setting or running tool release was a concern, and describes a pressure-balanced design to mitigate it.
- Packers Plus describes a case where upward string movement during a stuck-string event could activate a liner-top packer before reaching bottom; its mitigation was specific to that assembly design.
- Weatherford describes running-tool accessories, packoff systems and packer-setting interfaces as separate components that influence sequence interpretation.
- SLB describes both mechanical and hydraulic release tools and anti-preset hardware, demonstrating why vendor/assembly-specific logic is necessary.
See `SOURCE_REGISTER.md` for primary pages.
