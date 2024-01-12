from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    github_username: Optional[str] = None
    github_token: Optional[str] = None
    perform_io_checks: bool = True
    set_undefined_field_descriptions_from_var_docstrings: bool = False

    @property
    def github_auth(self):
        if self.github_username is None or self.github_token is None:
            return None
        else:
            return (self.github_username, self.github_token)


settings = Settings(_env_prefix="BIOIMAGEIO_", _env_file=".env", _env_file_encoding="utf-8", _secrets_dir="/var/run")
