import pickle

from command_base import CommandBase

class BcbCommand(CommandBase):
    """ a command for dynamically creating new commands at runtime

        created commands are persisted between sessions via pickle
    """

    def __init__(self, bot, **kwargs):
        super(BcbCommand, self).__init__(bot)

        # file where dynamic commands are persisted
        self.dynamic_command_file = '.dynamic_commands.p'
        self.commands = {}
        self.load_dynamic_commands()

    def execute(self, sender, argument):
        if sender in self.bot.chatters.get('moderators', []):
            arguments = argument.split()

            if len(arguments) < 2:
                self.bot.chat('Please provide at least 2 arguments.')
                return

            action, name, msg = arguments[0], arguments[1], ' '.join(arguments[2:])
            if action == 'remove' and name in self.bot.commands.keys():
                self.remove_command(name)
                self.bot.chat('Removed command %s' % name)

            elif action == 'set':
                self.add_command(name, msg)
                self.bot.chat('Added command %s: %s' % (name, msg))

    def create_dyanmic_command_object(self, name, msg):
        """ create a new command class of name "name" and instantiate object

        :param name: name of the command
        :param msg: chat message that the command will display
        :return: <name_command> class object
        """
        command = type(name, (CommandBase,), dict())

        # add the execute command to print out the desired message
        def ex(self, sender, argument):
            self.bot.chat(self.msg)

        setattr(command, 'execute', ex)
        return command(self.bot, msg=msg)

    def add_command(self, name, msg):
        """ add command of name "name" to available commands
        :param name: name of command
        :param msg: chat message that the command will display
        """
        self.commands[name] = msg
        self.bot.commands[name] = self.create_dyanmic_command_object(name, msg)
        self.persist_commands()

    def remove_command(self, name):
        """ remove command

        :param name: name of command
        """
        try:
            self.bot.commands.pop(name)
            self.commands.pop(name)
            self.persist_commands()
        except Exception as e:
            print e

    def persist_commands(self):
        """ persist current dynamic commands via pickle """
        with open(self.dynamic_command_file, 'wb') as fh:
            pickle.dump(self.commands, fh)

    def load_dynamic_commands(self):
        """ unpickle saved dynamic commands """
        try:
            with open(self.dynamic_command_file) as fh:
                for name, msg in pickle.load(fh).items():
                    self.add_command(name, msg)

        except IOError:
            open(self.dynamic_command_file, 'a').close()
        except EOFError:  # empty command file
            pass

