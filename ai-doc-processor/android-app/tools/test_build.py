"""Host unit tests for the build/deployment command routing (no SDK needed)."""

import contextlib
import io
import os
from pathlib import Path
import subprocess
import unittest
from unittest.mock import patch

import build


class BuildScriptTest(unittest.TestCase):
    def setUp(self):
        self.environment = patch.dict(os.environ, {}, clear=True)
        self.environment.start()
        self.addCleanup(self.environment.stop)

    def test_build_debug_and_release(self):
        with patch.object(build, "gradle") as gradle:
            self.assertEqual(build.main(["build"]), 0)
            gradle.assert_called_once_with(["assembleDebug"], offline=False)
            gradle.reset_mock()
            with contextlib.redirect_stdout(io.StringIO()) as output:
                self.assertEqual(build.main(["--offline", "build", "--variant", "release"]), 0)
            gradle.assert_called_once_with(["assembleRelease"], offline=True)
            self.assertIn("unsigned", output.getvalue())

    def test_host_suites(self):
        for suite, task in (("unit", "testDebugUnitTest"), ("lint", "lintDebug")):
            with self.subTest(suite=suite), patch.object(build, "gradle") as gradle:
                self.assertEqual(build.main(["test", "--suite", suite]), 0)
                gradle.assert_called_once_with([task], offline=False)

    def test_device_suite_filters_and_serial(self):
        for suite, names in build.DEVICE_SUITES.items():
            with self.subTest(suite=suite), patch.object(build, "gradle") as gradle:
                self.assertEqual(
                    build.main(["test", "--suite", suite, "--serial", "emulator-5554"]), 0
                )
                classes = ",".join(f"{build.PACKAGE}.{name}" for name in names)
                gradle.assert_called_once_with(
                    [
                        "connectedDebugAndroidTest",
                        f"-Pandroid.testInstrumentationRunnerArguments.class={classes}",
                    ],
                    offline=False,
                )
                self.assertEqual(os.environ["ANDROID_SERIAL"], "emulator-5554")

    def test_integration_suite_includes_local_assistant(self):
        self.assertEqual(
            build.DEVICE_SUITES["integration"],
            ("DocumentIntegrationTest", "LocalAssistantIntegrationTest"),
        )

    def test_all_suites(self):
        with patch.object(build, "gradle") as gradle:
            self.assertEqual(build.main(["test", "--suite", "all"]), 0)
            gradle.assert_called_once_with(
                ["testDebugUnitTest", "lintDebug", "connectedDebugAndroidTest"], offline=False
            )

    def test_install_builds_installs_and_launches(self):
        with (
            patch.object(build, "gradle") as gradle,
            patch.object(build, "run") as run,
            patch.object(build, "adb_path", return_value="/sdk/platform-tools/adb"),
            patch.object(Path, "is_file", return_value=True),
        ):
            self.assertEqual(build.main(["install", "--serial", "device-1"]), 0)
            gradle.assert_called_once_with(["assembleDebug"], offline=False)
            apk = str(build.ROOT / "app/build/outputs/apk/debug/app-debug.apk")
            self.assertEqual(
                run.call_args_list[0].args[0],
                ["/sdk/platform-tools/adb", "-s", "device-1", "install", "-r", apk],
            )
            self.assertEqual(
                run.call_args_list[1].args[0],
                [
                    "/sdk/platform-tools/adb", "-s", "device-1", "shell", "am", "start",
                    "-W", "-n", f"{build.PACKAGE}/.MainActivity",
                ],
            )

    def test_install_respects_environment_serial_and_no_build(self):
        with (
            patch.dict(os.environ, {"ANDROID_SERIAL": "device-2"}),
            patch.object(build, "gradle") as gradle,
            patch.object(build, "run") as run,
            patch.object(build, "adb_path", return_value="adb"),
            patch.object(Path, "is_file", return_value=True),
        ):
            self.assertEqual(build.main(["install", "--no-build"]), 0)
            gradle.assert_not_called()
            self.assertEqual(run.call_args_list[0].args[0][:3], ["adb", "-s", "device-2"])

    def test_missing_apk_is_a_failure(self):
        with (
            patch.object(Path, "is_file", return_value=False),
            patch.object(build, "run") as run,
            contextlib.redirect_stderr(io.StringIO()),
        ):
            self.assertEqual(build.main(["install", "--no-build"]), 1)
            run.assert_not_called()

    def test_gradle_failure_is_propagated(self):
        with (
            patch.object(build, "gradle", side_effect=subprocess.CalledProcessError(1, "gradle")),
            contextlib.redirect_stderr(io.StringIO()),
        ):
            self.assertEqual(build.main(["build"]), 1)

    def test_adb_sdk_lookup_and_path_fallback(self):
        with (
            patch.dict(os.environ, {"ANDROID_HOME": "/sdk with spaces"}),
            patch.object(Path, "is_file", return_value=True),
        ):
            executable = "adb.exe" if os.name == "nt" else "adb"
            self.assertEqual(
                build.adb_path(), str(Path("/sdk with spaces") / "platform-tools" / executable)
            )
        with patch.object(build.shutil, "which", return_value="/bin/adb"):
            self.assertEqual(build.adb_path(), "/bin/adb")
        with patch.object(build.shutil, "which", return_value=None):
            with self.assertRaises(FileNotFoundError):
                build.adb_path()

    def test_wrapper_offline_arguments_and_no_shell(self):
        with (
            patch.object(Path, "is_file", return_value=True),
            patch.object(build, "run") as run,
        ):
            build.gradle(["assembleDebug"], offline=True)
            command = (
                ["cmd.exe", "/d", "/c", str(build.ROOT / "gradlew.bat")]
                if os.name == "nt" else [str(build.ROOT / "gradlew")]
            )
            run.assert_called_once_with(
                command + ["--no-daemon", "--offline", "assembleDebug"]
            )
        with patch.object(build.subprocess, "run") as run:
            build.run(["adb", "-s", "serial with spaces"], cwd=build.ROOT)
            run.assert_called_once_with(
                ["adb", "-s", "serial with spaces"], cwd=build.ROOT, check=True
            )


if __name__ == "__main__":
    unittest.main()
