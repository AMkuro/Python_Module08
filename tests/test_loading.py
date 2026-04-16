import contextlib
import importlib.util
import io
import pathlib
import unittest
from unittest.mock import patch


ROOT = pathlib.Path(__file__).resolve().parents[1]
LOADING_PATH = ROOT / "ex01" / "loading.py"


def load_loading_module():
    spec = importlib.util.spec_from_file_location(
        "test_loading_module",
        LOADING_PATH,
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class LoadingProgramTests(unittest.TestCase):
    def test_main_uses_sample_data_when_requests_is_unavailable(self) -> None:
        module = load_loading_module()

        def fake_check_dependency(name: str) -> dict[str, object]:
            versions = {
                "pandas": "2.2.3",
                "matplotlib": "3.8.4",
                "numpy": "1.26.4",
            }
            if name == "requests":
                return {"name": name, "successed": False}
            return {
                "name": name,
                "successed": True,
                "version": versions[name],
            }

        output = io.StringIO()
        with patch.object(
            module,
            "check_dependency",
            side_effect=fake_check_dependency,
        ):
            with patch.object(module, "fetch_matrix_population") as fetch_mock:
                with patch.object(
                    module,
                    "build_dataframe",
                    return_value=object(),
                ):
                    with patch.object(
                        module,
                        "compute_age_stats",
                        return_value={
                            "average_age": 42.0,
                            "youngest_age": 18.0,
                            "oldest_age": 75.0,
                            "age_std_dev": 9.5,
                        },
                    ):
                        with patch.object(module, "create_visualization"):
                            with contextlib.redirect_stdout(output):
                                module.main()

        rendered = output.getvalue()
        fetch_mock.assert_not_called()
        self.assertIn("Using built-in sample data.", rendered)
        self.assertIn("pip", rendered)
        self.assertIn("Poetry", rendered)


if __name__ == "__main__":
    unittest.main()
