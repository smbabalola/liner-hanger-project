# Liner Hanger Investigation Workbench

**Status: Real investigation product MVP IN PROGRESS. The earlier offline synthetic demonstration is a verified baseline, not accepted completion of the real application.**  
**Application entrypoint:** [Open app source folder](skills/liner-hanger-rca/app/) · [First-use instructions](skills/liner-hanger-rca/app/README.md)

**Latest REAL-02 development:** Browser UI now includes a per-file evidence register, manual source-labelled job events and a rig-export CSV column/unit mapper, with unverified source units explicitly gated. [Regression 43820021238](https://github.com/smbabalola/liner-hanger-project/actions/runs/43820021238) passed **949 tests per Python version (3.11 and 3.12)**. The real end-to-end case, richer replay workstation and report integration are still open; follow [STEERING.md](STEERING.md), [TODO.md](TODO.md) and the [component integration map](docs/real-mvp-component-integration-map.md).

## Run on Windows

In your existing local checkout:

```powershell
cd C:\dev\liner-hanger-project
git pull --ff-only origin main
start .\skills\liner-hanger-rca\app\index.html
```

The application runs in your default browser; Chrome or Edge recommended. Alternatively, use `py -m http.server 8765` in the `app` directory and browse to `http://localhost:8765`. No account, cloud deployment, API key or Python package installation is needed for the UI.

1. Click **Load synthetic normal example** or **Load synthetic anomalous example**.
2. Explore **Replay** (synchronized surface trends, assembly outline and chronology).
3. Inspect **Deviations** (recorded signal-rule questions, missing evidence and optional reported step order).
4. Drag across a chart to annotate a time interval, or use **Notes** to add and edit findings.
5. Open **Report** to export a Markdown investigation draft; use **Export case JSON** to back up work.

To use authorized job data, import a timestamped surface telemetry CSV plus optional chronological event log and source-identified procedure rulebook. The application never interprets missing evidence as proof of a failed liner hanger. An illustrative moving schematic is not a downhole tool-state measurement.

## Release evidence

[GitHub Actions run 43764373475](https://github.com/smbabalola/liner-hanger-project/actions/runs/43764373475) at source commit `519de543`: **939 tests passed on Python 3.11 and 939 on Python 3.12**, including actual Playwright/Chromium normal/anomalous UI workflows, chart-range note modal, persisted notes, procedure step-order questions, invalid import safeguards, report download, and standalone copied-app case roundtrip.

See [MVP evidence and known limitations](docs/mvp-local-release-evidence.md), [STEERING.md](STEERING.md) and [TODO.md](TODO.md).

**Not field-approved:** The MVP is a retrospective local engineering demonstration, not a Baker Hughes/OEM-approved product, live rig operating guide or independent root-cause determination. The existing Python RCA/hydraulics research modules and other historical work remain in `skills/liner-hanger-rca/` but are not fully incorporated in the offline browser MVP. Real-job engineering validation, further Python integration and wider deployment are post-MVP work.
