import sys
import time
import socket
import inspect
import logging
import itertools

import yaml
import requests

import commands


class IRC(object):
    """ Wrapper class providing access to some standard IRC commands """

    def __init__(self):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self, host, port):
        self._socket.connect((host, port))

    def password(self, password):
        self._socket.send('PASS ' + password + '\n')

    def nick(self, nick):
        self._socket.send('NICK ' + nick + '\n')

    def user(self, un):
        self._socket.send('USER %s %s %s :%s\n' % (un, un, un, un))

    def join(self, channel):
        self._socket.send('JOIN #' + channel + '\n')

    def pong(self, msg):
        self._socket.send('PONG %s\r\n' % msg)

    def recv(self, recv_size=1024):
        return self._socket.recv(recv_size)

    def privmsg(self, target, message):
        self._socket.send('PRIVMSG #%s :%s\n' % (target, message))

    def close(self):
        self._socket.close()


class BcbBot(object):
    """ BcbBot """
    def __init__(self, username, password, channel, port=6667, host='irc.twitch.tv'):
        """
        :param username: bot username
        :param password: twitch api password
        :param channel:  channel the bot listens to
        :param port:     irc port
        :param host:     irc address
        """
        self.username = username
        self.password = password
        self.channel = channel
        self.host = host
        self.port = port

        # recent commands
        self.command_history = []
        # command objects
        self.commands = {}
        # direct irc connection to chat
        self.irc = IRC()
        self.load_commands()
        # users in chat
        self.chatters = None
        self.chatter_count = None
        self.update_chatters()

        self.last_poll_time = None

    def run(self):
        """ main run method """
        logging.info('Starting.')
        self.connect()
        try:
            self.listen()
        except KeyboardInterrupt:
            logging.info('Terminating bot.')
        finally:
            self.disconnect()

    def connect(self):
        """ handles logging into Twitch irc chat """
        logging.info('Connecting to %s' % self.channel)

        self.irc.connect(self.host, self.port)
        self.irc.password(self.password)
        self.irc.nick(self.username)
        self.irc.user(self.username)
        self.irc.join(self.channel)

        logging.info('Connected to %s' % self.channel)

    def disconnect(self):
        """ disconnects from Twitch irc chat """
        self.irc.close()

    def listen(self):
        """ listen to Twitch chat

            based on http://archive.oreilly.com/pub/h/1968
        """
        logging.info('Listening to %s.' % self.channel)

        readbuffer = ''
        while True:
            readbuffer += self.irc.recv()
            temp = readbuffer.split("\n")
            readbuffer = temp.pop()
            for line in temp:
                line = line.rstrip().split()
                if line[0] == "PING":
                    self.irc.pong(line[1])
                else:
                    self.process_data(line)
                    self.poll()

    def process_data(self, line):
        """ process data line and execute command if needed

        :param line: irc chat line
        """
        if len(line) <= 3:
            return

        sender = line[0].split('!')[0][1:]
        text = ' '.join(line[3:])[1:]
        # handle command
        if text.startswith('!'):
            logging.info('<%s> %s' % (sender, text))
            s = text.split()
            command = s[0][1:]
            arg = ' '.join(s[1:])
            self.process_command(sender, command, arg)

    def process_command(self, sender, command, argument):
        """ process command

        :param sender: username of command sender
        :param command: command name
        :param argument: command arguments
        """
        logging.info('Trying to handle command %s with %s sent by %s' % (command, argument, sender))

        if self.can_command():
            try:
                self.commands[command.lower()].execute(sender, argument)
                self.command_history.append((command, time.time()))
            except Exception as e:
                logging.warning('Unable to handle command %s: %s' % (command, str(e)))
        else:
            logging.warning('Too many commands, unable to process %s.' % command)

        # clean up command history to keep only commands in last 30 seconds
        self.command_history = list(itertools.dropwhile(lambda x: time.time()-x[1] > 30, self.command_history))

    def chat(self, msg):
        """ send message to channel

        :param msg: message to send to chat
        """
        self.irc.privmsg(self.channel, msg)

    def poll(self):
        """ update self data and execute periodic commands """
        if not self.last_poll_time:
            self.last_poll_time = time.time()

        # update viewer list
        elapsed_time = time.time() - self.last_poll_time
        if elapsed_time > 10:
            self.update_chatters()
            self.last_poll_time = time.time()

        # execute periodic commands
        for command in self.commands.values():
            if hasattr(command, 'periodic') and command.periodic:
                command.execute(None, None)

    def can_command(self):
        """ make sure bot doesn't do too many things too quickly """
        if len(self.command_history) > 0:
            now = time.time()
            return (len(self.command_history)/float((now-self.command_history[0][1]))) < 0.66
        else:
            return True

    def update_chatters(self):
        """ get users in channel """
        r = requests.get('http://tmi.twitch.tv/group/user/%s/chatters' % self.channel)
        if r.ok:
            j = r.json()
            self.chatter_count = j['chatter_count']
            self.chatters = j['chatters']

    def load_commands(self):
        """ instantiate a command object for each command in the commands directory """
        # load commands from command classes in commands directory
        class_members = inspect.getmembers(sys.modules['commands'], inspect.isclass)
        for m in class_members:
            if issubclass(m[1], commands.CommandBase):
                name = m[0].lower()
                self.commands[name] = m[1](self)

        logging.info('Loaded commands %s' % str(self.commands.keys()))


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Please provide a configuration file name!')
    else:
        try:
            with open(str(sys.argv[1])) as fh:
                config = yaml.load(fh)
        except IOError:
            print('Config file not found!')
            sys.exit(0)

        logging.basicConfig(filename='bcbbot.log', level=logging.DEBUG)
        d = BcbBot(config['username'], config['password'], config['channel'])
        d.run()
