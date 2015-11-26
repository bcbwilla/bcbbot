from command_base import CommandBase

class Echo(CommandBase):
    """ repeats the argument in chat if executed by a mod """
    def execute(self, sender, argument):
        if sender in self.bot.chatters.get('moderators', []):
            self.bot.chat(argument)