from PyQt5 import QtCore, QtGui, QtWidgets
import logging
import database
from PIL import Image

logger = logging.getLogger(__name__)


class GameCard(QtWidgets.QFrame):
    """Виджет карточки игры"""
    def __init__(self, game_data, parent=None):
        super().__init__(parent)
        self.game_data = game_data
        self.parent_window = parent
        self.setStyleSheet("background-color: #ffffff; font: 9pt 'Myanmar Text';")
        self.setup_ui()
        
    def setup_ui(self):
        """Настройка карточки"""
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Изображение
        self.image_label = QtWidgets.QLabel()
        self.image_label.setAlignment(QtCore.Qt.AlignCenter)
        self.image_label.setMinimumHeight(150)
        self.image_label.setMaximumHeight(200)
        self.image_label.setStyleSheet("background-color: #f0f0f0; border-radius: 8px;")
        self.image_label.setScaledContents(True)
        
        # Загрузка изображения
        if self.game_data['photo_path']:
            pixmap = QtGui.QPixmap(self.game_data['photo_path'])
            if not pixmap.isNull():
                self.image_label.setPixmap(pixmap.scaled(200, 200, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
            else:
                self.image_label.setText("Нет фото")
        else:
            self.image_label.setText("Нет фото")
        
        # Информация
        info_layout = QtWidgets.QVBoxLayout()

        name_label = QtWidgets.QLabel(self.game_data['name'])
        name_label.setStyleSheet("font: 75 14pt 'Myanmar Text';")
        name_label.setWordWrap(True)
        name_label.setAlignment(QtCore.Qt.AlignCenter)
        
        players_label = QtWidgets.QLabel(f"Кол-во игроков: {self.game_data['players']}+")
        
        minutes = self.game_data['time']
        hours = minutes // 60
        mins = minutes % 60
        if hours > 0:
            time = f"Время: {hours}ч {mins}мин"
        else:
            time = f"Время: {mins}мин"
        time_label = QtWidgets.QLabel(time)
        
        difficulty = self.game_data['difficulty']   
        diff_label = QtWidgets.QLabel(difficulty)

        # Кнопки управления карточкой
        self.btn_update = QtWidgets.QPushButton("Редактировать")
        self.btn_update.setStyleSheet("background-color: rgb(255, 170, 127);")
        self.btn_update.clicked.connect(self.on_update)

        self.btn_delete = QtWidgets.QPushButton("Удалить")
        self.btn_delete.setStyleSheet("background-color: rgb(255, 170, 127);")
        self.btn_delete.clicked.connect(self.on_delete)

        info_layout.addWidget(name_label)
        info_layout.addWidget(players_label)
        info_layout.addWidget(time_label)
        info_layout.addWidget(diff_label)
        
        layout.addWidget(self.image_label)
        layout.addLayout(info_layout)
        layout.addWidget(self.btn_update)
        layout.addWidget(self.btn_delete)
        
        self.setLayout(layout)

    def on_update(self):
        """Обработка редактирования"""
        if self.parent_window:
            self.parent_window.update_game(self.game_data)

    def on_delete(self):
        """Обработка удаления"""
        if self.parent_window:
            self.parent_window.delete_game(self.game_data['id'])


class MainWindow(QtWidgets.QMainWindow):
    """Главное окно"""
    def __init__(self):
        super().__init__()

        self.current_photo_path = None
        self.edit_id = None

        self.setWindowTitle("Архив настольных игр")
        self.resize(1300, 800)
        self.setMinimumSize(QtCore.QSize(1000, 800))
        self.setStyleSheet("background-color: rgb(234, 239, 255);font: 9pt \"Myanmar Text\";")
        # Инициализация БД
        self.db = database.DatabaseManager()
        if not self.db.init_db():
            QtWidgets.QMessageBox.critical(self, "Ошибка", "Не удалось инициализировать БД")
            self.close()
            return

        self._setup_ui()
        self._bind_signals()
        self._refresh_games()
        self._setup_keysequence()

        logger.info("Главное окно инициализировано")

    def _setup_ui(self):
        """Настройка интерфейса"""
        self.central_widget = QtWidgets.QWidget()
        self.main_layout = QtWidgets.QHBoxLayout(self.central_widget)
        self.main_layout.setSpacing(15)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Левая часть (коллекция)
        self.lbl_collection = QtWidgets.QLabel("Коллекция")
        self.lbl_collection.setStyleSheet("font: 63 20pt \"Yu Gothic UI Semibold\";")
        self.lbl_filter = QtWidgets.QLabel("Фильтр по минимуму игроков:")
        self.sb_filter = QtWidgets.QSpinBox(self.central_widget)
        self.sb_filter.setToolTip("Ctrl+F")
        self.sb_filter.setRange(1, 20)
        self.sb_filter.setValue(1)
        
        self.btn_clean_filter = QtWidgets.QPushButton("Сбросить фильтр")
        self.btn_clean_filter.setStyleSheet("background-color: light gray;")
        self.btn_clean_filter.setToolTip("Ctrl+N")
        self.left_btn_layout = QtWidgets.QHBoxLayout()
        self.left_btn_layout.addWidget(self.lbl_filter)
        self.left_btn_layout.addWidget(self.sb_filter)
        self.left_btn_layout.addWidget(self.btn_clean_filter)

        self.left_btn_layout.setStretch(0, 1)
        self.left_btn_layout.setStretch(2, 1)
        self.left_btn_layout.setStretch(3, 1)
        
        self.scroll_area = QtWidgets.QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        
        self.cards_container = QtWidgets.QWidget()
        self.cards_layout = QtWidgets.QGridLayout(self.cards_container)
        self.cards_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_area.setWidget(self.cards_container)

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
        self.btn_load_img.setToolTip("Ctrl+L")
        self.btn_delete_img = QtWidgets.QPushButton("Удалить фото")
        self.btn_delete_img.setStyleSheet("background-color: rgb(255, 170, 255);")
        self.btn_delete_img.setToolTip("Ctrl+D")
        self.btn_delete_img.setVisible(False)

        self.btn_save = QtWidgets.QPushButton("Сохранить")
        self.btn_save.setStyleSheet("background-color: rgb(85, 170, 255);")
        self.btn_save.setToolTip('Ctrl+S')
        self.btn_cancel = QtWidgets.QPushButton("Отменить") 
        self.btn_cancel.setStyleSheet("background-color: rgb(85, 170, 255);")
        self.btn_cancel.setToolTip("Ctrl+W")
        self.btn_cancel.setVisible(False)
        
        self.card_layout.addWidget(self.btn_load_img)
        self.card_layout.addWidget(self.btn_delete_img)
        self.card_layout.addWidget(self.btn_save)
        self.card_layout.addWidget(self.btn_cancel)
        
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
        self.btn_load_img.clicked.connect(self._load_img)
        self.btn_delete_img.clicked.connect(self._delete_img)
        self.btn_save.clicked.connect(self._save_game)
        self.btn_cancel.clicked.connect(self._clear_fields)

    def _setup_keysequence(self):
        """Настройка горячих клавиш"""
        QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+N"), self, self._clean_filter)
        QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+S"), self, self._save_game)
        QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+W"), self, self._clear_fields)
        QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+F"), self, self._apply_filter)
        QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+L"), self, self._load_img)
        QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+D"), self, self._delete_img)

    def _refresh_games(self):
        """Обновление данных из БД"""
        games = self.db.get_all()
        self._show_cards(games)

    def _apply_filter(self):
        """Применение фильтра"""
        self.btn_clean_filter.setStyleSheet("background-color: rgb(170, 255, 255);")
        min_players = self.sb_filter.value()
        games = self.db.get_filtered(min_players)
        self._show_cards(games)

    def _show_cards(self, games):
        """Отображение карточек соответствующих условию"""
        for i in reversed(range(self.cards_layout.count())):
            widget = self.cards_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        for i, game in enumerate(games):
            card = GameCard(game, self)
            row = i // 3
            col = i % 3
            self.cards_layout.addWidget(card, row, col)
        # Если нет записей
        if not games:
            empty_lbl = QtWidgets.QLabel("Нет игр в коллекции\nЧтобы добавить игру,\nзаполните все поля и нажмите кнопку 'Сохранить'")
            empty_lbl.setAlignment(QtCore.Qt.AlignCenter)
            self.cards_layout.addWidget(empty_lbl, 0, 0)
            
    def _clean_filter(self):
        """Сброс фильтра"""
        self.sb_filter.setValue(1)
        self.btn_clean_filter.setStyleSheet("background-color: light gray;")
        self._refresh_games()

    def update_game(self, data):
        """Редактирование игры"""
        self.btn_delete_img.setVisible(True)
        self.btn_cancel.setVisible(True)
        self.btn_save.setText("Обновить")
        self.edit_id = data['id']
        self.le_name.setText(data['name'])
        self.sb_count.setValue(data['players'])
        minutes = data['time']
        hours = minutes // 60
        minute = minutes % 60
        time = QtCore.QTime(hours, minute)
        self.time_edit.setTime(time)
        index = self.cb_difficulty.findText(data['difficulty'])
        self.cb_difficulty.setCurrentIndex(index)
        if data['photo_path']:
            self.current_photo_path = data['photo_path']
            self._load_img_to_edit(data['photo_path'])
        else:
            self.current_photo_path = None
            self.lbl_img.setText("Нет фото")

    def _load_img_to_edit(self, path):
        """Загрузка фото для редактирования"""
        try:
            pixmap = QtGui.QPixmap(path)
            if not pixmap.isNull():
                self.lbl_img.setPixmap(pixmap.scaled(300, 300, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
        except Exception as e:
            logger.error(f"Ошибка загрузки фото: {e}")

    def delete_game(self, id):
        """Удаление игры"""
        reply = QtWidgets.QMessageBox.question(self,"Подтверждение удаления",
            "Вы уверены, что хотите удалить эту игру?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            if self.db.delete_game(id):
                self._refresh_games()

    def _load_img(self):
        """Загрузка изображения"""
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Выберите изображение",
            "", "Images (*.png *.jpg *.jpeg *.bmp *.gif)")
        if not path:
            return
        try:
            img = Image.open(path).convert("RGBA") # Приводим к единому формату
            img.thumbnail((300, 300), Image.Resampling.LANCZOS) # Масштабируем с сохранением пропорций
            # Конвертация Pillow -> Qt
            qt_img = QtGui.QImage(img.tobytes(), img.width, img.height, QtGui.QImage.Format_RGBA8888)
            pixmap = QtGui.QPixmap.fromImage(qt_img)
            self.lbl_img.setPixmap(pixmap)
            self.current_photo_path = path
            self.lbl_img.setStyleSheet("background-color: #f0f0f0;")
            self.btn_delete_img.setVisible(True)
            logger.info(f"Загружено фото: {path}")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить изображение:\n{e}")
            logger.error(f"Ошибка загрузки изображения: {e}")
    
    def _delete_img(self):
        """Удаление изображения"""
        self.btn_delete_img.setVisible(False)
        self.current_photo_path = None
        self.lbl_img.setText("Нет фото")
        self.lbl_img.setStyleSheet("background-color: #f0f0f0;")

    def _save_game(self):
        """Сохранение игры"""
        if not self.le_name.text().strip():
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Поле 'Название' обязательно для заполнения.")
            return
        time = self.time_edit.time()
        time_minutes = time.hour() * 60 + time.minute() 
        # Валидация
        if time_minutes <= 0:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Время партии должно быть больше 0 минут.")
            return
        players = self.sb_count.value()
        if players < 2:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Минимальное количество игроков должно быть больше 1.")
            return
        # запись данных
        data = {
            "name": self.le_name.text().strip(),
            "players": self.sb_count.value(),
            "time": time_minutes,
            "difficulty": self.cb_difficulty.currentText(),
            "photo_path": self.current_photo_path}
        try:
            if self.edit_id:
                data['id'] = self.edit_id
                success = self.db.update_game(data)
            else:
                success = self.db.insert_game(data)
            if success:
                self._refresh_games()
                self._clear_fields()
            else:
                QtWidgets.QMessageBox.critical(self, "Ошибка", "Не удалось сохранить игру")
        except Exception as e:
            logger.error(f"Ошибка сохранения: {e}")
            QtWidgets.QMessageBox.critical(self, "Ошибка", f"Произошла ошибка: {str(e)}")

    def _clear_fields(self):
        """Очистка полей формы"""
        self.btn_delete_img.setVisible(False)
        self.btn_cancel.setVisible(False)
        self.btn_save.setText("Сохранить")
        self.le_name.clear()
        self.lbl_img.setText("Нет фото")
        self.lbl_img.setStyleSheet("background-color: #f0f0f0;")     
        self.sb_count.setValue(2)
        self.time_edit.setTime(QtCore.QTime(0, 30)) 
        self.cb_difficulty.setCurrentIndex(0)
        self.edit_id = None
        self.current_photo_path = None
        
    def closeEvent(self, event):
        """Переопределение закрытия окна"""
        reply = QtWidgets.QMessageBox.question(self, "Выход", "Вы уверены, что хотите выйти?", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            try:
                self.db.close()
                logger.info("БД закрыта")
            except Exception as e:
                logger.error(f"Ошибка при закрытии БД: {e}")
            event.accept()
        else:
            event.ignore()

    


