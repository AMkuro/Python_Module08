import importlib.util
import sys
from typing import Any

OUTPUT_IMAGE: str = "matrix_analysis.png"
POPULATION_SIZE: int = 1000
API_URL: str = "https://randomuser.me/api/"


def is_available(module_name: str) -> bool:
    return importlib.util.find_spec(module_name) is not None


def check_dependency(module_name: str) -> dict[str, Any]:
    try:
        module = importlib.import_module(module_name)
        version: str = getattr(module, "__version__", "unknown")
        return {
            "name": module_name,
            "successed": True,
            "version": version,
            "module": module,
        }
    except ImportError:
        return {"name": module_name, "successed": False}


def get_check_dependency_msg(module_name: str, msg: str) -> str:
    result: dict[str, Any] = check_dependency(module_name)
    if result["successed"]:
        return f"[OK] {module_name} ({result['version']}) - {msg} ready"
    else:
        return f"[MISSING] {module_name} - {msg} unavailable"


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
    modules: list[tuple[str, str]] = [
        ("pandas", "Data manipulation"),
        ("requests", "Network access"),
        ("matplotlib", "Visualization"),
        ("numpy", "numerical computations"),
    ]
    missing_modules: list[str] = []
    for name, msg in modules:
        if not check_dependency(name)["successed"]:
            missing_modules.append(name)
        print(get_check_dependency_msg(name, msg))

    if missing_modules:
        print(f"""[ERROR] Required dependency \
{",".join(missing_modules)} is not installed.
Install dependencies with one of the following:
- pip install -r requirements.txt
- poetry install
              """)
        sys.exit(1)

    import requests

    try:
        print("\nFetching Matrix population data...")
        raw_data = fetch_matrix_population(__import__("requests"))
        print(f"Retrieved {len(raw_data)} records.")
        print()

        print("Analyzing Matrix data...")
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
    except requests.RequestException as exc:
        print(f"[ERROR] Failed to fetch Matrix population data: {exc}")
    except Exception as exc:
        print(f"[ERROR] Unexpected failure: {exc}")


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


if __name__ == "__main__":
    main()
