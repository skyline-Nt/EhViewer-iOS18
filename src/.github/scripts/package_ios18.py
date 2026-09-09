"""Validate an unsigned device archive, then package it for local re-signing.

Run on the macOS build host. Fails if any bundled Mach-O targets a newer OS
or a platform other than iOS. This checks deployment metadata, not runtime
behavior or availability of every dynamically loaded symbol.
"""

import hashlib
import json
import plistlib
import re
import shutil
import subprocess
import sys
from pathlib import Path


def version(value):
    parts = tuple(int(part) for part in value.split("."))
    return parts + (0,) * (3 - len(parts))


def require_ios18(value, label):
    if version(value) > (18, 0, 0):
        raise ValueError(f"{label}: minimum OS {value} exceeds iOS 18.0")


def validate(app):
    bundles = [app] + sorted(
        path for path in app.rglob("*")
        if path.is_dir() and path.suffix in {".appex", ".framework"}
    )
    bundle_report = []
    for bundle in bundles:
        with (bundle / "Info.plist").open("rb") as source:
            info = plistlib.load(source)
        minimum = info.get("MinimumOSVersion")
        if not minimum:
            raise ValueError(f"Missing MinimumOSVersion: {bundle}")
        require_ios18(minimum, bundle)
        executable = bundle / info["CFBundleExecutable"]
        if not executable.is_file():
            raise ValueError(f"Missing bundle executable: {executable}")
        bundle_report.append({"bundle": str(bundle.relative_to(app.parent)),
                              "minimumOS": minimum})

    binaries = []
    # Include frameworks and dylibs, even when they have no bundle plist.
    for path in sorted(app.rglob("*")):
        if not path.is_file() or path.is_symlink():
            continue
        description = subprocess.check_output(["file", "-b", str(path)], text=True)
        if "Mach-O" not in description:
            continue
        architectures = subprocess.check_output(["xcrun", "lipo", "-archs", str(path)], text=True).split()
        if "arm64" not in architectures:
            raise ValueError(f"Missing device arm64 slice: {path}")
        commands = subprocess.check_output(["xcrun", "otool", "-l", str(path)], text=True)
        minimums = []
        for block in re.split(r"Load command \d+", commands):
            if re.search(r"cmd LC_BUILD_VERSION\b", block):
                platform = re.search(r"\bplatform\s+(\S+)", block)
                minimum = re.search(r"\bminos\s+([\d.]+)", block)
                if not platform or platform.group(1).upper() not in {"2", "IOS"} or not minimum:
                    raise ValueError(f"Unexpected platform/build metadata: {path}")
                minimums.append(minimum.group(1))
            elif re.search(r"cmd LC_VERSION_MIN_", block):
                minimum = re.search(r"\bversion\s+([\d.]+)", block)
                if "LC_VERSION_MIN_IPHONEOS" not in block or not minimum:
                    raise ValueError(f"Unexpected legacy platform: {path}")
                minimums.append(minimum.group(1))
        if not minimums:
            raise ValueError(f"Missing Mach-O minimum OS: {path}")
        for minimum in minimums:
            require_ios18(minimum, path)
        binaries.append({"binary": str(path.relative_to(app)),
                         "architectures": architectures, "minimumOS": minimums})
    if not binaries:
        raise ValueError("No Mach-O binaries found")
    return {"targetOS": "18.0", "signed": False, "runtimeTested": False,
            "bundles": bundle_report, "binaries": binaries}


def main():
    archive, output = map(Path, sys.argv[1:])
    apps = list((archive / "Products" / "Applications").glob("*.app"))
    if len(apps) != 1:
        raise ValueError(f"Expected one archived app, found {len(apps)}")
    report = validate(apps[0])
    output.mkdir(parents=True, exist_ok=True)
    staging = output.parent / "ios18-payload"
    # Fail rather than overwrite a pre-existing staging directory.
    payload = staging / "Payload"
    payload.mkdir(parents=True, exist_ok=False)
    shutil.copytree(apps[0], payload / apps[0].name, symlinks=True)
    ipa = output / "EhViewer-iOS18-unsigned.ipa"
    subprocess.run(["ditto", "-c", "-k", "--keepParent", str(payload.resolve()), str(ipa.resolve())], check=True)
    report["sha256"] = hashlib.sha256(ipa.read_bytes()).hexdigest()
    (output / "compatibility.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    (output / "INSTALL.txt").write_text(
        "Unsigned iOS 18 compatibility build. Re-sign with your own account before installation.\n"
        "Archive and deployment metadata checks passed; iPadOS 18 runtime testing is still required.\n",
        encoding="utf-8",
    )
    print(f"Created {ipa}; SHA-256: {report['sha256']}")


if __name__ == "__main__":
    main()
