import vlc
import pafy
from collections import deque
from vlc import State

INVALID_URL_ERR = 'Invalid URL Entered'
EMPTY_QUEUE_ERR = 'No Songs in Queue'
PLAYER_STATE_ERROR = 'Player is in Error State'
NO_INFO_AVAILABLE = -1, -1


class Song:
    def __init__(self, title, url):
        self.title = title
        self.url = url

    def get_title(self):
        return self.title

    def get_url(self):
        return self.url


class MusicPlayer:
    def __init__(self):
        self.queue = deque()
        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()
        self.media = None
        self.current_song = None

    def add_to_queue(self, url):
        try:
            url = pafy.new(url)
        except (ValueError, OSError):
            return INVALID_URL_ERR
        best = url.getbestaudio()
        best_url = best.url
        title = url.title
        s = Song(title, best_url)
        self.queue.append(s)
        return 0

    """ Returns a list(str) of all song titles in the deque in order.
    """
    def publish_queue(self):
        songlist = []
        for song in self.queue:
            songlist.append(song.get_title())
        return songlist

    def play(self):
        state = self.player.get_state()
        # case paused, resume play
        if state == State(4):
            self.player.play()
            return 0
        # case playing, pause
        elif state == State(3):
            self.player.pause()
            return 0
        # case ended, stopped, or doing nothing, go to next track.
        elif state == State(6) or state == State(0) or state == State(5):
            if not len(self.queue) > 0:
                return EMPTY_QUEUE_ERR
            self.current_song = self.queue.popleft()
            self.media = self.instance.media_new(self.current_song.get_url())
            self.media.get_mrl()
            self.player.set_media(self.media)
            self.player.play()
            return 0
        elif state == State(7):
            return PLAYER_STATE_ERROR
        return 0

    def get_current_title(self):
        if self.current_song is not None:
            return self.current_song.get_title()
        return False

    """ Returns a tuple of total length and current time in milliseconds
        Returns -1, -1 if not available
    """
    def get_current_song_duration(self):
        if not self.player.get_length() == -1:
            return self.player.get_length(), self.player.get_time()
        else:
            return NO_INFO_AVAILABLE

    def stop_track(self):
        self.player.stop()
        self.current_song = None
        self.media = None

    def skip_track(self):
        self.stop_track()
        return self.play()
