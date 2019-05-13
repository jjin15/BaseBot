from BaseBot import *
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QApplication
from threading import Thread
import sys


class ChatBot(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("TwitchChatBot")
        self.bot = None
        self.center = QtWidgets.QWidget()
        self.chat_view = QtWidgets.QTextEdit()
        self.chat_view.setReadOnly(True)
        self.send_field = QtWidgets.QLineEdit()
        self.send_field.returnPressed.connect(self.handle_send_button)
        self.main_layout = QtWidgets.QGridLayout()
        self.main_layout.addWidget(self.chat_view, 0, 0, 1, 2)
        self.main_layout.addWidget(self.send_field, 1, 0, 1, 2)
        self.bot = BaseBot()
        self.bot.chat_msg_sig.connect(self.append_message)
        self.bot_thread = Thread(target=self.connect_to_bot)
        self.bot_thread.start()
        self.center.setLayout(self.main_layout)
        self.setCentralWidget(self.center)
        self.show()

    def connect_to_bot(self):
        self.bot.run_main()

    def append_message(self, msg):
        self.chat_view.append(msg)

    def handle_send_button(self):
        text = self.send_field.text()
        self.send_field.setText('')
        self.bot.send_message(text)
        self.chat_view.append(text)
        # send message to channel


def main():
    app = QApplication(sys.argv)
    cb = ChatBot()
    app.exec_()


if __name__ == "__main__":
    main()





