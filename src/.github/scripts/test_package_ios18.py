"""Exercise deployment rejection cases without requiring Apple's toolchain."""
import importlib.util
import plistlib
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("package_ios18", Path(__file__).with_name("package_ios18.py"))
packager = importlib.util.module_from_spec(spec)
spec.loader.exec_module(packager)


class ArchiveValidationTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.app = Path(self.directory.name) / "Reader.app"
        self.app.mkdir()
        self.write_bundle(self.app, "18.0")
        self.platform = "2"
        self.binary_minimum = "18.0"

    def write_bundle(self, bundle, minimum):
        (bundle / "Info.plist").write_bytes(plistlib.dumps({
            "MinimumOSVersion": minimum, "CFBundleExecutable": "Reader",
        }))
        (bundle / "Reader").write_bytes(b"fixture")

    def output(self, command, **kwargs):
        if command[0] == "file":
            return "Mach-O 64-bit executable arm64" if command[-1].endswith("Reader") else "XML"
        if command[1] == "lipo":
            return "arm64\n"
        return f"Load command 1\n cmd LC_BUILD_VERSION\n platform {self.platform}\n minos {self.binary_minimum}\n sdk 26.2\n"

    def validate(self):
        with patch.object(packager.subprocess, "check_output", side_effect=self.output):
            return packager.validate(self.app)

    def test_accepts_ios18_built_with_new_sdk(self):
        self.assertEqual(self.validate()["binaries"][0]["minimumOS"], ["18.0"])

    def test_rejects_newer_binary_even_with_old_plist(self):
        self.binary_minimum = "26.2"
        with self.assertRaisesRegex(ValueError, "exceeds"):
            self.validate()

    def test_rejects_simulator_binary(self):
        self.platform = "7"
        with self.assertRaisesRegex(ValueError, "Unexpected platform"):
            self.validate()

    def test_rejects_newer_embedded_extension(self):
        extension = self.app / "PlugIns" / "Progress.appex"
        extension.mkdir(parents=True)
        self.write_bundle(extension, "18.1")
        with self.assertRaisesRegex(ValueError, "exceeds"):
            self.validate()


if __name__ == "__main__":
    unittest.main()
