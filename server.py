import os
import logging
import sentry_sdk
from bottle import Bottle, HTTPResponse
from sentry_sdk.integrations.bottle import BottleIntegration
from sentry_sdk.integrations.logging import LoggingIntegration, ignore_logger

# Получаем адрес из переменной окружения (должна быть прописана в хероку), а если её нет, то из файла env.py
SENTRY_DSN = os.environ.get("SENTRY_DSN")
if not SENTRY_DSN:
    from env import SENTRY_DSN

# Настройка, позволяющая отправлять в Sentry не только ошибки, но и логи любого уровня.
# Выбран уровень INFO
sentry_logging = LoggingIntegration(
    level=logging.INFO,
    event_level=logging.INFO
)

sentry_sdk.init(dsn=SENTRY_DSN, integrations=[BottleIntegration(), sentry_logging])

# Игнорируем сообщения от gunicorn-овских логгеров
ignore_logger("gunicorn.error")
ignore_logger("gunicorn.access")

formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger("new_logger")
logger.setLevel(logging.DEBUG)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
stream_handler.setLevel(logging.DEBUG)

logger.addHandler(stream_handler)
app = Bottle()


@app.route("/")
def hello():
    return HTTPResponse(status="200 OK", body="Тут ничего нет")


@app.route("/success")
def index():
    logger.info('Выполнен вход по адресу "/success"')
    return HTTPResponse(status="200 OK", body="Здесь могла быть Ваша реклама")


@app.route("/warning")
def index():
    logger.warning('Попытка проникнуть на закрытую территорию')
    return HTTPResponse(status=403, body="Сюда нельзя!")


@app.route("/fail")
def generate_fails():
    raise RuntimeError("Ошибка.")


if os.environ.get("APP_LOCATION") == "heroku":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        server="gunicorn",
        workers=3,
    )
else:
    app.run(host="localhost", port=8080, debug=True)
