# Format provenance and supported subset

Sources read during implementation (not installed as dependencies):

* [gd.py](https://github.com/nekitdev/gd.py), commit
  `f2c1c74bdeb55bbe8e1233ec2f04098ef043f5c8`: `gd/api/objects.py`,
  `gd/api/header.py`, `gd/api/color_channels.py`, `gd/api/levels.py`, `gd/enums.py`.
  Supports the property keys, portal IDs, speed IDs, channel encoding and nominal
  4x horizontal speed 576 units/s used here. This is not a GD 2.281 physics specification.
* [GD Docs](https://github.com/gd-programming/gd.docs), commit
  `860029207cedc7f1a183216a2165c70eff72b24d`: `docs/resources/client/level.md`,
  `level-components/level-object.md`, `inner-level-string.md`, `color-string.md`.
  Confirms header/semicolon structure, transform/group keys and block ID 1.
* [gmd-api](https://github.com/HJfod/gmd-api), commit
  `7d2d49655b6f95dd860fe1903ac2efc5c6c9068b`: `src/GMD.cpp`, `src/Shared.cpp`.
  GDShare uses a `root` DS_Dictionary XML/plist for `.gmd`; `.gmd2` is a different
  archive format. `intoLevel()` steps into `root`; no fictitious JSON container is used.
* [SPWN](https://github.com/Spu7Nix/SPWN-language), commit
  `6ab224065f478fa541e1fbfd187925579000e6c4`:
  `libraries/std/constants.spwn`, corroborating legacy property keys.

Registry: 1 block; 8 spike; 289 legacy 45° slope; 211 legacy non-solid glow;
12 cube; 13 ship; 660 wave; 99 normal size; 101 mini; 1334 4x speed;
899 color; 901 move; 1006 pulse; 1007 alpha; 1049 toggle.
The small legacy shape/glow catalog is not a complete authoritative 2.281 object
catalog. Their live asset mapping, slope appearance and collision meshes still
require an in-game check. No modern particle, shader or camera IDs are guessed.

Supported property vocabulary is explicit in `src/core/objects.py`. Native glow
objects simulate motes; there is no native 2.2 particle emitter. Non-solid decoration
alone receives Move/Alpha. Pulse targets existing color channels. Unknown IDs and
properties fail validation. This validates the supported subset, not arbitrary GD levels.

The compact XML dialect uses `<k>`, `<s>`, `<i>`, `<t/>`, `<f/>`, with
`<plist version="1.0" gjver="2.0"><dict><k>root</k><dict>…`.
`kCEK=4`, `k21=2` (editor), `k14=false` (not verified), `k48=object count`.
`k4` is deterministic gzip (mtime=0), URL-safe base64. No secret, account credential,
server difficulty/rating or fabricated song ID is written.
