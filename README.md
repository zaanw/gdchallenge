# GD Challenge Engine — ABSOLUTE COLLAPSE

A working, dependency-free Python 3.11+ modular level generator. It creates an editable
GDShare XML `.gmd`, raw GD editor stream, diagnostic trajectory, geometry report,
SVG overview and release ZIP. Its design target is a dark red/neon **TOP 1 Wave
Challenge**, with seven sections over a nominal 44 seconds at 4x speed.

```bash
python main.py --generate absolute-collapse
python -m unittest discover -s tests -v
python main.py --convert output/ABSOLUTE_COLLAPSE.level --output converted
```

Run these commands from this repository. `--output DIRECTORY` changes the export
location. Generation is deterministic and replaces only its named generated files;
do not hand-edit files in `output/` without copying them elsewhere first.

## Gameplay

| Time | Timeline | Section | Mode |
|---|---|---|---|
| 0–4.4s | 0–10% | Rupture | Cube |
| 4.4–11s | 10–25% | Needle ignition | Mini Wave 4x |
| 11–17.6s | 25–40% | Crimson interference | Nine Circles styled Wave |
| 17.6–24.2s | 40–55% | Event horizon | Ship |
| 24.2–30.8s | 55–70% | Oblique fracture | Slope Wave |
| 30.8–37.4s | 70–85% | Zero tolerance | Precision Wave |
| 37.4–44s | 85–100% | Collapse gauntlet | Wave |

All percentages describe the modeled constant-speed gameplay timeline. A short entry
lead and the game's automatic end travel can change displayed progress/duration.
Wave reversal thresholds use nonperiodic motifs. Conservative corridor widths change
from 36 units in mini-wave to 34 in precision-wave; transition buffers open around
portals. Spike clusters sit under approximate cube jump arcs. Ship uses a bounded
acceleration control witness. Shape/glow objects remain editable.

## Engine

`src/core` implements objects, transforms, groups, colors, triggers, serialization and
validation. `src/gameplay` contains cube, wave, ship, slope construction and portals.
`src/decoration` adds glow layers, background motes, channel pulses and group animation.
`src/generator.py` assembles the challenge and exports artifacts. No GUI or services
are required. `requirements.txt` intentionally has no third-party dependencies.

The collision checker uses full 30-unit square envelopes for block, spike and slope,
rotated/scaled conservatively. Player square half-extents are 15 (cube/ship), 9
(wave), 5 (mini-wave). Swept line segments vs expanded AABBs avoid tunneling between
240 Hz samples. The checker also detects obstacle-envelope overlaps, ground crossings,
dangling trigger targets, missing channels and noncontinuous section boundaries.
Moving collision solids are rejected because the checker models static geometry.

## Validation limits — read before playing

**This is a generated candidate, not a verified TOP 1 release.** GD 2.281 was not run.
Exact collision meshes, tick physics, portal activation and real playability are not
proven. The successful report means an assumed model trajectory clears conservative
static obstacle envelopes. It does not establish a game-executable input sequence.
Cube uses gravity 2600 and jump impulse 620; ship acceleration is 1100, velocity cap
220; wave slopes are ±1 or ±2. These assumptions are explicit and require calibration.
No gameplay bug is silently excluded from the report by switching off checks.

**Creo — Flow is not embedded or automatically synchronized.** A verified song ID,
licensed/local audio and measured timing were not available. Pulses use an editable
provisional 140 BPM grid. Select music and measure its offset/BPM in-game before
claiming song synchronization. TOP 1 difficulty needs independent human assessment.

The format is grounded in GDShare/gmd-api, gd.py and GD Docs, but actual import into
2.281 and availability of a compatible GDShare build are untested. See
[format sources](docs/format_sources.md) and [import instructions](docs/import_instructions.md).
No arbitrary JSON is labeled `.gmd`. The `.level` file is the documented raw fallback.

## Release contents

`output/ABSOLUTE_COLLAPSE.gmd`, `ABSOLUTE_COLLAPSE.zip`, `validation_report.txt`,
`validation_report.json`, `import_instructions.md`, `format_sources.md`,
`ABSOLUTE_COLLAPSE.level`, `trajectory.csv`, `sections.json`, `layout_preview.svg`.
The ZIP bundles all level artifacts, validation evidence, import/format documentation
and this README. The SVG is a schematic overview, not a screenshot of the game.

No runtime secrets, external service or downloadable Python package is required.
Use the existing checkout in cloud tasks; each task is already isolated, so do not
create a Git worktree unless explicitly requested.
