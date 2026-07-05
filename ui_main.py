from PyQt5 import QtCore, QtGui, QtWidgets
import logging

logger = logging.getLogger(__name__)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Архив настольных игр")
        self.resize(1350, 870)
        self.setMinimumSize(QtCore.QSize(1350, 870))
        self.setStyleSheet("background-color: rgb(234, 239, 255);\n"
"font: 9pt \"Myanmar Text\";\n"
"")
        self._setup_ui()
        self._bind_signals()

        logger.info("Главное окно инициализировано")

    def _setup_ui(self):
        """Настройка интерфейса"""
        self.central_widget = QtWidgets.QWidget()
        self.main_layout = QtWidgets.QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Левая часть (коллекция)
        self.lbl_collection = QtWidgets.QLabel("Коллекция")
        self.lbl_collection.setStyleSheet("font: 63 20pt \"Yu Gothic UI Semibold\";")
        
        self.lbl_filter = QtWidgets.QLabel("Фильтр по количеству игроков:")
        self.sb_filter = QtWidgets.QSpinBox(self.central_widget)
        self.sb_filter.setRange(1, 20)
        self.sb_filter.setValue(1)
        self.btn_clean_filter = QtWidgets.QPushButton("Сбросить фильтр")
        self.btn_clean_filter.setStyleSheet("background-color: rgb(170, 255, 255);")
        self.btn_delete = QtWidgets.QPushButton("Удалить игру")
        self.btn_delete.setStyleSheet("background-color: rgb(255, 170, 127);")

        self.left_btn_layout = QtWidgets.QHBoxLayout()
        self.left_btn_layout.addWidget(self.lbl_filter)
        self.left_btn_layout.addWidget(self.sb_filter)
        self.left_btn_layout.addWidget(self.btn_clean_filter)
        self.left_btn_layout.addWidget(self.btn_delete)

        self.left_btn_layout.setStretch(0, 1)
        self.left_btn_layout.setStretch(2, 1)
        self.left_btn_layout.setStretch(3, 1)
        
        self.scroll_area = QtWidgets.QScrollArea(self.central_widget)
        self.scroll_area.setWidgetResizable(True)
        
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollContentLayout = QtWidgets.QGridLayout(self.scrollAreaWidgetContents)
        self.scrollContentLayout.setContentsMargins(0, 0, 0, 0)
        
        # # Здесь будут добавляться карточки игр динамически
        # self.empty_widget = QtWidgets.QWidget(self.scrollAreaWidgetContents)

        # self.scrollContentLayout.addWidget(self.empty_widget)
        
        self.scroll_area.setWidget(self.scrollAreaWidgetContents)

        self.left_layout = QtWidgets.QVBoxLayout()
        self.left_layout.addWidget(self.lbl_collection)
        self.left_layout.addLayout(self.left_btn_layout)
        self.left_layout.addWidget(self.scroll_area)
        self.left_layout.setStretch(2, 1)
        
        self.main_layout.addLayout(self.left_layout)
        
        # Правая часть (карточка игры)
        self.right_layout = QtWidgets.QVBoxLayout()
        
        self.game = QtWidgets.QLabel("Игра")
        self.game.setStyleSheet("font: 63 20pt \"Yu Gothic UI Semibold\";")
        self.right_layout.addWidget(self.game)
        
        self.frame = QtWidgets.QFrame(self.central_widget)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        
        self.frame_layout = QtWidgets.QVBoxLayout(self.frame)
        self.frame_layout.setContentsMargins(10, 10, 10, 10)
        
        self.verticalLayoutWidget = QtWidgets.QWidget(self.frame)
        self.card_layout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.card_layout.setContentsMargins(0, 0, 0, 0)
        
        self.lbl_img = QtWidgets.QLabel("Нет фото")
        self.lbl_img.setAlignment(QtCore.Qt.AlignCenter)
        self.lbl_img.setMinimumHeight(200)
        self.lbl_img.setMaximumHeight(300)
        self.lbl_img.setScaledContents(True)
        self.lbl_img.setStyleSheet("background-color: #f0f0f0; border-radius: 8px;")
        self.card_layout.addWidget(self.lbl_img)
        
        self.le_name = QtWidgets.QLineEdit(self.verticalLayoutWidget)
        self.sb_count = QtWidgets.QSpinBox(self.verticalLayoutWidget)  
        self.sb_count.setRange(1, 20)       
        self.sb_count.setValue(2)      
        self.time_edit = QtWidgets.QTimeEdit(self.verticalLayoutWidget)
        self.time_edit.setDisplayFormat("hh:mm")
        self.time_edit.setTime(QtCore.QTime(0, 30)) 
        self.time_edit.setWrapping(False)  # Не перематывать время
        self.time_edit.setToolTip("Введите время партии в формате ЧЧ:ММ")
      
        self.lbl_name = QtWidgets.QLabel("Название:")
        self.lbl_difficulty = QtWidgets.QLabel("Сложность:")
        self.lbl_count = QtWidgets.QLabel("Минимум игроков:")
        self.lbl_time = QtWidgets.QLabel("Время партии:")
    
        self.cb_difficulty = QtWidgets.QComboBox(self.verticalLayoutWidget)
        self.cb_difficulty.addItems(["Легкая", "Средняя", "Сложная"])
        self.right_char_layout = QtWidgets.QGridLayout()
        self.right_char_layout.addWidget(self.sb_count, 1, 1, 1, 1)
        self.right_char_layout.addWidget(self.le_name, 0, 1, 1, 1)
        self.right_char_layout.addWidget(self.time_edit, 2, 1, 1, 1)
        self.right_char_layout.addWidget(self.lbl_name, 0, 0, 1, 1)
        self.right_char_layout.addWidget(self.lbl_difficulty, 3, 0, 1, 1)
        self.right_char_layout.addWidget(self.lbl_count, 1, 0, 1, 1)
        self.right_char_layout.addWidget(self.lbl_time, 2, 0, 1, 1)
        self.right_char_layout.addWidget(self.cb_difficulty, 3, 1, 1, 1)
        self.card_layout.addLayout(self.right_char_layout)
        
        self.btn_load_img = QtWidgets.QPushButton("Загрузить фото")
        self.btn_load_img.setStyleSheet("background-color: rgb(255, 170, 255);")
        self.btn_delete_img = QtWidgets.QPushButton("Удалить фото")
        self.btn_delete_img.setStyleSheet("background-color: rgb(255, 170, 255);")
    
        self.btn_add = QtWidgets.QPushButton("Добавить игру")
        self.btn_add.setStyleSheet("background-color: rgb(85, 170, 255);")
        
        self.card_layout.addWidget(self.btn_load_img)
        self.card_layout.addWidget(self.btn_delete_img)
        self.card_layout.addWidget(self.btn_add)
        
        self.frame_layout.addWidget(self.verticalLayoutWidget)
        
        self.right_layout.addWidget(self.frame)
        self.right_layout.setStretch(1, 1)
        
        self.main_layout.addLayout(self.right_layout)
        self.main_layout.setStretch(0, 2)
        self.main_layout.setStretch(1, 1)
        
        self.setCentralWidget(self.central_widget)

    def _bind_signals(self):
        """Отслеживание сигналов"""
        self.sb_filter.valueChanged.connect(self._apply_filter)
        self.btn_clean_filter.clicked.connect(self._clean_filter)
        self.btn_delete.clicked.connect(self._delete_game)
        self.btn_load_img.clicked.connect(self._load_img)
        self.btn_delete_img.clicked.connect(self._delete_img)
        self.btn_add.clicked.connect(self._add_game)

    def _apply_filter(self):
        """Применение фильтра"""
        min_players = self.sb_filter.value()
        print("Минимум", min_players)

    def _clean_filter(self):
        """Сброс фильтра"""
        print("фильтр сброшен")

    def _delete_game(self):
        """Удаление игры"""
        print("Игра удалена")

    def _load_img(self):
        """Загрузка изображения"""
        print("Изображение загружено")

    def _delete_img(self):
        """Удаление изображения"""
        print("Изображение удалено")

    def _add_game(self):
        """Сохранение игры"""
        print("Игра сохранена")


