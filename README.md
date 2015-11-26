# bcbbot
A light, pluginabble Twitch chat bot.

## Useage
1. Make sure you have python and setuptools installed. You're best doing this in a virtual 
environment
2. Make a proper config file with your auth keys and stuff. See `example_config.py`.
3. `python setup.py install`
4. `python bot.py config.yaml`


## Another Twitch Bot? Really? Why?
Yeah.

1. I had started playing with scraping Twitch chats for a project, and I thought I would generalize 
the bot I was using a little bit in case anyone wanted to play with it
2. Couldn't really find a simple bot that you could easily add plugins to (I didn't look very hard 
because it seemed fun to make my own)

## Why not use bot XYZ?
I do. This doesn't come with any actual useful features - you're on your own to implement those. 
(Share them if you do and they are neat!). I don't have any plans to reproduce the wonderful mod 
features of the standard bots. I'm only using this to do silly things like notify the chat when
my tea is done.


## Adding Commands
Commands go in the `commands` folder. There are a couple things you need to do to make sure your
command is properly loaded when the bot starts:

1. Commands should inherit from the `CommandBase` class.
2. The name of the python file and class name should be the same name as the command as you run it
in chat.

You can put any configuration information you want for a command in the `commands.yaml` file. Just
put them under a section named the same as your command.