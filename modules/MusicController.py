from modules.MusicPlayer import *
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QApplication
from threading import Thread
import sys


class MusicController(QtWidgets.QWidget):
    def __init__(self):
        super(MusicController, self).__init__()
        self.setWindowTitle("MusicController")
        self.layout = QtWidgets.QGridLayout()
        self.play_button = QtWidgets.QPushButton()
        self.skip_button = QtWidgets.QPushButton()
        self.curr_title_label = QtWidgets.QLabel('Playing: ')
        self.curr_title_field = QtWidgets.QLabel()
        self.add_song_button = QtWidgets.QPushButton('ADD')
        self.add_song_field = QtWidgets.QLineEdit()
        self.add_song_label = QtWidgets.QLabel("URL:")
        self.song_list = QtWidgets.QListView()
        self.music_player = None
        self.song_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.volume_slider = QtWidgets.QSlider(QtCore.Qt.Vertical)
        self.volume_slider.valueChanged.connect(self.handle_vol_slider_changed)
        self.volume_slider.setMinimum(0)
        self.volume_slider.setMaximum(100)
        self.volume_slider.setValue(100)
        self.volume_label = QtWidgets.QLabel("Volume:")

        self.queue_thread = None
        self.running = False
        self.thread_list = []
        self.layout.addWidget(self.volume_slider, 0, 0, 3, 1)
        self.layout.addWidget(self.add_song_label, 0, 1, 1, 1)
        self.layout.addWidget(self.add_song_field, 0, 2, 1, 3)
        self.layout.addWidget(self.add_song_button, 0, 5, 1, 1)
        self.layout.addWidget(self.curr_title_label, 1, 1, 1, 1)
        self.layout.addWidget(self.curr_title_field, 1, 2, 1, 4)
        self.layout.addWidget(self.play_button, 2, 1, 1, 1)
        self.layout.addWidget(self.skip_button, 2, 2, 1, 1)
        self.layout.addWidget(self.song_slider, 2, 3, 1, 3)
        self.setLayout(self.layout)
        self.show()

    def close(self):
        self.running = False
        self.music_player.stop_track()
        self.music_player = None

    def add_music_player(self):
        self.music_player = MusicPlayer()
        self.running = True
        self.queue_thread = Thread(target=self.music_queue_thread)
        self.queue_thread.start()
        self.thread_list.append(self.queue_thread)

    def music_queue_thread(self):
        while self.running:
            if self.music_player is not None:
                songlist = self.music_player.publish_queue()
                # add these to the listview

    def handle_vol_slider_changed(self):
        if self.music_player is not None:
            self.music_player.set_volume(self.volume_slider.value())

    def handle_play_button(self):
        if self.music_player is not None:
            self.music_player.play()

    def handle_skip_button(self):
        if self.music_player is not None:
            self.music_player.skip_track()

    def handle_add_song_button(self):
        if self.add_song_field.text() == '':
            return
        if self.music_player is not None:
            new_url = str(self.add_song_field.text())
            if self.music_player.add_to_queue(new_url):
                # invalid url
                return


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mc = MusicController()
    app.exec_()