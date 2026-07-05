import sys
import logging
from PyQt5 import QtWidgets
from ui_main import MainWindow

# Настройка логирования
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def main():
    """Точка запуска"""
    try:
        app = QtWidgets.QApplication(sys.argv)
        window = MainWindow()
        window.show()
        logger.info("Приложение успешно запущено")
        sys.exit(app.exec_())
    except Exception as e:
        logger.error(f"Критическая ошибка при запуске: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()