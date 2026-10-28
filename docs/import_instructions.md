# Import ABSOLUTE COLLAPSE

1. Back up your Geometry Dash local levels before using any import mod.
2. Install a GDShare build compatible with your installed Geometry Dash/Geode version.
   The format implementation targets [HJfod/gmd-api](https://github.com/HJfod/gmd-api),
   used by [GDShare](https://github.com/HJfod/GDShare). Availability of a build for
   **2.281 has not been verified** in this environment.
3. Use GDShare's level import action and select `ABSOLUTE_COLLAPSE.gmd`.
   This is compact XML/plist, not JSON and not a renamed ZIP. The `root` dictionary
   contains gzip+URL-safe-base64 `k4` editor object data. It is an unverified editable level.
4. If your importer rejects this file, keep `ABSOLUTE_COLLAPSE.level`: it contains
   the uncompressed editor header and semicolon-delimited object stream. Use an
   importer that explicitly supports raw level strings, or regenerate the XML using:
   `python main.py --convert output/ABSOLUTE_COLLAPSE.level --output converted`.
   The converter changes the container; it cannot fix an incompatible game/mod version.
5. In the editor set the intended song to **Creo — Flow**, using its verified lawful
   source/custom song ID on your installation. No guessed song ID or copyrighted audio
   is supplied. Set song offset and replace the provisional 140 BPM pulse grid after
   measuring the actual audio. Current section changes match the modeled 44s timeline,
   not verified musical beats.
6. Test every portal with practice checkpoints, especially cube → mini-wave and ship
   → wave. Inspect slope orientations and non-colliding glow appearance. Validate real
   hitboxes, ship camera bounds, size-change timing, game tick behavior and final travel.
   The trajectory CSV is a diagnostic witness for assumed physics, not a replay or macro.
7. Perform an actual completion/verification before sharing as playable. TOP 1 is only
   the design ambition, not an established Challenge List ranking.

The source generator, report and converter require Python 3.11+ only. No game savefile
is modified. Import in Geometry Dash has **not** been exercised here. Do not mark the
level verified based on the geometry report. See `validation_report.json` for details.
