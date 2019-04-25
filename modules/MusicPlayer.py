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
        self.event_manager = self.player.event_manager()
        self.event_manager.event_attach(vlc.EventType.MediaPlayerEndReached, self.handle_song_finished)
        self.media = None
        self.current_song = None

    def add_to_queue(self, url: str, front: bool = False):
        """
        Takes a youtube link and adds it to the playing queue if it is valid.
        :param url: the youtube link
        :type url: str
        :param front: an optional param that when true, appends it to the front of the queue.
        :type front: bool
        """
        try:
            url = pafy.new(url)
        except (ValueError, OSError):
            return INVALID_URL_ERR
        best = url.getbestaudio()
        best_url = best.url
        title = url.title
        s = Song(title, best_url)
        if front:
            self.queue.appendleft(s)
        else:
            self.queue.append(s)
        return 0

    def handle_song_finished(self, event):
        self.play()

    def publish_queue(self):
        """
        Returns a list(str) of all song titles in the deque in order.
        :rtype: list
        """
        songlist = []
        for song in self.queue:
            songlist.append(song.get_title())
        return songlist

    def play(self):
        """
        Main function that handles play logic.
        :return: 0 on success, error code otherwise
        :rtype: int
        """
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
        """
        Gets the current title of the song playing.
        :return: Title of the song, or False if no song is playing
        :rtype: str or bool
        """
        if self.current_song is not None:
            return self.current_song.get_title()
        return False

    def set_volume(self, val: int):
        """
        :param val: the volume percentage (0-100)
        :type val: int
        :return: 0 on success, -1 on failure
        :rtype: int
        """
        return self.player.audio_set_volume(int(val))

    def get_volume(self):
        """
        :return: The volume percentage from 0-100
        :rtype: int
        """
        return self.player.audio_get_volume()

    def get_current_song_duration(self):
        """
        Function that gets the current song's total duration and current time
        :return: A tuple of the total length and current time of the song in milliseconds.
                 Returns -1, -1 if there is no information available
        :rtype: Tuple(int, int)
        """
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
