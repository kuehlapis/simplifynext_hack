import os
from dotenv import load_dotenv
from pydantic import SecretStr
from functools import lru_cache

load_dotenv()


class Config:
    GEMINI_API_KEY: SecretStr = SecretStr(os.getenv("GEMINI_API_KEY", ""))

    @classmethod
    def validate_config(cls) -> None:
        required_secrets = {
            "GEMINI_API_KEY": cls.GEMINI_API_KEY.get_secret_value(),
        }

        missing_secrets = [
            var_name
            for var_name, var_value in required_secrets.items()
            if not var_value or var_value == "<secret_here>"
        ]

        if missing_secrets:
            raise ValueError(
                f"Missing required secret environment variables: {', '.join(missing_secrets)}. "
                f"Please check your .env file."
            )

    @classmethod
    def get_gemini_api(cls) -> str:
        return cls.GEMINI_API_KEY.get_secret_value()


@lru_cache(maxsize=1)
def getConfig() -> Config:
    config = Config()
    config.validate_config()
    return config
