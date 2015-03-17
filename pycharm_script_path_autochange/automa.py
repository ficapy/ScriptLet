from automa.api import *
from sys import argv

switch_to("pycharm")
click(Point(1206,58))
click(Point(1206,76))
#script path
click(Point(1023,149))
press(CTRL + 'a')
press(BKSP)
write(argv[-1])
#click OK
click(Point(960,707))
