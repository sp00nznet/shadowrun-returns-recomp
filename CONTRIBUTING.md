# Contributing to shadowrun-returns-recomp

This repo recompiles Shadowrun Returns with [netrecomp](https://github.com/sp00nznet/netrecomp).
It holds only the setup tooling, the version table and docs; the recompiler and runtime live
in netrecomp.

## Setup

Run `Setup.cmd`, or follow Getting Started in the [README](README.md). You need your own copy
of the game (Steam or GOG 1.2.7).

## What helps most

- **Play it and report where it breaks**: what you did, a screenshot, `setup.log` if setup
  failed, and the game's log (`Shadowrun_Data\output_log.txt` in the copy under `game\`).
  Run with `NR_DEBUG=1` to get the managed exception or fault in the log.
- **Test the GOG build.** Steam 1.2.7 is the one that has been played so far.
- **Fixes belong in netrecomp** when they're general (a runtime icall, a lowering bug). Keep
  only Shadowrun-specific setup or version data here.

## Game data

Never commit the game, its assemblies, generated C, decompiled source, assets, saves or
recordings of the game's audio. Screenshots of your own runs in `docs/screenshots/` are fine.

## Where your code comes from

Contributions must be your own work, or come from a source whose licence is compatible with
MIT (MIT, BSD, zlib, Apache-2.0, public domain). Don't port code from GPL or LGPL projects
(the old Mono runtime, Wine). If something came from elsewhere, say so in the PR with a link.
AI-assisted contributions are welcome, provided a human understood and verified the change.

## Where to ask

[The sp00nznet recomp Discord](https://discord.gg/CRpzGWZFcu).

## Licence

MIT. By submitting a contribution you agree that it is released under the same licence.
