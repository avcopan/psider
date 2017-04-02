import re
import numpy as np
from . import regex
from .molecule import Molecule
from .input import InputFile


class XYZLine(object):
  """Helper for processing coordinate-containing lines in the input file.

  Attributes:
    xyz_regex: Regex that finds Cartesian coordinates in the template file.
      Must contain @AtomicSymbol, @XCoord, @YCoord, and @ZCoord, indicating
      the positions of the atomic symbol and its associated coordinate values.
      If the line contains brackets, they must be doubled (i.e. replace '{'
      with '{{')
  """
  def __init__(self, xyz_regex):
    self.xyz_regex = xyz_regex

  def capture_none(self):
    """Return non-capturing XYZ line regex.
    """
    ret = self.xyz_regex
    ret = re.sub('@AtomicSymbol', regex.atomic_symbol, ret)
    ret = re.sub('@.Coord', regex.float_, ret)
    return ret

  def capture_label(self):
    """Return XYZ line regex capturing the atom label.
    """
    ret = self.xyz_regex
    ret = re.sub('@AtomicSymbol', regex.capture(regex.atomic_symbol), ret)
    ret = re.sub('@.Coord', regex.float_, ret)
    return ret

  def capture_coords(self):
    """Return XYZ line regex capturing all of the coordinates.
    """
    ret = self.xyz_regex
    ret = re.sub('@AtomicSymbol', regex.atomic_symbol, ret)
    ret = re.sub('@.Coord', regex.capture(regex.float_), ret)
    return ret


def process_template_file(string, options):
  """Process the contents of the input file template.

  Extract coordinates from the template file and reformat it for filling in new
  coordinates.

  Args:
    string: A string holding the contents of the template file
    options: An optavc Options object

  Returns:
    A Molecule object containing the molecule extracted from the template file.
    An InputFile object containing the fillable template string.
  """
  # Replace any curly braces with double braces to prevent formatting them
  string = string.replace('{', '{{').replace('}', '}}')
  # Identify the part of the input file that contains the geometry
  xyzline = XYZLine(options.xyz_regex)
  body_regex = regex.two_or_more(xyzline.capture_none())
  match = None
  for match in re.finditer(body_regex, string, re.MULTILINE):
    pass
  if not match:
    raise Exception("Cannot find Cartesian coordinates in template file.  "
                    "Did you remember to set the 'xyz_regex' option?")
  start, end = match.start(), match.end()
  # Split the file into a header, a footer, and a body containing the geometry
  header, body, footer = string[:start], string[start:end], string[end:]
  # Build a Molecule object
  units = options.input_units
  labels = re.findall(xyzline.capture_label(), body)
  coordinates = np.array([
    [float(coord) for coord in match.groups()]
    for match in re.finditer(xyzline.capture_coords(), body)])
  mol = Molecule(labels, coordinates, units)
  print(mol)
  # Build an InputFile object
  


if __name__ == "__main__":
  from .options import Options
  process_template_file(open('template.dat').read(), Options())
