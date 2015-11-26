class CommandBase(object):
    """ the base object which all commands should subclass

        the execute method should be overridden with desired functionality
    """

    def __init__(self, bot, **kwargs):
        self.bot = bot

        for k, v in kwargs.items():
            setattr(self, k, v)

    def execute(self, sender, argument):
        pass
