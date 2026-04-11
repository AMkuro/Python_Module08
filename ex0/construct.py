import sys
import os
import site


def is_venv() -> bool:
    return sys.prefix != sys.base_prefix


def get_environment_info() -> dict[str, str]:
    package_paths: list[str] = site.getsitepackages()
    package_path: str = package_paths[0] if package_paths else "Unknown"

    return {
        "python": sys.executable,
        "env_path": sys.prefix,
        "env_name": os.path.basename(sys.prefix),
        "site_packages": package_path,
    }


def warning_msg() -> str:
    return """
WARNING: You're in the global environment!
The machines can see everything you install.
"""


def success_msg() -> str:
    return """
SUCCESS: You're in an isolated environment!
Safe to install packages without affecting the global system.
"""


def activation_instructions() -> str:
    return """To enter the construct, run:
python -m venv matrix_env
source matrix_env/bin/activate # On Unix
matrix_env\\Scripts\\activate # On Windows
"""


def main() -> None:
    print("\nMATRIX STATUS: ", end="")
    venv_flag: bool = is_venv()
    env_info: dict[str, str] = get_environment_info()
    if venv_flag:
        print("Welcome to the construct")
    else:
        print("You're still plugged in")
    print()

    print(f"Current Python: {env_info['python']}")
    print("Virtual Environment: ", end="")
    if venv_flag:
        env_path: str = env_info["env_path"]
        env_name: str = env_info["env_name"]
        print(env_name)
        print(f"Environment Path: {env_path}")
        print(success_msg())
        print("Package installation path:")
        print(env_info["site_packages"])
    else:
        print("None detected")
        print(warning_msg())
        print(activation_instructions())
        print("Then run this program again.")


if __name__ == "__main__":
    main()
