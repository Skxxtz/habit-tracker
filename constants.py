from datetime import datetime

DEBUG = False

# Terminal constants
# https://gist.github.com/fnky/458719343aabd01cfb17a3a4f7296797
HIDE_CURSOR = "\033[?25l"
SHOW_CURSOR = "\033[?25h"
CLEAR_SCREEN = "\033[2J"
CURSOR_HOME = "\033[H"


# Globalize for efficiency since it won't change
TODAY = datetime.today()
DATEFORMAT = "%d-%m-%Y"
