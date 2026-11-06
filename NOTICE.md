# Provenance and distribution boundaries

This repository contains original continuation tooling under GPL-3.0-only.
LasVola/godhand-recomp is a separately fetched dependency, pinned in upstream.json;
its declared GPL license and its own attribution/notices remain applicable.
That project builds on PS2Recomp and other projects described by its notices.
Do not relabel their work as ours or as MIT. No decompiled/translated game source
is included here. Source exposure in the separate evaluation is recorded; this
continuation is not presented as an independent clean-room engine.

God Hand and its contents belong to their respective rights holders. No game
rights or affiliation are asserted. A repository license is not permission to
redistribute game assets, program images, generated game code or saves. No such
material may be added to this repository, its releases, Actions artifacts or CI.

The old independent MIT lab remains separate and paused, not completed.

The original native resource bridge calls the privately fetched upstream generic
SHA-256 helper; that implementation is not vendored here. Integration metadata
selects exact normalized host-source hashes and records only original additions,
not game functions or instruction patches. Its byte offsets index open-source
host files, not the game disc. The prior private range helper was original GPL
evaluation code; the public bridge retains that provenance and is not MIT.
