from pydantic_settings import BaseSettings, SettingsConfigDict


from pydantic import BaseModel


class UploadConfig(BaseModel):
    dowloand_dir: str = "data"


class BotConfig(BaseModel):
    token: str


class DatabaseConfig(BaseModel):
    url: str
    echo: bool = False
    echo_pool: bool = False
    max_overflow: int = 10
    pool_size: int = 50

    naming_convention: dict[str, str] = {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_N_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }


class AppConfig(BaseSettings):
    db: DatabaseConfig
    bot: BotConfig
    upload: UploadConfig = UploadConfig()
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        env_nested_delimiter="__",
        env_prefix="APP_CONFIG__",
    )


conf = AppConfig()
