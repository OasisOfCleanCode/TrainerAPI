# app/core/config.py

"""
📦 Конфигурация проекта: зачем и как всё устроено

✅ Почему используется `pydantic_settings.BaseSettings`?
---------------------------------------------------------
- Все переменные окружения строго типизированы и валидируются.
- .env-файл подключается автоматически (через Config).
- Удобно работать с разными окружениями: dev, prod, test.
- Ошибки конфигурации ловятся сразу при старте проекта.

✅ Зачем нужны lazy-обёртки с `@lru_cache`?
------------------------------------------
- Настройки и .env загружаются один раз — никакой лишней работы.
- Нет глобальных переменных — вызов в любом месте через `get_*_settings()`.
- Устойчиво к циклическим импортам.
- Легко протестировать или подменить конфиг.

📚 Где какой конфиг и зачем он нужен?
--------------------------------------

🔹 `AppMetaSettings`
    - Общие параметры приложения.
    - `APP_MODE`: текущий режим работы (dev/prod/test).
    - `VERSION_TAG`: версия API или проекта.

🔹 `UrlSetting`
    - Настройки базового домена и CORS.
    - `DOMAIN_URL`: основной URL сервиса.
    - `CORS_ALLOWED_ORIGINS`: список доменов, откуда разрешены запросы.

🔹 `ApiTokens`
    - Ключи и алгоритм для подписи JWT.
    - `TAPI_TOKEN_ACCESS_SECRET_KEY`: секрет для access-токена.
    - `TAPI_TOKEN_REFRESH_SECRET_KEY`: секрет для refresh-токена.
    - `ALGORITHM`: алгоритм шифрования токенов.

🔹 `TelegramBotSetting`
    - Настройки телеграм-бота для логов/оповещений.
    - `TELEGRAM_TOKEN_FOR_SEND_TELEBOT`: токен бота.
    - `CHAT_ID_FOR_SEND`: чат или канал, куда писать.

🔹 `PstgrDataBaseSettings`
    - Настройки PostgreSQL.
    - `TAPI_PSTGR_USER`: пользователь.
    - `TAPI_PSTGR_PASS`: пароль.
    - `TAPI_PSTGR_HOST`: хост базы.
    - `TAPI_PSTGR_PORT`: порт подключения.
    - `TAPI_PSTGR_NAME`: имя базы.
    - `async_tapi_pstgr_url`: DSN для async-соединения (asyncpg).
    - `sync_tapi_pstgr_url`: DSN для sync-соединения.

🔹 `RabbitMqSetting`
    - Настройки очередей RabbitMQ.
    - `TAPI_RABBITMQ_USER`, `PASS`, `HOST`, `PORT`.
    - `tapi_rabbitmq_broker_url`: готовый amqp:// URL.

🔹 `RedisMqSetting`
    - Подключение к Redis (брокер + кэш/баны).
    - `TAPI_REDIS_HOST`, `PORT`, `PASS`.
    - `TAPI_REDIS_BAN_LIST_INDEX`: индекс DB для банов.
    - `TAPI_REDIS_BROKER_INDEX`: индекс DB для брокера.
    - `tapi_redis_ban_list_url`: redis:// URL для банов.
    - `tapi_redis_broker_url`: redis:// URL для брокера.

🔹 `S3StorageConfig`
    - S3/MinIO-хранилище.
    - `TAPI_MINIO_USER`, `PASS`, `HOST`, `PORT`, `BASKET_NAME`.
    - `BASE_PHOTO_PATH`: локальная папка с фото.
    - `photo_path`: getter с автосозданием директории при доступе.

🔹 `MailSenderConfig`
    - SMTP-параметры.
    - `TAPI_MAIL_USERNAME`, `PASSWORD`, `SERVER`, `PORT`.

🔹 `UrlsToServices`
    - URL-ы к другим микросервисам или сторонним API.
    - `BASE_URL`: главный сайт.
    - `BASE_USER_URL`: сайт пользователей.
    - `BASE_USER_API_URL`: API пользователей.

🧠 Использование (в любом месте проекта):
-----------------------------------------
    from app.core.config import get_db_settings
    db = get_db_settings().async_tapi_pstgr_url
"""

# ================================
# 📁 Импорты и базовая инициализация
# ================================
from enum import Enum  # Перечисления для mode
from pathlib import Path  # Работа с путями
from functools import lru_cache  # Кэшируем вызовы
from dotenv import load_dotenv  # Загрузка .env
from pydantic_settings import BaseSettings  # Настройки через Pydantic

# 📍 Базовая директория проекта
BASE_PATH = Path(__file__).resolve().parent.parent.parent



# 🔄 Режимы приложения
class ModeEnum(str, Enum):
    development = "development"
    production = "production"
    testing = "testing"


# 🛠️ Базовый класс всех настроек
class Settings(BaseSettings):
    class Config:
        env_file = BASE_PATH / ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # игнорировать лишние переменные


# ===============================
# 🔧 Конкретные классы настроек
# ===============================


class AppMetaSettings(Settings):
    APP_MODE: ModeEnum = ModeEnum.development
    VERSION_TAG: str = "v1.0.0"


class UrlSetting(Settings):
    DOMAIN_URL: str
    CORS_ALLOWED_ORIGINS: list[str] = []


class TelegramBotSetting(Settings):
    TELEGRAM_TOKEN_FOR_SEND_TELEBOT: str
    CHAT_ID_FOR_SEND: int


class ApiTokens(Settings):
    TAPI_TOKEN_ACCESS_SECRET_KEY: str
    TAPI_TOKEN_REFRESH_SECRET_KEY: str
    ALGORITHM: str = "HS256"


class PstgrDataBaseSettings(Settings):
    TAPI_PSTGR_USER: str
    TAPI_PSTGR_PASS: str
    TAPI_PSTGR_NAME: str
    TAPI_PSTGR_HOST: str
    TAPI_PSTGR_PORT: str

    @property
    def async_tapi_pstgr_url(self) -> str:
        return f"postgresql+asyncpg://{self.TAPI_PSTGR_USER}:{self.TAPI_PSTGR_PASS}@{self.TAPI_PSTGR_HOST}:{self.TAPI_PSTGR_PORT}/{self.TAPI_PSTGR_NAME}"

    @property
    def sync_tapi_pstgr_url(self) -> str:
        return f"postgresql://{self.TAPI_PSTGR_USER}:{self.TAPI_PSTGR_PASS}@{self.TAPI_PSTGR_HOST}:{self.TAPI_PSTGR_PORT}/{self.TAPI_PSTGR_NAME}"


class RabbitMqSetting(Settings):
    TAPI_RABBITMQ_USER: str
    TAPI_RABBITMQ_PASS: str
    TAPI_RABBITMQ_HOST: str
    TAPI_RABBITMQ_PORT: str

    @property
    def tapi_rabbitmq_broker_url(self) -> str:
        return f"amqp://{self.TAPI_RABBITMQ_USER}:{self.TAPI_RABBITMQ_PASS}@{self.TAPI_RABBITMQ_HOST}:{self.TAPI_RABBITMQ_PORT}/"


class RedisMqSetting(Settings):
    TAPI_REDIS_HOST: str
    TAPI_REDIS_PORT: str
    TAPI_REDIS_PASS: str
    TAPI_REDIS_BAN_LIST_INDEX: int = 0
    TAPI_REDIS_BROKER_INDEX: int = 1

    @property
    def tapi_redis_ban_list_url(self) -> str:
        return f"redis://:{self.TAPI_REDIS_PASS}@{self.TAPI_REDIS_HOST}:{self.TAPI_REDIS_PORT}/{self.TAPI_REDIS_BAN_LIST_INDEX}"

    @property
    def tapi_redis_broker_url(self) -> str:
        return f"redis://:{self.TAPI_REDIS_PASS}@{self.TAPI_REDIS_HOST}:{self.TAPI_REDIS_PORT}/{self.TAPI_REDIS_BROKER_INDEX}"


class S3StorageConfig(Settings):
    TAPI_MINIO_USER: str
    TAPI_MINIO_PASS: str
    TAPI_MINIO_HOST: str
    TAPI_MINIO_PORT: int
    TAPI_MINIO_USER_BASKET_NAME: str

    # 📁 Временное решение: локальный путь для хранения фотографий
    BASE_PHOTO_PATH: Path = BASE_PATH / "imgs"

    # 📌 Есть два варианта автоматического создания директории:
    # 1. Через __init__ — создаётся один раз при инициализации настроек (предпочтительно)
    # 2. Через геттер — создаётся при каждом обращении к свойству (резервный способ)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.BASE_PHOTO_PATH.mkdir(parents=True, exist_ok=True)

    @property
    def photo_path(self) -> Path:
        self.BASE_PHOTO_PATH.mkdir(parents=True, exist_ok=True)
        return self.BASE_PHOTO_PATH


class MailSenderConfig(Settings):
    TAPI_MAIL_USERNAME: str
    TAPI_MAIL_PASSWORD: str
    TAPI_MAIL_SERVER: str
    TAPI_MAIL_PORT: int


class UrlsToServices(Settings):
    BASE_URL: str = "https://occ.dev/"
    BASE_USER_URL: str = "https://id.occ.dev/"
    BASE_USER_API_URL: str = "https://id.api.occ.dev/"


class SuperUsersConfig(Settings):
    ADMIN: str


# ================================
# 🧠 Lazy-обёртки для импорта
# ================================


@lru_cache()
def get_app_settings() -> AppMetaSettings:
    return AppMetaSettings()


@lru_cache()
def get_url_settings() -> UrlSetting:
    return UrlSetting()


@lru_cache()
def get_api_tokens() -> ApiTokens:
    return ApiTokens()


@lru_cache()
def get_db_settings() -> PstgrDataBaseSettings:
    return PstgrDataBaseSettings()


@lru_cache()
def get_rabbitmq_settings() -> RabbitMqSetting:
    return RabbitMqSetting()


@lru_cache()
def get_redis_settings() -> RedisMqSetting:
    return RedisMqSetting()


@lru_cache()
def get_telegram_settings() -> TelegramBotSetting:
    return TelegramBotSetting()


@lru_cache()
def get_mail_sender_config() -> MailSenderConfig:
    return MailSenderConfig()


@lru_cache()
def get_urls_to_services() -> UrlsToServices:
    return UrlsToServices()


@lru_cache()
def get_s3_storage_config() -> S3StorageConfig:
    return S3StorageConfig()
