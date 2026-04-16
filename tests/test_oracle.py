import contextlib
import importlib.util
import io
import pathlib
import sys
import types
import unittest
from unittest.mock import patch


ROOT = pathlib.Path(__file__).resolve().parents[1]
ORACLE_PATH = ROOT / "ex02" / "oracle.py"


def load_oracle_module():
    fake_dotenv = types.ModuleType("dotenv")
    fake_dotenv.load_dotenv = lambda: None

    spec = importlib.util.spec_from_file_location(
        "test_oracle_module",
        ORACLE_PATH,
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    with patch.dict(sys.modules, {"dotenv": fake_dotenv}):
        spec.loader.exec_module(module)
    return module


class OracleProgramTests(unittest.TestCase):
    def test_main_prints_configuration_source_and_mode_summary(self) -> None:
        module = load_oracle_module()
        config = {
            "MATRIX_MODE": "development",
            "DATABASE_URL": (
                "postgresql://user:password@localhost:5432/matrix_db"
            ),
            "API_KEY": "api_secret-api-key-here",
            "LOG_LEVEL": "DEBUG",
            "ZION_ENDPOINT": "http://localhost:8080/zion",
        }

        output = io.StringIO()
        with patch.object(module, "load_configuration", return_value=config):
            with patch.object(module.os.path, "isfile", return_value=True):
                with contextlib.redirect_stdout(output):
                    module.main()

        rendered = output.getvalue()
        self.assertIn("Configuration source:", rendered)
        self.assertIn(".env file loaded", rendered)
        self.assertIn(
            "Environment variables override .env when present",
            rendered,
        )
        self.assertIn("Mode summary:", rendered)
        self.assertIn("development profile detected", rendered)
        self.assertIn("Local development settings are active", rendered)


if __name__ == "__main__":
    unittest.main()
