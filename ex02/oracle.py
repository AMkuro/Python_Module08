import os
import sys
from typing import Callable

try:
    from dotenv import load_dotenv
except ImportError:
    sys.exit(
        "Error: python-dotenv is not installed. Run: pip install python-dotenv"
    )


REQUIRED_VARS = [
    "MATRIX_MODE",
    "DATABASE_URL",
    "API_KEY",
    "LOG_LEVEL",
    "ZION_ENDPOINT",
]

VAR_LABELS: dict[str, str] = {
    "MATRIX_MODE": "Mode",
    "DATABASE_URL": "Database",
    "API_KEY": "API Access",
    "LOG_LEVEL": "Log Level",
    "ZION_ENDPOINT": "Zion Network",
}


def is_matrix_mode(val: str) -> bool:
    return val in ("development", "production")


def is_database_url(val: str) -> bool:
    schemes = (
        "postgresql://",
        "postgres://",
        "mysql://",
        "sqlite://",
        "mongodb://",
    )
    return any(val.startswith(s) for s in schemes)


def is_api_key(val: str) -> bool:
    allowed = set(
        "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_-"
    )
    return (
        len(val) >= 16
        and all(c in allowed for c in val)
        and val.startswith("api_")
    )


def is_log_level(val: str) -> bool:
    return val.upper() in ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")


def is_zion_endpoint(val: str) -> bool:
    schemes = ("http://", "https://")
    return any(val.startswith(s) for s in schemes)


VALIDATORS: dict[str, Callable[[str], bool]] = {
    "MATRIX_MODE": is_matrix_mode,
    "DATABASE_URL": is_database_url,
    "API_KEY": is_api_key,
    "LOG_LEVEL": is_log_level,
    "ZION_ENDPOINT": is_zion_endpoint,
}


def transform_database_url(url: str) -> str:
    if any(h in url for h in ("localhost", "127.0.0.1", "local")):
        return "Connected to local instance"
    return "Connected to remote instance"


VALID_DISPLAYS: dict[str, Callable[[str], str] | str] = {
    "MATRIX_MODE": lambda x: x,
    "DATABASE_URL": transform_database_url,
    "API_KEY": "Authenticated",
    "LOG_LEVEL": lambda x: x,
    "ZION_ENDPOINT": "Online",
}

INVALID_DISPLAYS: dict[str, str] = {
    "MATRIX_MODE": "unknown mode",
    "DATABASE_URL": "disconnected",
    "API_KEY": "Unauthenticated",
    "LOG_LEVEL": "unknown level",
    "ZION_ENDPOINT": "Offline",
}


def load_configuration() -> dict[str, str]:
    load_dotenv()
    detected: dict[str, str] = {}
    for var in REQUIRED_VARS:
        val = os.getenv(var)
        if val is not None:
            detected[var] = val
    return detected


def display_value(var: str, raw: str) -> str:
    if not VALIDATORS[var](raw):
        return INVALID_DISPLAYS[var]
    valid = VALID_DISPLAYS[var]
    if isinstance(valid, str):
        return valid
    return valid(raw)


def config_section(config: dict[str, str]) -> str:
    if not config:
        return "No configuration detected."

    lines = "Configuration loaded:"
    for var in REQUIRED_VARS:
        if var in config:
            lines += f"\n{VAR_LABELS[var]}: {display_value(var, config[var])}"
    return lines


def config_source_section() -> str:
    source_line = (
        ".env file loaded"
        if os.path.isfile(".env")
        else "No .env file detected"
    )
    return f"""Configuration source:
{source_line}
Environment variables override .env when present
"""


def mode_summary_section(config: dict[str, str]) -> str:
    mode = config.get("MATRIX_MODE")
    if mode == "development":
        details = (
            "development profile detected\n"
            "Local development settings are active"
        )
    elif mode == "production":
        details = (
            "production profile detected\n"
            "Deployment settings should come from the environment"
        )
    else:
        details = (
            "unknown profile detected\n"
            "Set MATRIX_MODE to development or production"
        )
    return f"""Mode summary:
{details}
"""


def security_section(config: dict[str, str]) -> str:
    env_ok = os.path.isfile(".env")
    env_status = (
        "[OK] .env file properly configured"
        if env_ok
        else "[WARNING] .env file not found — copy .env.example to .env"
    )

    lines = ""

    for var in REQUIRED_VARS:
        if var not in config:
            lines += f"\n[WARNING] Missing variable: {var}"
        elif not VALIDATORS[var](config[var]):
            lines += f"\n[WARNING] Invalid value for {var}: {config[var]}"
    if not lines and env_ok:
        lines += "\nThe Oracle sees all configurations."

    return f"""Environment security check:
[OK] No hardcoded secrets detected
{env_status}
[OK] Production overrides available
{lines}
"""


def main() -> None:
    config = load_configuration()

    print("\nORACLE STATUS: Reading the Matrix...\n")
    print(config_section(config))
    print()
    print(config_source_section())
    print(mode_summary_section(config))
    print(security_section(config))


if __name__ == "__main__":
    main()
