from command_base import CommandBase

class Test(CommandBase):
    """ simple test command """

    def execute(self, sender, argument):
        """
        :param sender: name of the command executor
        :param argument: argument sent to command

        """
        if sender in self.bot.chatters.get('moderators', []):
            self.bot.chat("I'm here.")
