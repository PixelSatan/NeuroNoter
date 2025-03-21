from PyQt6.QtWidgets import QApplication, QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QLabel, QTextEdit, QCheckBox, QComboBox, QHBoxLayout, QWidget, QHeaderView, QSizePolicy, QSpacerItem, QMessageBox, QApplication
from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtCore import Qt, QSignalBlocker, QPropertyAnimation, QEasingCurve
import sqlite3
import datetime
import requests
import json
import os

config_path = "config.json"


class TaskManager(QDialog):
    def __init__(self):
        super().__init__()

        dark_palette = QPalette()
        dark_palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
        dark_palette.setColor(QPalette.ColorRole.Base, QColor(44, 47, 51))  # Серый фон вместо черного
        dark_palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))  # Белый текст
        dark_palette.setColor(QPalette.ColorRole.Highlight, QColor(28, 28, 28))  # Подсветка выделенного текста
        dark_palette.setColor(QPalette.ColorRole.PlaceholderText, QColor(176, 176, 176))



        dark_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.ColorRole.ToolTipText, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ColorRole.ButtonText, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 0, 0))
        dark_palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
        # Устанавливаем тему
        app = QApplication.instance()
        app.setPalette(dark_palette)

        QApplication.setStyle("Fusion")  # Современный стиль
        self.setWindowTitle("NeuroNote")
        self.setMinimumWidth(400)  # Минимальная ширина окна
        self.setMaximumWidth(400)
        self.setMinimumHeight(425)
        self.setMaximumHeight(425)


        screen = QApplication.primaryScreen().geometry()
        screen_center_x = screen.width() // 2
        screen_center_y = screen.height() // 2

        


        # Размер главного окна
        window_width = 500
        window_height = 350

        # Вычисляем координаты так, чтобы окно было по центру
        self.setGeometry(
            screen_center_x - window_width // 2, 
            screen_center_y - window_height // 2, 
            window_width, 
            window_height
        )


        layout = QVBoxLayout()

        def fade_in_animation(self, widget):
                anim = QPropertyAnimation(widget, b"windowOpacity")
                anim.setDuration(300)  # Длительность анимации в миллисекундах
                anim.setStartValue(0)
                anim.setEndValue(1)
                anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
                anim.start()
                widget.show()

        # Выбор категории
        self.category_dropdown = QComboBox()
        self.category_dropdown.addItems(["🎮Games", "🎥Video", "🛑 YouTube", "🔗Link", "📝Note", "📌Task"])
        layout.addWidget(QLabel("Choose Category:"))
        layout.addWidget(self.category_dropdown)


        
        # Поле ввода заметки
        self.note_input = QTextEdit()
        self.note_input.setPlaceholderText("Write here...")
        layout.addWidget(self.note_input)
        self.note_input.setStyleSheet("border: 1px solid #72767D; background-color: #2C2F33; color: white;")

        self.note_input.setStyleSheet("""
            border: 1px solid #72767D;
            background-color: #2C2F33;
            color: white;
            selection-background-color: #7289DA;
            border-radius: 5px;
        """)

        # Создаём окно логов перед применением стилей
        self.log_window = QTextEdit()
        self.log_window.setReadOnly(True)  # Делаем окно только для чтения

        # Теперь можно применить стиль
        self.log_window.setStyleSheet("""
            border: 1px solid #72767D;
            background-color: #2C2F33;
            color: white;
            selection-background-color: #7289DA;
            border-radius: 5px;
        """)




        # Выбор тегов (кнопки)
        self.tags = {
            "Important": "red",
            "Work": "green",
            "Personal": "yellow",
            "Urgent": "orange",
            "Info": "blue",
            "Success": "lime",
            "Warning": "purple",
            "Error": "gold"
        }

        self.webhooks = {
            "Games": "INSERT_YOUR_WEBHOOK_HERE",
            "Link": "INSERT_YOUR_WEBHOOK_HERE",
            "YouTube": "INSERT_YOUR_WEBHOOK_HERE",
            "Video": "INSERT_YOUR_WEBHOOK_HERE",
            "Note": "INSERT_YOUR_WEBHOOK_HERE",
            "Task": "INSERT_YOUR_WEBHOOK_HERE"
        }




        layout.addWidget(QLabel("Choose a tag (max. 3):"))

        self.selected_tags = set()
        self.tag_buttons = {}

        tag_layout = QHBoxLayout()
        tag_layout.setSpacing(0)  # Уменьшаем расстояние между кнопками (по умолчанию 10+)
        tag_layout.setContentsMargins(0, 5, 0, 5)

        for tag, color in self.tags.items():
            btn = QPushButton()
            btn.setFixedSize(20,20)
            btn.setStyleSheet(f"background-color: {color}; border-radius: 5px;")
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, t=tag: self.toggle_tag(t, checked))
            self.tag_buttons[tag] = btn
            tag_layout.addWidget(btn)

        tag_widget = QWidget()
        tag_widget.setLayout(tag_layout)
        tag_widget.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        layout.addWidget(tag_widget)

        # Чекбокс отправки в Discord
        self.send_to_discord = QCheckBox("Send to Discord")
        layout.addWidget(self.send_to_discord)

        # Кнопка сохранения
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_note)
        layout.addWidget(self.save_button)

        # Кнопки для открытия Saved Notes и очистки
        self.saved_notes_button = QPushButton("SavedNotes")
        self.saved_notes_button.clicked.connect(self.show_saved_notes)
        layout.addWidget(self.saved_notes_button)

        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.clear_notes)
        layout.addWidget(self.clear_button)

        button_style = """
            QPushButton {
                border: 1px solid #4E5D94;
                background-color: #424549;
                color: white;
                border-radius: 4px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #5865F2;
            }
            QPushButton:pressed {
                background-color: #3C45A5;
            }
        """
        self.save_button.setStyleSheet(button_style)
        self.clear_button.setStyleSheet(button_style)
        self.saved_notes_button.setStyleSheet(button_style)

        # Окно логов
        layout.addItem(QSpacerItem(10, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        layout.addWidget(QLabel("Logs:"))  # Заголовок логов
        self.log_window = QTextEdit()
        self.log_window.setReadOnly(True)  # Только для чтения
        self.log_window.setFixedHeight(70)  # Высота логов
        self.log_window.setStyleSheet("border: 1px solid #72767D; background-color: #2C2F33; color: white;")

        layout.addWidget(self.log_window)

        

        self.setLayout(layout)
        self.initDB()




    def initDB(self):
        """Инициализация базы данных"""
        self.conn = sqlite3.connect("tasks_notes.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY,
                category TEXT,
                content TEXT,
                date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                tags TEXT
            )
        """)
        self.conn.commit()

    def toggle_tag(self, selected_tag, checked):
        """Обновлённая логика выбора тегов (разрешает только один тег за раз)"""
        if checked:
            # **Сбрасываем все другие теги**
            for tag, btn in self.tag_buttons.items():
                if tag != selected_tag:
                    with QSignalBlocker(btn):  # Блокируем сигналы, чтобы избежать рекурсий
                        btn.setChecked(False)
                        btn.setStyleSheet(f"background-color: {self.tags[tag]}; border-radius: 5px;")

            # **Выбранный тег остаётся выделенным**
            self.selected_tags = {selected_tag}
            self.tag_buttons[selected_tag].setChecked(True)
            self.tag_buttons[selected_tag].setStyleSheet(
                f"background-color: {self.tags[selected_tag]}; border: 2px solid black; border-radius: 5px;"
            )
        else:
            # **Если кликнули ещё раз по тому же тегу – убираем его**
            self.selected_tags.clear()
            self.tag_buttons[selected_tag].setStyleSheet(f"background-color: {self.tags[selected_tag]}; border-radius: 5px;")



    def save_note(self):
        """Сохранение заметки в базу данных"""
        for tag, btn in self.tag_buttons.items():
            print(f"Тег: {tag}, Checked: {btn.isChecked()}, Enabled: {btn.isEnabled()}")

        category = self.category_dropdown.currentText()
        content = self.note_input.toPlainText().strip()

        self.category_dropdown.setStyleSheet("""
            QComboBox {
                background-color: #23272A;
                border: 1px solid #72767D;
                color: white;
                padding: 4px;
                border-radius: 4px;
            }
            QComboBox:hover {
                background-color: #2C2F33;
            }
            QComboBox QAbstractItemView {
                background-color: #2C2F33;
                selection-background-color: #5865F2;
                color: white;
            }
        """)


        # Собираем выбранные теги
        selected_tag = next((tag for tag, btn in self.tag_buttons.items() if btn.isChecked()), None)


        if content:
            self.cursor.execute("INSERT INTO notes (category, content, date, tags) VALUES (?, ?, ?, ?)", 
                                (category, content, datetime.datetime.now(), selected_tag if selected_tag else "без тега"))

            self.conn.commit()
            self.note_input.clear()

            # **Логируем сохранение заметки**
            emoji = self.webhooks.get(category, ("", ""))[1]  # Берём эмодзи для категории
            #tag_display = ", ".join(selected_tag) if selected_tag else "без тегов"
            self.log_message(f"✅ {emoji} Note saved in **[{category}]**")

            # Сбрасываем кнопки тегов
            for tag, btn in self.tag_buttons.items():
                btn.setChecked(False)  # Сбрасываем нажатое состояние
                btn.setEnabled(True)   # Убеждаемся, что кнопка активна
                btn.repaint()          # Принудительно перерисовываем кнопку
                btn.clearFocus()       # Убираем фокус с кнопки






            # **Отправка в Discord**
            if self.send_to_discord.isChecked():
                self.send_to_discord_webhook(category, content, selected_tag)


    def save_to_json():
        """Сохраняет данные из базы данных в JSON файл"""
        db_path = "название_файла.db"  # Укажи путь к твоему файлу
        json_path = "neuronote_data.json"  # Имя JSON файла

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Получаем все заметки (замени notes на свою таблицу)
        cursor.execute("SELECT * FROM notes;")  
        rows = cursor.fetchall()

        # Список заголовков (замени на названия своих колонок)
        columns = ["id", "content", "date", "tags", "category"]
        
        # Преобразуем в список словарей
        data = [dict(zip(columns, row)) for row in rows]

        # Сохраняем в JSON
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        conn.close()
        print(f"Данные сохранены в {json_path}")







    # def send_to_discord_webhook(self, category, content):
    #     """Заглушка для отправки в Discord (замени на Webhook)"""
    #     print(f"[DISCORD] Отправка в канал: {category}, Контент: {content}")

    def show_saved_notes(self):
        
        """Открывает окно с сохранёнными заметками"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Saved Notes")
        dialog.setFixedSize(750, 400)  # Расширяем окно

        # Размер окна Saved Notes
        saved_width = 600
        saved_height = 400

        # Получаем текущую позицию главного окна
        main_x = self.x()
        main_y = self.y()
        main_width = self.width()

        # Устанавливаем Saved Notes справа от главного окна, с минимальным отступом
        dialog.setGeometry(
            main_x + main_width + 10,  # 10 пикселей отступ
            main_y,  # Высота как у главного окна
            saved_width,
            saved_height
        )


        layout = QVBoxLayout()
        table_widget = QTableWidget()
        table_widget.setColumnCount(4)  # Добавляем 4-й столбец для категорий
        table_widget.setHorizontalHeaderLabels(["Note", "Date", "Tag", "Category"])

        self.cursor.execute("SELECT category, content, date, tags FROM notes ORDER BY date DESC")
        notes = self.cursor.fetchall()
        table_widget.setRowCount(len(notes))

        for row, note in enumerate(notes):
            local_time = datetime.datetime.strptime(note[2], "%Y-%m-%d %H:%M:%S.%f").strftime("%Y-%m-%d %H:%M:%S")
            category = note[0]  # Категория отдельно
            note_text = note[1]  # Оставляем только текст заметки
            tags = note[3] if note[3] else ""

            table_widget.setItem(row, 0, QTableWidgetItem(note_text))  # Только заметка
            table_widget.setItem(row, 1, QTableWidgetItem(local_time))  # Дата
            table_widget.setItem(row, 3, QTableWidgetItem(category))  # Категория

            # Отображение тегов цветными квадратиками
            tag_list = tags.split(",") if tags else []
            color_widget = QWidget()
            color_layout = QHBoxLayout()
            color_layout.setContentsMargins(0, 0, 0, 0)

            for tag in tag_list:
                tag_color = self.tags.get(tag, "silver")
                tag_label = QLabel()
                tag_label.setFixedSize(15, 15)
                tag_label.setStyleSheet(f"background-color: {tag_color}; border-radius: 3px;")
                color_layout.addWidget(tag_label)

            color_widget.setLayout(color_layout)
            table_widget.setCellWidget(row, 2, color_widget)  # Вставляем цветные теги

        # Настраиваем ширину колонок
        table_widget.setColumnWidth(0, 350)  # Заметка
        table_widget.setColumnWidth(1, 120)  # Дата
        table_widget.setColumnWidth(2, 100)  # Теги
        table_widget.setColumnWidth(3, 100)  # Категория

        table_widget.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)

        layout.addWidget(table_widget)
        dialog.setLayout(layout)
        dialog.exec()


    def log_message(self, message):
        """Добавляет лог в окно логов"""
        self.log_window.append(message)



    def clear_notes(self):
        """Удаление всех записей"""
        self.cursor.execute("DELETE FROM notes")
        self.conn.commit()
        self.log_message("⚠️ Все сохранённые заметки удалены.")




    def clear_notes(self):
        """Очистка всех заметок с подтверждением"""
        reply = QMessageBox.question(self, "Confirmation", "Are you sure to delete all notes?",
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
                                    QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            self.cursor.execute("SELECT COUNT(*) FROM notes")
            count = self.cursor.fetchone()[0]  # Получаем количество заметок

            self.cursor.execute("DELETE FROM notes")
            self.conn.commit()

            self.log_message(f"⚠️ 🗑 Deleted {count} notes.")



    def send_to_discord_webhook(self, category, content, tags):
        """Отправляет сообщение в нужный канал Discord с эмодзи и цветами"""
        
        # Убираем эмодзи перед поиском вебхука
        clean_category = category
        for emoji in self.webhooks.values():
            clean_category = clean_category.replace(emoji[1], "").strip()

        
        webhook_data = self.webhooks.get(clean_category)

        if not webhook_data:
            self.log_message(f"⚠️ Webhook **{clean_category}** is not found!")
            return

        webhook_url, emoji = webhook_data  # Разбираем кортеж

        # Если выбрана категория "Video" -> отправляем обычное сообщение без embed
        if clean_category == "Video":
            data = {"content": f"{emoji} **[{clean_category}]** {content}"}
        else:
            # Выбираем цвет Embed-а в зависимости от тегов
            tag_colors = {
                "Important": 0xFF0000,  # Красный
                "Work": 0x008000,  # Зелёный
                "Personal": 0xFFFF00,  # Жёлтый
                "Urgent": 0xFFA500,  # Оранжевый
                "Info": 0x0000FF,  # Синий
                "Success": 0x32CD32,  # Лаймовый
                "Warning": 0x800080,  # Фиолетовый
                "Error": 0xFFD700  # Золотой
            }

            color = tag_colors.get(tags, 0xFFFFFF)  # Белый цвет по умолчанию

            embed = {
                "title": f"{emoji} **{clean_category}**",
                "description": content,
                "color": color
            }

            data = {"embeds": [embed]}

        response = requests.post(webhook_url, json=data)

        if response.status_code == 204:
            self.log_message(f"{emoji} 📩 Message sent to Discord")
        else:
            self.log_message(f"❌ Couldn't send to Discord **({clean_category})**: {response.status_code}")



if __name__ == "__main__":
    app = QApplication([])
    window = TaskManager()
    window.show()
    app.exec()