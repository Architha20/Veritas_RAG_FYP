"""
Test runner for VeritasRAG using Python's standard unittest.
Ensures the repository root is on sys.path.
"""

import os
import sys
import unittest

# Ensure workspace root is in sys.path
workspace_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if workspace_root not in sys.path:
    sys.path.insert(0, workspace_root)

if __name__ == "__main__":
    print(f"[VeritasRAG] Running test suite with Python: {sys.executable}")
    print(f"[VeritasRAG] Workspace root: {workspace_root}")
    loader = unittest.TestLoader()
    suite = loader.discover(start_dir=os.path.join(workspace_root, "tests"), pattern="test_*.py")
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
