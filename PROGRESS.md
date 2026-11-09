# Canonical progress and publication workflow

Owner decision, 9 November 2026: **god-hand-pc is the sole active repository for
PC code, documentation, roadmap and public journal**. The MIT Rust/Bevy lab at
god-hand-rs is historical, paused and not achieved. Do not send future PC progress
commits to it. Preserve its old pages, screenshot originals, WIP and history.

## Resume and evidence

Read AGENTS.md, DIRECTION.md, ARCHITECTURE.md, the active goal, both current Git
state and `.local/progress-checkpoint.json`. `docs/journal.json` is the canonical
public source for future entries, tasks and reviewed comparisons. Generate
ROADMAP.md and the static Pages HTML with `python scripts/journal.py`.
The full PC-port goal remains active; the editorial migration is only a milestone.

At useful boundaries record exact revisions, commands, tool versions, native
results, hashes, private evidence paths, failures, pending process identities and
the next falsifiable experiment. Poll confirmed live jobs before restarting.
Tests, native linking, actual runtime, persistence and reference fidelity are
separate gates. No percentages, invented performance, promised remaster features
or autonomous level-beating. No delegation and no new Rust work.

## Journal and selected comparisons

After substantial progress, add an English factual entry with actual evidence
and limitations, then adjust roadmap statuses only against acceptance criteria.
Historical entries/reports imported in docs/migration.json retain their exact
original text, dates, attribution and scope. Their migration is not a rerun.
Keep corrections/superseding results in new entries rather than rewriting history.
Source reports are unchanged Markdown; generated HTML adds an editorial banner.
Their exact raw bytes are protected with explicit `-text` Git attributes, even
under Windows `core.autocrlf=true`. Do not normalize/rewrite them or weaken the
SHA-256 check to hide checkout differences. A fresh invented-data clone regression
tests this boundary; generated HTML and new journal entries remain editable.

Publish only explicitly reviewed screenshot originals, never a directory sweep.
Register both sides, implementation labels, same-frame/same-landmark/unmatched
alignment, original resolution, capture time/timezone, exact runtime/revision,
SHA-256, scenario, observations and limitations in `comparisons`. Preserve each
original byte-for-byte under docs/media/<sha256>.png, with a download link.
Legacy `bevy` registry keys in imported native comparisons are schema history,
not an implementation label. Retail and prototype claims stay separate.
Do not manufacture image pairs for nonvisual work. No game pixels in test fixtures.
CI may check approved publication-file hashes and headers, not treat them as
synthetic rendering inputs. Journal-only JPEG captures have a separate reviewed
`captures` registry. Never crop/repaint/overwrite failed original evidence.

The owner requested selected screenshot publication, not rights-holder permission.
Game imagery is not MIT/GPL. Original GPL tooling, imported MIT text and game
rights remain distinct. No ISO, ELF, asset extract, dump, save, generated game
code, binary, third-party checkout or private research output belongs in public.

## Verification and free hosting

1. Run relevant original synthetic tests and inspect the actual site.
2. Generate HTML/roadmap; explicitly stage only reviewed paths and update the
   exact PUBLIC_FILES.json allowlist. Never stage unrelated WIP or .local/.
3. Run `python scripts/check_public_tree.py`, full Python tests,
   `python scripts/journal.py --check`, and `git diff --cached --check`.
4. Push main, verify matching CI and Pages deployment, open the published site,
   exercise navigation/downloads and compare selected live originals with Git.

Hosting is free public GitHub Pages at https://yyoudi.github.io/god-hand-pc/,
main:/docs, github.io, standard public runners. No paid service, custom domain,
persistent cache or custom artifact upload. Do not archive the historical lab
without a separate verified Pages/link impact decision.
