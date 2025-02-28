import os
import sys
import requests
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QApplication, QWidget, QLabel
from PyQt6.QtCore import Qt

WINDOW_SIZE = (600, 450)


class MapViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.coordinates = self.get_user_input("Введите координаты через пробел: ")
        self.scale = self.get_user_input("Введите масштаб в процентах: ")
        self.validate_inputs()
        self.fetch_map_image()
        self.setup_ui()

    def get_user_input(self, prompt):
        return input(prompt)

    def validate_inputs(self):
        self.coordinates = ','.join(self.coordinates.split())
        scale_value = float(self.scale)

        if scale_value > 100:
            print('Необходимо ввести масштаб от 1 до 100')

        self.scale = round(0.17 * int(scale_value))
        self.scale = max(0, min(self.scale, 17))

    def fetch_map_image(self):
        map_api_url = f"http://static-maps.yandex.ru/1.x/?ll={self.coordinates}&z={self.scale}&size=600,450&l=map"
        response = requests.get(map_api_url)

        if not response.ok:
            self.handle_error(map_api_url, response)

        self.map_file = "map_image.png"
        with open(self.map_file, "wb") as file:
            file.write(response.content)

    def handle_error(self, api_url, response):
        print('Ошибка при вводе координат')
        print(f"Ошибка выполнения запроса: {api_url}")
        print(f"Http статус: {response.status_code} ({response.reason})")
        sys.exit(1)

    def setup_ui(self):
        self.setGeometry(100, 100, *WINDOW_SIZE)
        self.setWindowTitle('Карта')

        self.pixmap = QPixmap(self.map_file)
        self.image_label = QLabel(self)
        self.image_label.setPixmap(self.pixmap)
        self.image_label.move(0, 0)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_PageUp:
            self.scale = min(self.scale + 1, 17)
            self.update_map()
        elif event.key() == Qt.Key.Key_PageDown:
            self.scale = max(self.scale - 1, 0)
            self.update_map()

    def update_map(self):
        self.fetch_map_image()
        self.pixmap = QPixmap(self.map_file)
        self.image_label.setPixmap(self.pixmap)

    def closeEvent(self, event):
        if os.path.exists(self.map_file):
            os.remove(self.map_file)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    viewer = MapViewer()
    viewer.show()
    sys.exit(app.exec())
