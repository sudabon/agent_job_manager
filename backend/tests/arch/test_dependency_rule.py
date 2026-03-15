import ast
import unittest
from pathlib import Path


class TestDependencyRule(unittest.TestCase):
    """Verify Clean Architecture's dependency rule."""

    def test_domain_layer_dependencies(self):
        """Verify domain layer has no outward dependencies."""
        domain_path = Path("src/domain")
        violations = []

        for py_file in domain_path.rglob("*.py"):
            with open(py_file) as f:
                tree = ast.parse(f.read())

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    module = node.names[0].name
                    if module.startswith("src."):
                        layer = module.split(".")[1]
                        if layer in ["infra", "interface", "app"]:
                            violations.append(
                                f"{py_file.relative_to(domain_path)}: "
                                f"Domain layer cannot import from {layer} layer"
                            )
                elif isinstance(node, ast.ImportFrom):
                    if node.module and node.module.startswith("src."):
                        layer = node.module.split(".")[1]
                        if layer in ["infra", "interface", "app"]:
                            violations.append(
                                f"{py_file.relative_to(domain_path)}: "
                                f"Domain layer cannot import from {layer} layer"
                            )

        self.assertEqual(violations, [], "\nDependency Rule Violations:\n" + "\n".join(violations))
