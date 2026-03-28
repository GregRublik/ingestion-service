from pydantic_settings import BaseSettings, SettingsConfigDict

class AWSSettings(BaseSettings):
    endpoint: str
    access_key: str
    secret_key: str
    bucket_name: str

    model_config = SettingsConfigDict(env_file=".env", env_prefix="AWS_", extra="ignore")

class QueueSettings(BaseSettings):
    embedding_document: str

    model_config = SettingsConfigDict(env_file=".env", env_prefix="QUEUE_", extra="ignore")


class RabbitSettings(BaseSettings):
    user: str
    password: str
    host: str
    port: int

    queues: QueueSettings

    @property
    def url(self) -> str:
        return f"amqp://{self.user}:{self.password}@{self.host}:{self.port}/"

    model_config = SettingsConfigDict(env_file=".env", env_prefix="RABBITMQ_", extra="ignore")

class DbSettings(BaseSettings):
    host: str
    user: str
    password: str
    name: str
    port: int

    model_config = SettingsConfigDict(env_prefix="DB_", env_file=".env", extra="ignore")

    @property
    def dsn_asyncpg(self):
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"


class Settings(BaseSettings):
    port: int
    host: str

    db: DbSettings
    aws: AWSSettings
    rabbitmq: RabbitSettings

    model_config = SettingsConfigDict(env_file=".env", env_prefix="APP_", extra="ignore")

settings = Settings(
    db=DbSettings(),
    rabbitmq=RabbitSettings(),
    aws=AWSSettings(),
)
