import os
import sys
import requests
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QPushButton
from PyQt6.QtCore import Qt

WINDOW_SIZE = (600, 450)
API_URL = "http://static-maps.yandex.ru/1.x/"
MAP_SIZE = "600,450"


class MapViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.coordinates = self.get_user_input("Введите координаты через пробел: ")
        self.scale = self.get_user_input("Введите масштаб в процентах: ")
        self.map_type = "map"  # По умолчанию используется стандартная карта
        self.validate_inputs()
        self.fetch_map_image()
        self.setup_ui()

    def get_user_input(self, prompt):
        return input(prompt)

    def validate_inputs(self):
        try:
            lat, lon = map(float, self.coordinates.split())
            self.coordinates = f"{lat},{lon}"
        except ValueError:
            print("Ошибка: введите корректные координаты (два числа через пробел).")
            sys.exit(1)

        scale_value = float(self.scale)
        if scale_value < 1 or scale_value > 100:
            print('Масштаб должен быть в диапазоне от 1 до 100')
            sys.exit(1)

        self.scale = round(0.17 * int(scale_value))
        self.scale = max(0, min(self.scale, 17))

    def fetch_map_image(self):
        map_api_url = f"{API_URL}?ll={self.coordinates}&z={self.scale}&size={MAP_SIZE}&l={self.map_type}"
        try:
            response = requests.get(map_api_url)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при выполнении запроса: {e}")
            sys.exit(1)

        self.map_file = "map_image.png"
        with open(self.map_file, "wb") as file:
            file.write(response.content)

    def setup_ui(self):
        self.setGeometry(100, 100, *WINDOW_SIZE)
        self.setWindowTitle('Карта')

        self.pixmap = QPixmap(self.map_file)
        self.image_label = QLabel(self)
        self.image_label.setPixmap(self.pixmap)
        self.image_label.move(0, 0)

        # Кнопка для переключения темы
        self.theme_button = QPushButton('Сменить тему', self)
        self.theme_button.clicked.connect(self.toggle_theme)
        self.theme_button.move(10, 10)
        self.theme_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)  # Запрещаем кнопке захватывать фокус

    def toggle_theme(self):
        # Переключение между стандартной картой и схемой
        self.map_type = "skl" if self.map_type == "map" else "map"
        self.update_map()

    def keyPressEvent(self, event):
        lat, lon = map(float, self.coordinates.split(','))

        if event.key() == Qt.Key.Key_PageUp:
            self.scale = min(self.scale + 1, 17)
            self.update_map()
        elif event.key() == Qt.Key.Key_PageDown:
            self.scale = max(self.scale - 1, 0)
            self.update_map()
        elif event.key() == Qt.Key.Key_Up:
            lon += 0.1
            lon = min(lon, 180)
            self.coordinates = f"{lat},{lon}"
            self.update_map()
        elif event.key() == Qt.Key.Key_Down:
            lon -= 0.1
            lon = max(lon, -90)
            self.coordinates = f"{lat},{lon}"
            self.update_map()
        elif event.key() == Qt.Key.Key_Left:
            lat -= 0.1
            lat = max(lat, -180)
            self.coordinates = f"{lat},{lon}"
            self.update_map()
        elif event.key() == Qt.Key.Key_Right:
            lat += 0.1
            lat = min(lat, 90)
            self.coordinates = f"{lat},{lon}"
            self.update_map()

    def update_map(self):
        self.fetch_map_image()
        self.pixmap = QPixmap(self.map_file)
        self.image_label.setPixmap(self.pixmap)

    def closeEvent(self, event):
        if os.path.exists(self.map_file):
            os.remove(self.map_file)
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    viewer = MapViewer()
    viewer.show()
    sys.exit(app.exec())