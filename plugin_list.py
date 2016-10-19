from TCI.plugins.CalculatorPlot import CalculatorPlot
from TCI.plugins.MohrCircles import MohrCircles
from TCI.plugins.ComboList import ComboList
from TCI.plugins.SonicInterpreter import SonicInterpreter

def get_plugin_list():
    return CalculatorPlot, MohrCircles, ComboList, SonicInterpreter
