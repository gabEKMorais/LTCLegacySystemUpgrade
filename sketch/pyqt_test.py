import sys
from PyQt5.QtWidgets import QApplication, QLabel, QWidget

app = QApplication(sys.argv)

window = QWidget()
window.setWindowTitle("Minha primeira janela PyQt")

label = QLabel("Olá, mundo!", window)

window.show()
sys.exit(app.exec())