from ollama_test import Conversation

prompt = """
import numpy as np
from matplotlib import pyplot as plt

def compute_ground_state_energy_of_atom(protons=1):
    # TODO
    return energy # in eV

compute_ground_state_energy_of_atom(1)
compute_ground_state_energy_of_atom(2)

"""


coder = Conversation("qwen2.5-coder:32b")
thinker = Conversation("deepseek-r1:32b")

DEFAULT = '\033[0m'; BOLD = '\033[1m';ITALIC = '\033[3m';UNDERLINE = '\033[4m';UNDERLINE_THICK = '\033[21m';HIGHLIGHTED = '\033[7m';HIGHLIGHTED_BLACK = '\033[40m';HIGHLIGHTED_RED = '\033[41m';HIGHLIGHTED_GREEN = '\033[42m';HIGHLIGHTED_YELLOW = '\033[43m';HIGHLIGHTED_BLUE = '\033[44m';HIGHLIGHTED_PURPLE = '\033[45m';HIGHLIGHTED_CYAN = '\033[46m';HIGHLIGHTED_GREY = '\033[47m';HIGHLIGHTED_GREY_LIGHT = '\033[100m';HIGHLIGHTED_RED_LIGHT = '\033[101m';HIGHLIGHTED_GREEN_LIGHT = '\033[102m';HIGHLIGHTED_YELLOW_LIGHT = '\033[103m';HIGHLIGHTED_BLUE_LIGHT = '\033[104m';HIGHLIGHTED_PURPLE_LIGHT = '\033[105m';HIGHLIGHTED_CYAN_LIGHT = '\033[106m';HIGHLIGHTED_WHITE_LIGHT = '\033[107m';STRIKE_THROUGH = '\033[9m';MARGIN_1 = '\033[51m';MARGIN_2 = '\033[52m';BLACK = '\033[30m';RED_DARK = '\033[31m';GREEN_DARK = '\033[32m';YELLOW_DARK = '\033[33m';BLUE_DARK = '\033[34m';PURPLE_DARK = '\033[35m';CYAN_DARK = '\033[36m';GREY_DARK = '\033[37m';BLACK_LIGHT = '\033[90m';RED = '\033[91m';GREEN = '\033[92m';YELLOW = '\033[93m';BLUE = '\033[94m';PURPLE = '\033[95m';CYAN = '\033[96m';WHITE = '\033[97m'  # noqa
echo = lambda values, color: print("%s%s%s" % (color, values, DEFAULT)) if color else print("%s%s" % (values, DEFAULT))

thought = thinker.prompt("Please help guide me to fill out this skeleton code: \n\n" + prompt)
echo(thought, BLUE)
code = coder.prompt("Please write code based on the following instructions: \n\n" + thought)
echo(code, RED)
thought = thinker.prompt("Please advise if you think this code is a complete solution or not.  Please give your answer as only a simple \"Yes\" or \"No\" with no further detail or explanation.\n\n" + code)
echo(thought, BLUE)

    
