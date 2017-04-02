import re
from . import regex
from .options import Options
from .molecule import Molecule

class InputFile(object):
  """An input file object.

  A formatable template for an input file that can place coordinates in the
  proper location in the input file.
  """

  def __init__(self, template_string):
    self.template_string = template_string

  def make_input(self, geometry_array):
    """
    Generates an input_file string with the geometry replaced by the
    geometry_array.
    """
    coordinates = list(geometry_array.flatten())
    return self.template_string.format(*coordinates)
    

    


if __name__ == "__main__":
  options = Options()
  string = open('template.dat').read()
  tmp = TemplateFileProcessor(string, options)
