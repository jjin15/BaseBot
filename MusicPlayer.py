import vlc
import pafy
from collections import deque

TEST_URL = 'https://www.youtube.com/watch?v=KpOtuoHL45Y'
INVALID_URL = 'Invalid URL entered'

class Song:
    def __init__(self, title, length, url):
        self.title = title
        self.length = length
        self.url = url

    def get_title(self):
        return self.title

    def get_length(self):
        return self.length

    def get_url(self):
        return self.url


class MusicPlayer:
    def __init__(self):
        self.queue = deque()
        self.current_play_thread = None
        self.playing = False
        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()
        self.media = None
        self.current_song = None

    def add_to_queue(self, url):
        # TODO: need to check for valid youtube url
        try:
            url = pafy.new(url)
        except (ValueError, OSError):
            return INVALID_URL
        best = url.getbestaudio()
        best_url = best.url
        title = url.title
        length = url.duration
        s = Song(title, length, best_url)
        self.queue.append(s)
        return 0

    def play_track(self):
        if self.playing:
            self.play()
            return True
        self.playing = True
        if not len(self.queue) > 0:
            return False
        self.current_song = self.queue.popleft()
        self.media = self.instance.media_new(self.current_song.get_url())
        self.media.get_mrl()
        self.player.set_media(self.media)
        self.player.play()
        return True

    def get_current_title(self):
        if self.current_song is not None:
            return self.current_song.get_title()
        return False

    def get_current_song_duration(self):
        if self.current_song is not None:
            return self.current_song.get_length()
        return False

    def play(self):
        self.player.play()

    def pause_track(self):
        self.player.pause()

    def stop_track(self):
        self.player.stop()
        self.current_song = None
        self.playing = False
        self.media = None

    def skip_track(self):
        self.stop_track()
        self.play_track()

