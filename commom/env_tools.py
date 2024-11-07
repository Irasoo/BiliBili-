import os
from dotenv import load_dotenv


def get_env_var(var_name: str) -> str:
    load_dotenv()
    target_var = os.getenv(var_name)
    if target_var is None:
        raise ValueError(f"environment variable '{var_name}' is not set")
    return target_var

