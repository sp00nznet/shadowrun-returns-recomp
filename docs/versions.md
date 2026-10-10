# Versions

Steam and GOG ship the same Unity 4.2.0f4 player (`Shadowrun.exe`), the same `mono.dll`
and the same class library. Only three assemblies differ:

| File | Steam 1.2.7 | GOG 1.2.7 |
|---|---|---|
| `Assembly-CSharp.dll` | `c0e46e22...` | `cec8df78...` |
| `Assembly-CSharp-firstpass.dll` | `d8fe5b82...` | `e7fdc1fc...` |
| `Assembly-UnityScript.dll` | `146ac4f1...` | `d8e893cc...` |

(full hashes in `tools/versions.json`). So a version is just a different set of generated
C: setup picks it from the hash of `Assembly-CSharp.dll`, and the built `mono.dll` checks
each assembly Unity loads against the one it was compiled from.

The Steam copy keeps Steam integration (`SteamworksManaged.dll` P/Invokes into
`SteamworksNative.dll`); a copy outside the Steam folder starts with `steam_appid.txt`
(234650) beside the exe while the Steam client runs. The GOG copy ships the same
Steamworks assemblies, unused, plus GOG's `goggame-1207660413.dll`.

The GOG offline installer is Inno Setup; `innoextract -s` unpacks it to `app\`, which is
the game folder.
