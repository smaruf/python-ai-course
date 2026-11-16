"""Build, test and deploy the native Android app using Python and the Android SDK."""

import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = "com.example.aidocprocessor"
DEVICE_SUITES = {
    "integration": ("DocumentIntegrationTest", "LocalAssistantIntegrationTest"),
    "e2e": ("DocumentE2ETest",),
    "bdd": ("DocumentFeatureTest",),
    "load": ("DocumentLoadTest",),
    "smoke": ("SmokeTest",),
}


def run(command: list[str], *, cwd: Path = ROOT) -> None:
    print("+ " + subprocess.list2cmdline(command), flush=True)
    subprocess.run(command, cwd=cwd, check=True)


def gradle(tasks: list[str], *, offline: bool = False) -> None:
    wrapper = ROOT / ("gradlew.bat" if os.name == "nt" else "gradlew")
    if not wrapper.is_file():
        raise FileNotFoundError(f"Missing Gradle wrapper: {wrapper}")
    command = [str(wrapper)]
    if os.name == "nt":
        command = ["cmd.exe", "/d", "/c", str(wrapper)]
    run(command + ["--no-daemon"] + (["--offline"] if offline else []) + tasks)


def adb_path() -> str:
    executable = "adb.exe" if os.name == "nt" else "adb"
    for variable in ("ANDROID_HOME", "ANDROID_SDK_ROOT"):
        if os.environ.get(variable):
            candidate = Path(os.environ[variable]) / "platform-tools" / executable
            if candidate.is_file():
                return str(candidate)
    found = shutil.which(executable)
    if found:
        return found
    raise FileNotFoundError("adb not found; set ANDROID_HOME or add platform-tools to PATH")


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--offline", action="store_true", help="Use cached Gradle dependencies")
    commands = result.add_subparsers(dest="command", required=True)
    build = commands.add_parser("build", help="Build an APK")
    build.add_argument("--variant", choices=("debug", "release"), default="debug")
    test = commands.add_parser("test", help="Run host or connected-device tests")
    test.add_argument("--suite", choices=("unit", "lint", "all", *DEVICE_SUITES), default="unit")
    test.add_argument("--serial", help="Connected Android device/emulator serial")
    install = commands.add_parser("install", help="Build, install and launch the debug APK")
    install.add_argument("--serial", help="Connected Android device/emulator serial")
    install.add_argument("--no-build", action="store_true", help="Install the existing debug APK")
    return result


def main(argv: list[str] | None = None) -> int:
    arguments = parser().parse_args(argv)
    if getattr(arguments, "serial", None):
        os.environ["ANDROID_SERIAL"] = arguments.serial
    try:
        if arguments.command == "build":
            gradle([f"assemble{arguments.variant.title()}"], offline=arguments.offline)
            if arguments.variant == "release":
                print("Release APK is unsigned; sign it before distribution or installation.")
        elif arguments.command == "test":
            suite = arguments.suite
            if suite == "unit":
                tasks = ["testDebugUnitTest"]
            elif suite == "lint":
                tasks = ["lintDebug"]
            elif suite == "all":
                tasks = ["testDebugUnitTest", "lintDebug", "connectedDebugAndroidTest"]
            else:
                classes = ",".join(f"{PACKAGE}.{name}" for name in DEVICE_SUITES[suite])
                tasks = [
                    "connectedDebugAndroidTest",
                    f"-Pandroid.testInstrumentationRunnerArguments.class={classes}",
                ]
            gradle(tasks, offline=arguments.offline)
        else:
            if not arguments.no_build:
                gradle(["assembleDebug"], offline=arguments.offline)
            apk = ROOT / "app/build/outputs/apk/debug/app-debug.apk"
            if not apk.is_file():
                raise FileNotFoundError(f"Build the debug APK first: {apk}")
            command = [adb_path()]
            serial = arguments.serial or os.environ.get("ANDROID_SERIAL")
            if serial:
                command += ["-s", serial]
            run(command + ["install", "-r", str(apk)])
            run(command + ["shell", "am", "start", "-W", "-n", f"{PACKAGE}/.MainActivity"])
        return 0
    except (FileNotFoundError, subprocess.CalledProcessError, PermissionError) as error:
        print(f"Android automation failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
