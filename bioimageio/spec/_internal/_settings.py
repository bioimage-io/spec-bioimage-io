from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="BIOIMAGEIO_", env_file=".env", env_file_encoding="utf-8"
    )

    github_username: Optional[str] = None
    github_token: Optional[str] = None
    perform_io_checks: bool = True

    @property
    def github_auth(self):
        if self.github_username is None or self.github_token is None:
            return None
        else:
            return (self.github_username, self.github_token)


settings = Settings()
