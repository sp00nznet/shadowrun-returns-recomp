# Changelog

All notable changes to this project. Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
versions: [SemVer](https://semver.org/).

## [Unreleased]

### Added
- `Setup.cmd` and `tools/setup.py`: prerequisites (asking before installing), finds the game
  (Steam library, GOG install, or GOG offline installer), identifies it by the SHA-256 of
  `Assembly-CSharp.dll`, copies it to `game\<version>\`, recompiles it with netrecomp,
  installs the built `mono.dll` into the copy and writes a launcher.
- `tools/versions.json`: Steam 1.2.7 and GOG 1.2.7.
- Both versions lift 88867/88868 methods and compile.
- Steam 1.2.7 runs windowed to a main menu that renders like the original (logo, slide-in,
  buttons, labels); screenshot in `docs/screenshots/`. Needed netrecomp's Unity liveness
  support (scene loads were unloading the UI atlases) and compiled `List<T>` field ctors.
- In game on Steam 1.2.7: Continue loads the autosave (Dead Man's Switch, the Hive), the
  party spawns with its AI and click-to-move works. Screenshot in `docs/screenshots/`.
