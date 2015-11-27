import time
import glob

import yaml

class CommandBase(object):
    """ the base object which all commands should subclass

        the execute method should be overridden with desired functionality
    """

    def __init__(self, bot, **kwargs):
        self.bot = bot

        # standard default settings, can be overwritten via config
        self.cooldown = 0
        self.mod_only = False
        self.last_run_time = 0

        kwargs.update(self.load_config())
        for k, v in kwargs.items():
            setattr(self, k, v)

    def load_config(self):
        class_name = self.__class__.__name__.lower()
        config = [c for c in glob.glob("commands/**/*.yaml") if class_name in c]
        try:
            with open(config[0], 'r') as f:
                return yaml.load(f)
        except (IOError, IndexError):
            return {}

    def can_run(self, sender):
        is_cool = (time.time() - self.last_run_time) > self.cooldown
        if self.mod_only:
            return self.is_mod(sender)
        else:
            return is_cool or self.is_mod(sender)

    def is_mod(self, sender):
        return sender in self.bot.chatters.get('moderators', [])

    def execute(self, sender, argument):
        pass
