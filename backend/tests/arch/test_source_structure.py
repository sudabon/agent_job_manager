import unittest
from pathlib import Path


class ArchitectureConfig:
    """Defines Clean Architecture structure and rules."""

    # Ordered from innermost to outermost layer
    LAYER_HIERARCHY = ["domain", "app", "interface", "infra"]


class TestSourceStructure(unittest.TestCase):
    """Verify top-level source structure follows Clean Architecture."""

    def test_source_folders(self):
        """Verify todo_app contains only Clean Architecture layer folders."""
        src_path = Path("src")
        folders = {f.name for f in src_path.iterdir() if f.is_dir() and not f.name.startswith("__")}

        # All layer folders must exist
        for layer in ArchitectureConfig.LAYER_HIERARCHY:
            self.assertIn(layer, folders, f"Missing {layer} layer folder")

        # No unexpected folders
        unexpected = folders - set(ArchitectureConfig.LAYER_HIERARCHY)
        self.assertEqual(
            unexpected,
            set(),
            f"Source should only contain Clean Architecture layers.\n"
            f"Unexpected folders found: {unexpected}",
        )

    def test_interface_folders(self):
        """Verify interface layer folder names use the expected convention."""
        interface_path = Path("src/interface")
        folders = {
            f.name for f in interface_path.iterdir() if f.is_dir() and not f.name.startswith("__")
        }

        self.assertIn("presenter", folders)
        self.assertNotIn("presender", folders)
