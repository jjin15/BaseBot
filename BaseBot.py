import socket
import re
import time
import sys

HOSTNAME = "irc.chat.twitch.tv"
PORT = 6667
NICK = "yournamehere"
PASS = "oauth:pw"
CHAN = "yourchannel"
PING = "PING :tmi.twitch.tv\r\n"


class BaseBot:
    def __init__(self):
        self.conn = None
        self.command_dict = {}
        self.connect_to_channel()
        self.run_main()

    """ Method uses the configurable global variables to connect to the Twitch IRC Server
    """
    def connect_to_channel(self):
        self.conn = socket.socket()
        self.conn.connect((HOSTNAME, PORT))
        self.conn.send("PASS {}\r\n".format(PASS).encode("utf-8"))
        self.conn.send("NICK {}\r\n".format(NICK).encode("utf-8"))
        self.conn.send("JOIN #{}\r\n".format(CHAN).encode("utf-8"))

    """ Main Loop
    """
    def run_main(self):
        response = ""
        while True:
            response = response + self.conn.recv(1024).decode("utf-8")
            all_data = response.split("\r\n")
            response = all_data.pop()
            status, user, message = self.parse_message(all_data[0])
            if status:
                continue
            status = self.handle_message(user, message)

    """ Allows for registering commands
        Arguments:
            - cmd: type: str The string to look for ex "!test"
            - cmd_handler: type: method The method to run when this command is entered
    """
    def register_command(self, cmd, cmd_handler):
        if cmd not in self.command_dict.keys():
            self.command_dict[cmd] = cmd_handler

    """ De-registers a command so that it is no longer usable.
    """
    def deregister_command(self, cmd):
        if cmd in self.command_dict.keys():
            self.command_dict.pop(cmd)

    """ Runs a command from the registered command_dict
    """
    def run_command(self, cmd):
        self.command_dict[cmd]()

    """ Sends a message to the chat group.
        Defaults to the configured channel, but can also send messages to other channels.
    """
    def send_message(self, msg, user=CHAN):
        message = "PRIVMSG #%s :%s\r\n" % (user, msg)
        self.conn.send(message.encode("utf-8"))

    """ Reply to server's ping
    """
    def send_pong(self):
        self.conn.send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))

    """ Function to handle incoming messages
        Arguments: 
            - msg: takes the incoming received message
        Returns:
            - status, user, message
    """
    def parse_message(self, msg):
        # first check for ping from server
        if msg == PING:
            self.send_pong()

        # split the incoming message into an array

        # message sent to the channel
        # incoming messages are formatted as such:
        # :username!username@username.tmi.twitch.tv PRIVMSG #channel :message here
        if "PRIVMSG" in msg:
            data = msg.split(".tmi.twitch.tv PRIVMSG #%s :" % CHAN)
            username = data[0].split("!")[0][1:]
            # print(username)
            message = data[-1]
            print(message)
            return 0, username, message
        return 1, -1,-1

    """ Function to read the message and determine whether it is a command.
        Non command messages are ignored.
    """
    def handle_message(self, user, message):
        if message[0] == "!":
            # need to check the message against the commands
            data = message.split(" ")
            if data[0] in self.command_dict.keys():
                # run command
                return self.run_command(data[0])
            else:
                return 1
        else:
            return 1

    """ The following methods are standard twitch chat commands for mods.
    """
    def ban(self, user):
        self.conn.send(".ban %s" % user)

    def timeout(self, user):
        self.conn.send(".timeout %s" % user)

    def unban(self, user):
        self.conn.send(".unban %s" % user)

    def slow(self, seconds):
        self.conn.send(".slow %d" % seconds)

    def slowoff(self):
        self.conn.send(".slowoff")


def main():
    b = BaseBot()


if __name__ == "__main__":
    main()