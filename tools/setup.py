"""Set up Shadowrun Returns on netrecomp, end to end. Setup.cmd runs this.

    py -3 tools\\setup.py [--game <folder or GOG installer>] [--version steam-1.2.7|gog-1.2.7] [--yes]

Steps, each skipped when already done, so a rerun resumes:
  1. check prerequisites (asks before installing anything)
  2. find your copy of the game: --game, the Steam library, a GOG install, or a
     GOG offline installer next to this repo or in Downloads
  3. identify it (Steam or GOG) by the hash of Assembly-CSharp.dll
  4. copy it to game\\<version>\\ (your Steam/GOG install is never modified)
  5. get netrecomp (../netrecomp, NETRECOMP, or a clone)
  6. recompile the managed code to C: work\\<version>\\gen
  7. compile mono.dll: work\\<version>\\mono.dll
  8. install it into game\\<version>\\Shadowrun_Data\\Mono (the original is kept as mono.dll.orig)
  9. write "Play Shadowrun Returns (<version>).cmd"

Nothing from the game is downloaded or bundled: it all comes from your copy.
Details go to setup.log; a failure stops with one sentence on what to do.
"""
import argparse, glob, hashlib, json, os, shutil, subprocess, sys, winreg

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG = os.path.join(ROOT, "setup.log")
NETRECOMP_URL = "https://github.com/sp00nznet/netrecomp"
VERSIONS = json.load(open(os.path.join(ROOT, "tools", "versions.json")))
ASSUME_YES = False


def log(msg):
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(msg + "\n")


def say(msg):
    print(msg)
    log(msg)


def fail(msg):
    say("\nSetup stopped: " + msg)
    say(f"Details are in {LOG}")
    sys.exit(1)


def run(args, **kw):
    log("$ " + " ".join(f'"{a}"' if " " in a else a for a in args))
    r = subprocess.run(args, capture_output=True, text=True, **kw)
    log(r.stdout[-20000:] + r.stderr[-20000:])
    return r


def ask(q):
    if ASSUME_YES:
        return True
    return input(q + " [y/N] ").strip().lower().startswith("y")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


# ---- 1. prerequisites ----

def winget(pkg, what, size):
    if not ask(f"{what} is missing. Install it with winget ({pkg}, about {size})?"):
        fail(f"{what} is needed. Install it, then run Setup again.")
    r = run(["winget", "install", "-e", "--id", pkg, "--accept-package-agreements", "--accept-source-agreements"])
    if r.returncode:
        fail(f"winget couldn't install {what}. Install it by hand, then run Setup again.")


def check_prereqs():
    say("[1/9] Checking prerequisites")
    if sys.version_info < (3, 10):
        fail("Python 3.10 or newer is needed.")
    r = run(["dotnet", "--list-sdks"]) if shutil.which("dotnet") else None
    if not r or not any(l.startswith(("8.", "9.", "10.")) for l in r.stdout.splitlines()):
        winget("Microsoft.DotNet.SDK.8", "The .NET 8 SDK (the recompiler runs on it)", "200 MB")
    vswhere = r"C:\Program Files (x86)\Microsoft Visual Studio\Installer\vswhere.exe"
    vs = run([vswhere, "-latest", "-products", "*", "-requires", "Microsoft.VisualStudio.Component.VC.Tools.x86.x64", "-property", "installationPath"]).stdout.strip() if os.path.exists(vswhere) else ""
    if not vs:
        winget("Microsoft.VisualStudio.2022.BuildTools", "Visual Studio 2022 Build Tools with the C++ workload (headers and libraries)", "2 GB")
        say("  In the Visual Studio Installer, add 'Desktop development with C++', then run Setup again.")
        fail("the C++ workload needs adding in the Visual Studio Installer.")
    if not os.path.exists(r"C:\Program Files\LLVM\bin\clang-cl.exe"):
        winget("LLVM.LLVM", "LLVM (clang-cl, the C compiler used for the generated code)", "400 MB")
    if not shutil.which("git"):
        winget("Git.Git", "Git (to fetch the netrecomp toolkit)", "60 MB")
    say("  ok")


# ---- 2/3. find and identify the game ----

def steam_dirs():
    out = []
    try:
        k = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam")
        steam = winreg.QueryValueEx(k, "SteamPath")[0]
        out.append(os.path.join(steam, "steamapps"))
        vdf = os.path.join(steam, "steamapps", "libraryfolders.vdf")
        if os.path.exists(vdf):
            for line in open(vdf, encoding="utf-8", errors="replace"):
                if '"path"' in line:
                    out.append(os.path.join(line.split('"')[3].replace("\\\\", "\\"), "steamapps"))
    except OSError:
        pass
    return [os.path.join(d, "common", "Shadowrun Returns") for d in out]


def gog_dirs():
    for view in (winreg.KEY_WOW64_32KEY, winreg.KEY_WOW64_64KEY):
        try:
            k = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\GOG.com\Games\1207660413", 0, winreg.KEY_READ | view)
            return [winreg.QueryValueEx(k, "path")[0]]
        except OSError:
            pass
    return []


def gog_installers():
    places = [ROOT, os.path.join(os.path.expanduser("~"), "Downloads")]
    return [p for d in places for p in glob.glob(os.path.join(d, "setup_shadowrun_returns_*.exe"))]


def is_game(d):
    return os.path.exists(os.path.join(d, "Shadowrun_Data", "Managed", "Assembly-CSharp.dll"))


def extract_installer(exe):
    out = os.path.join(ROOT, "game", "_gog_installer")
    if is_game(os.path.join(out, "app")):
        return os.path.join(out, "app")
    inno = shutil.which("innoextract")
    if not inno:
        winget("dscharrer.innoextract", "innoextract (unpacks the GOG installer)", "5 MB")
        inno = shutil.which("innoextract") or "innoextract"
    say(f"  unpacking {os.path.basename(exe)} (about 1 GB)")
    os.makedirs(out, exist_ok=True)
    r = run([inno, "-s", "-d", out, exe])
    if r.returncode or not is_game(os.path.join(out, "app")):
        fail("the GOG installer couldn't be unpacked. Check that both installer files (.exe and -1.bin) are present.")
    return os.path.join(out, "app")


def find_game(given):
    say("[2/9] Finding the game")
    cands = []
    if given:
        cands.append(given)
    else:
        cands += [d for d in steam_dirs() + gog_dirs() if is_game(d)]
        cands += gog_installers()
    for c in cands:
        if c.lower().endswith(".exe"):
            c = extract_installer(c)
        if is_game(c):
            say(f"  using {c}")
            return c
    fail("no copy of Shadowrun Returns was found. Run Setup with --game \"<game folder or GOG installer .exe>\".")


def identify(d):
    say("[3/9] Identifying the version")
    h = sha256(os.path.join(d, "Shadowrun_Data", "Managed", "Assembly-CSharp.dll"))
    v = VERSIONS.get(h)
    if not v:
        fail(f"this copy isn't one netrecomp knows (Assembly-CSharp.dll {h[:16]}...). Supported: Steam 1.2.7 and GOG 1.2.7.")
    say(f"  {v['id']}")
    return v


# ---- 4. local copy ----

def copy_game(src, ver):
    dst = os.path.join(ROOT, "game", ver["id"])
    say(f"[4/9] Copying the game to game\\{ver['id']}")
    if is_game(dst) and os.path.exists(os.path.join(dst, "Shadowrun.exe")):
        say("  already there")
        return dst
    r = run(["robocopy", src, dst, "/E", "/NFL", "/NDL", "/NJH", "/NP", "/R:1", "/W:1"])
    if r.returncode >= 8:
        fail("copying the game failed (see the robocopy output in the log).")
    if ver["store"] == "steam":
        # lets the copy start outside Steam's folder; the Steam client must be running
        open(os.path.join(dst, "steam_appid.txt"), "w").write(ver["appid"])
    return dst


# ---- 5. toolkit ----

def get_netrecomp():
    say("[5/9] Getting netrecomp")
    for d in [os.environ.get("NETRECOMP"), os.path.join(os.path.dirname(ROOT), "netrecomp"), os.path.join(ROOT, "tools", "netrecomp")]:
        if d and os.path.exists(os.path.join(d, "tools", "build.py")):
            say(f"  using {d}")
            return d
    d = os.path.join(ROOT, "tools", "netrecomp")
    r = run(["git", "clone", "--depth", "1", NETRECOMP_URL, d])
    if r.returncode:
        fail(f"netrecomp couldn't be cloned from {NETRECOMP_URL}. Put a checkout next to this repo or set NETRECOMP.")
    return d


# ---- 6/7. recompile and build ----

def recompile(nr, game, ver):
    say("[6/9] Recompiling the managed code to C")
    r = run(["dotnet", "build", "-c", "Release", os.path.join(nr, "tools", "netrecomp")])
    if r.returncode:
        fail("the recompiler didn't build (is the .NET 8 SDK installed?).")
    gen = os.path.join(ROOT, "work", ver["id"], "gen")
    r = run(["dotnet", os.path.join(nr, "tools", "netrecomp", "bin", "Release", "net8.0", "netrecomp.dll"), "lift",
             os.path.join(game, "Shadowrun_Data", "Managed"), "-o", gen,
             "--report", os.path.join(ROOT, "work", ver["id"], "lift-failures.txt")])
    if r.returncode:
        fail("recompiling failed.")
    say("  " + r.stdout.strip().splitlines()[0])
    return gen


def build(nr, gen, ver):
    say("[7/9] Compiling mono.dll (several minutes the first time)")
    out = os.path.join(ROOT, "work", ver["id"], "mono.dll")
    r = run([sys.executable, os.path.join(nr, "tools", "build.py"), "--gen", gen, "--out", out])
    if r.returncode:
        fail("compiling failed.")
    return out


# ---- 8/9. install and launcher ----

def install(dll, game):
    say("[8/9] Installing mono.dll into the copy")
    mono = os.path.join(game, "Shadowrun_Data", "Mono", "mono.dll")
    if not os.path.exists(mono + ".orig"):
        shutil.copy2(mono, mono + ".orig")
    shutil.copy2(dll, mono)
    pdb = os.path.splitext(dll)[0] + ".pdb"
    if os.path.exists(pdb):
        shutil.copy2(pdb, os.path.splitext(mono)[0] + ".pdb")


def launcher(game, ver):
    say("[9/9] Writing the launcher")
    name = os.path.join(ROOT, f"Play Shadowrun Returns ({ver['id']}).cmd")
    rel = os.path.relpath(game, ROOT)
    with open(name, "w") as f:
        f.write(f'@echo off\r\ncd /d "%~dp0{rel}"\r\nstart "" Shadowrun.exe %*\r\n')
    say(f"  {os.path.basename(name)}")


def main():
    global ASSUME_YES
    ap = argparse.ArgumentParser()
    ap.add_argument("--game")
    ap.add_argument("--yes", action="store_true", help="install missing prerequisites without asking")
    ap.add_argument("--skip-prereqs", action="store_true")
    a = ap.parse_args()
    ASSUME_YES = a.yes
    open(LOG, "w").close()
    if not a.skip_prereqs:
        check_prereqs()
    src = find_game(a.game)
    ver = identify(src)
    game = copy_game(src, ver)
    nr = get_netrecomp()
    gen = recompile(nr, game, ver)
    dll = build(nr, gen, ver)
    install(dll, game)
    launcher(game, ver)
    say("\nDone.")


if __name__ == "__main__":
    main()
