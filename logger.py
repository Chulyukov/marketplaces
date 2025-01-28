# Формируем путь относительно текущего файла
import logging
import os

log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs/error_page.log")

# Настройка логирования
log_formatter = logging.Formatter(
    "\n%(asctime)s - %(levelname)s - %(message)s => %(exc_info)s"
)

# Создаём обработчик для записи в файл
file_handler = RotatingFileHandler(log_file_path, maxBytes=10 * 1024 * 1024, backupCount=5)
file_handler.setLevel(logging.ERROR)
file_handler.setFormatter(log_formatter)

# Настройка основного логгера
logger = logging.getLogger()
logger.setLevel(logging.INFO)  # Логируем только ERROR и выше
logger.addHandler(file_handler)