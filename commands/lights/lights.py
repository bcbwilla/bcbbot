import re
import time

from phue import Bridge, PhueException

from .. import CommandBase

class Lights(CommandBase):

    def __init__(self, bot, **kwargs):
        super(Lights, self).__init__(bot)

        # connect
        self.last_run_time = time.time()
        self.b = self.setup()

    def execute(self, sender, argument):
        if not self.b or not self.setup():
            self.bot.chat("Can't connect to lights.")

        elif self.can_run(sender):
            color_tuple = self.to_rgb_tuple(argument)
            if color_tuple:
                self.change_lights(*color_tuple)
                self.bot.chat('Lights successfully updated.')
                self.last_run_time = time.time()
            else:
                self.bot.chat('%s not available.' % argument)

    def to_rgb_tuple(self, s):
        """ try to convert input to rgb tuple
        :param s: argument string
        :return: (r, g, b) tuple if possible, else None
        """
        # a few basic colors
        colors = {
            'red': (255, 0, 0),
            'green': (0, 255, 0),
            'blue': (0, 0, 255),
            'pink': (255, 192, 203),
            'purple': (128, 0, 128),
            'yellow': (255, 255, 0),
            'orange': (255, 128, 0),
            'white': (255, 255, 255),
        }

        # case of use passing in name of color
        if s in colors.keys():
            return colors[s]

        # some form of (r,g,b) input
        matches = re.search(r'(\d+)\D+(\d+)\D+(\d+)', s)
        if len(matches.groups()) == 3:
            try:
                return map(float, matches.groups())
            except ValueError:
                return

    def setup(self):
        try:
            self.b = Bridge(self.bridge_ip)
            self.b.connect()
            return self.b
        except PhueException as e:
            print('Unable to connect to hue: %s' % str(e))
            return

    def change_lights(self, r, g, b):
        for light in self.b.lights:
            light.xy = self.rgb_to_xy(r, g, b)

    def rgb_to_xy(self, r, g, b):
        # http://www.everyhue.com/vanilla/discussion/94/rgb-to-xy-or-hue-sat-values
        X = 1.076450*r - 0.237662*g + 0.161212*b
        Y = 0.410964*r + 0.554342*g + 0.034694*b
        Z = -0.010954*r - 0.013389*g + 1.024343*b
        return [X/(X+Y+Z), Y/(X+Y+Z)]

