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
- Both versions lift 88432/88433 methods and compile.
