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
        self.service_list = {}
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

    def register_command(self, cmd: str, cmd_handler):
        """
        Allows registering of commands
        :param cmd: the string to trigger the command on
        :type cmd: str
        :param cmd_handler: the function to run when the command is entered
        :type cmd_handler: function
        :param service: a service that needs to run continuously until cancelled
        """
        if cmd not in self.command_dict.keys():
            self.command_dict[cmd] = cmd_handler

    def deregister_command(self, cmd: str):
        """
        De-registers a command so it is no longer triggering the corresponding function
        :param cmd: the command to de-register
        :type cmd: str
        """
        if cmd in self.command_dict.keys():
            self.command_dict.pop(cmd)

    def register_service(self, service_name, service):
        if service_name not in self.service_list.keys():
            self.service_list[service_name] = service

    def deregister_service(self, service_name):
        if service_name in self.service_list.keys():
            self.service_list.pop(service_name)

    """ Runs a command from the registered command_dict
    """
    def run_command(self, cmd: str, cmd_data: str):
        output = self.command_dict[cmd](cmd_data)
        return output

    """ Sends a message to the chat group.
        Defaults to the configured channel, but can also send messages to other channels.
    """
    def send_message(self, msg: str, user: str = CHAN):
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
    def parse_message(self, msg: str):
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
            data = message.split(" ", 1)
            if data[0] in self.command_dict.keys():
                try:
                    cmd_data = data[1]
                except IndexError:
                    cmd_data = None
                # run command
                return self.run_command(data[0], cmd_data)
            else:
                return 1
        else:
            for k, s in self.service_list.items():
                output = s(user, message)
                # service handler should return
                if output:
                    self.send_message(output)
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