from dataclasses import dataclass
from typing import Optional

from environs import Env


@dataclass
class DbConfig:
    host: str
    password: str
    user: str
    database: str
    port: int = 5432

    @staticmethod
    def from_env(env: Env):
        host = env.str("DB_HOST")
        password = env.str("POSTGRES_PASSWORD")
        user = env.str("POSTGRES_USER")
        database = env.str("POSTGRES_DB")
        port = env.int("DB_PORT", 5432)
        return DbConfig(
            host=host, password=password, user=user, database=database, port=port
        )


@dataclass
class DjangoIp:
    ip: str

    @staticmethod
    def from_env(env: Env):
        ip = env.str("IP")
        return DjangoIp(
            ip=ip
        )


@dataclass
class TgBot:
    token: str
    admin_ids: list[int]
    use_redis: bool
    yookassa_id: int
    yookassa_key: str
    price: int

    @staticmethod
    def from_env(env: Env):
        token = env.str("BOT_TOKEN")
        admin_ids = env.list("ADMINS", subcast=int)
        use_redis = env.bool("USE_REDIS")
        yookassa_id = env.int("YOOKASSA_ACCOUNT_ID")
        yookassa_key = env.str("YOOKASSA_SECRET_KEY")
        price = env.int("price")
        return TgBot(token=token, admin_ids=admin_ids, use_redis=use_redis, yookassa_id=yookassa_id, yookassa_key=yookassa_key, price=price)


@dataclass
class RedisConfig:
    redis_pass: Optional[str]
    redis_port: Optional[int]
    redis_host: Optional[str]

    def dsn(self) -> str:
        if self.redis_pass:
            return f"redis://:{self.redis_pass}@{self.redis_host}:{self.redis_port}/0"
        else:
            return f"redis://{self.redis_host}:{self.redis_port}/0"

    @staticmethod
    def from_env(env: Env):

        redis_pass = env.str("REDIS_PASSWORD")
        redis_port = env.int("REDIS_PORT")
        redis_host = env.str("REDIS_HOST")

        return RedisConfig(
            redis_pass=redis_pass, redis_port=redis_port, redis_host=redis_host
        )


@dataclass
class Miscellaneous:
    path_media: str

    @staticmethod
    def from_env(env: Env):
        return Miscellaneous(
            path_media=env.str("path_media")
        )


@dataclass
class Config:
    tg_bot: TgBot
    misc: Miscellaneous
    db: Optional[DbConfig] = None
    django_ip: Optional[DjangoIp] = None
    redis: Optional[RedisConfig] = None


def load_config(path: str = None) -> Config:
    env = Env()
    env.read_env(path)
    return Config(
        tg_bot=TgBot.from_env(env),
        db=DbConfig.from_env(env),
        redis=RedisConfig.from_env(env),
        misc=Miscellaneous.from_env(env),
    )


config = load_config(".env")
