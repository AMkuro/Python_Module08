import importlib.util
import sys
from typing import Any

OUTPUT_IMAGE: str = "matrix_analysis.png"
POPULATION_SIZE: int = 1000
API_URL: str = "https://randomuser.me/api/"
SAMPLE_MATRIX_DATA: list[dict[str, Any]] = [
    {
        "dob": {"age": 24},
        "gender": "female",
        "location": {"country": "Zion"},
    },
    {
        "dob": {"age": 31},
        "gender": "male",
        "location": {"country": "Mega City"},
    },
    {
        "dob": {"age": 42},
        "gender": "female",
        "location": {"country": "Machine City"},
    },
    {
        "dob": {"age": 19},
        "gender": "male",
        "location": {"country": "Nebuchadnezzar"},
    },
    {
        "dob": {"age": 56},
        "gender": "female",
        "location": {"country": "Matrix"},
    },
]


def check_dependency(module_name: str) -> dict[str, Any]:
    try:
        module = importlib.import_module(module_name)
        version: str = getattr(module, "__version__", "unknown")
        return {
            "name": module_name,
            "succeeded": True,
            "version": version,
            "module": module,
        }
    except ImportError:
        return {"name": module_name, "succeeded": False}


def format_dependency_msg(
    result: dict[str, Any],
    msg: str,
    optional: bool = False,
) -> str:
    if result["succeeded"]:
        version = result.get("version", "unknown")
        return f"[OK] {result['name']} ({version}) - {msg} ready"
    if optional:
        return (
            f"[OPTIONAL] {result['name']} - {msg} unavailable "
            "(using built-in sample data)"
        )
    return f"[MISSING] {result['name']} - {msg} unavailable"


def sample_matrix_population() -> list[dict[str, Any]]:
    return SAMPLE_MATRIX_DATA.copy()


def fetch_matrix_population(
    requests_module: Any,
) -> list[dict[str, Any]]:

    response = requests_module.get(
        API_URL,
        params={"results": POPULATION_SIZE},
        timeout=20,
    )
    response.raise_for_status()
    payload: dict[str, Any] = response.json()
    return payload["results"]


def load_population_data(
    requests_module: Any | None,
) -> tuple[list[dict[str, Any]], str]:
    if requests_module is None:
        return sample_matrix_population(), "Using built-in sample data."
    try:
        data = fetch_matrix_population(requests_module)
        return (
            data,
            "Fetching Matrix population data from API...",
        )
    except requests_module.RequestException:
        return (
            sample_matrix_population(),
            "API fetch failed. Using built-in sample data.",
        )


def build_dataframe(
    raw_data: list[dict[str, Any]],
) -> Any:
    import pandas as pd

    records: list[dict[str, Any]] = []
    for entry in raw_data:
        records.append(
            {
                "age": entry["dob"]["age"],
                "gender": entry["gender"],
                "country": entry["location"]["country"],
            }
        )
    return pd.DataFrame(records)


def compute_age_stats(
    data_frame: Any,
) -> dict[str, float]:
    import numpy as np

    ages = data_frame["age"].to_numpy()
    return {
        "average_age": float(np.mean(ages)),
        "youngest_age": float(np.min(ages)),
        "oldest_age": float(np.max(ages)),
        "age_std_dev": float(np.std(ages)),
    }


def create_visualization(data_frame: Any) -> None:
    import matplotlib

    matplotlib.use("Agg")
    pyplot = importlib.import_module("matplotlib.pyplot")

    figure = pyplot.figure(figsize=(10, 6))
    axis = figure.add_subplot(1, 1, 1)

    axis.hist(data_frame["age"], bins=20, edgecolor="black")
    axis.set_title("Matrix Population Scan - Age Distribution")
    axis.set_xlabel("Age")
    axis.set_ylabel("Count")
    axis.grid(True, alpha=0.3)

    figure.tight_layout()
    figure.savefig(OUTPUT_IMAGE)
    pyplot.close(figure)


def main() -> None:
    print("\nLOADING STATUS: Loading programs...")

    print("\nChecking dependencies:")
    required_modules: list[tuple[str, str]] = [
        ("pandas", "Data manipulation"),
        ("matplotlib", "Visualization"),
        ("numpy", "numerical computations"),
    ]
    optional_modules: list[tuple[str, str]] = [
        ("requests", "Network access"),
    ]
    missing_modules: list[str] = []
    optional_results: dict[str, dict[str, Any]] = {}

    for name, msg in required_modules:
        result = check_dependency(name)
        if not result["succeeded"]:
            missing_modules.append(name)
        print(format_dependency_msg(result, msg))

    for name, msg in optional_modules:
        result = check_dependency(name)
        optional_results[name] = result
        print(format_dependency_msg(result, msg, optional=True))

    if missing_modules:
        print(f"""
[ERROR] Required dependency \
{",".join(missing_modules)} is not installed.
Install dependencies with one of the following:
- pip install -r requirements.txt
- poetry install
              """)
        sys.exit(1)

    requests_result = optional_results["requests"]
    requests_module = (
        requests_result.get("module") if requests_result["succeeded"] else None
    )

    try:
        print("\nAnalyzing Matrix data...")
        raw_data, data_source_msg = load_population_data(requests_module)
        print(data_source_msg)
        print(f"Processing {len(raw_data)} data points...")
        data_frame = build_dataframe(raw_data)
        stats = compute_age_stats(data_frame)

        print(f"Average age: {stats['average_age']:.2f}")
        print(f"Youngest age: {int(stats['youngest_age'])}")
        print(f"Oldest age: {int(stats['oldest_age'])}")
        print(f"Age standard deviation: {stats['age_std_dev']:.2f}")
        print()

        print("Generating visualization...")
        create_visualization(data_frame)

        print("Analysis complete!")
        print(f"Results saved to: {OUTPUT_IMAGE}")
    except Exception as exc:
        print(f"[ERROR] Unexpected failure: {exc}")


if __name__ == "__main__":
    main()
