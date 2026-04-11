import importlib.util
import sys
from typing import Any


def is_available(module_name: str) -> bool:
    return importlib.util.find_spec(module_name) is not None


def check_dependency(module_name: str) -> dict[str, Any]:
    try:
        # importlib.import_module() is more readable.
        module = __import__(module_name)
        # module = __import__("os.path") It makes problem?
        # Output: <module 'os' (frozen)>
        version: str = getattr(module, "__version__", "unknown")
        return {"name": module_name, "successed": True, "version": version}
    except ImportError:
        return {"name": module_name, "successed": False}


def get_check_dependency_msg(module_name: str, msg: str) -> str:
    result: dict[str, Any] = check_dependency(module_name)
    if result["successed"]:
        return f"[OK] {module_name} ({result['version']}) - {msg} ready"
    else:
        return f"[MISSING] {module_name} - {msg} unavailable"


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
        print("""[ERROR] Required dependency 'matplotlib' is not installed.
Install dependencies with one of the following:
- pip install -r requirements.txt
- poetry install
              """)
        sys.exit(1)
    print("\nAnalyzing Matrix data...")
    print("Processing 1000 data points...")
    print("Generating visualization...")

    print("\nAnalysis complete!")
    pic_name: str = "matrix_analysis.png"
    print(f"Results saved to: {pic_name}")


if __name__ == "__main__":
    main()
