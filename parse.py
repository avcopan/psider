"""Module for extracting information from a string.
"""
import re
import numpy as np
from . import rehelper

class XYZString(object):
  """A container for a string containing cartesian coordinates.

  A helper for parsing a coordinate-containing string.  Assumes the coordinates
  are contained in the last block of more than two consecutive lines matching
  the given rehelper.XYZFinder.

  Attributes:
    string: A string containing a block of more than two consecutive lines that
      match xyzfinder.regex.
    xyzfinder: An rehelper.XYZFinder object.
    unitsfinder: A rehelper.UnitsFinder object.
    regex: Regex for finding the Cartesian coordinates within the string.
  """

  def __init__(self, string, xyzfinder = rehelper.XYZFinder(),
                             unitsfinder = rehelper.UnitsFinder()):
    self.string = string.replace('{', '{{').replace('}', '}}')
    self.xyzfinder = xyzfinder
    if not isinstance(self.xyzfinder, rehelper.XYZFinder):
      raise Exception("The 'xyzfinder' argument must be an instance of the "
                      "class rehelper.XYZFinder.")
    self.unitsfinder = unitsfinder
    self.regex = rehelper.two_or_more(xyzfinder.get_regex())
    start, end = self._get_last_match().span()
    self.head = self.string[:start]
    self.body = self.string[start:end]
    self.foot = self.string[end:]

  def extract_units(self):
    """Extract the units from `string`, if present.

    Returns:
      str: A string indicating the units, 'bohr' or 'angstrom'.
    """
    if not isinstance(self.unitsfinder, rehelper.UnitsFinder):
      raise Exception("This method requires the 'unitsfinder' attribute to be "
                      "an instance of the class rehelper.UnitsFinder.")
    regex = self.unitsfinder.get_units_regex()
    match = re.search(regex, self.string)
    if not match:
      raise Exception("Couldn't find a match for the units regex.")
    return match.group(1).lower()

  def extract_labels(self):
    """Extract the labels from the coordinate block.

    Returns:
      tuple: A tuple of atomic labels.
    """
    regex = self.xyzfinder.get_label_regex()
    return tuple(re.findall(regex, self.body))

  def extract_coordinates(self):
    """Extract coordinates from the coordinate block.

    Returns:
      numpy.ndarray: A numpy array of coordinates.
    """
    regex = self.xyzfinder.get_coordinates_regex()
    coordinates = np.array(re.findall(regex, self.body))
    return coordinates.astype(np.float)

  def replace_coordinates_with_placeholder(self, placeholder):
    """Replace coordinates in the coordinate block with a placeholder.

    Args:
      placeholder: The string to put in place of the coordinates

    Returns:
      str: A copy of `self.string`, with coordinates replaced by `placeholder`.
    """
    body = ''
    regex = self.xyzfinder.get_coordinates_inverse_regex()
    for line in self.body.splitlines():
      line += '\n'
      match = re.search(regex, line)
      if not match:
        body += line
      else:
        body += (placeholder).join(match.groups())
    return ''.join([self.head, body, self.foot])

  def _get_last_match(self):
    match = None
    for match in re.finditer(self.regex, self.string, re.MULTILINE):
      pass
    if not match:
      raise Exception("No Cartesian coordinates found in this string.")
    return match


def OutfileString(object):
  """A container for the job output file string.

  A helper for parsing a string containing the energy, and possibly also the
  gradient.
  """

  def __init__(self, string, energyfinder, successfinder, gradientfinder=None):
    self.string = self.string
    self.energyfinder = energyfinder
    if not isinstance(self.energyfinder, rehelper.EnergyFinder):
      raise Exception("The 'energyfinder' argument must be an instance of the "
                      "class rehelper.EnergyFinder.")
    self.successfinder = successfinder
    self.gradientfinder = gradientfinder


if __name__ == "__main__":
  from .molecule import Molecule
  from .options import Options
  # Build some helper objects.
  string = """
  { "bagel" : [

    {
      "title": "molecule",
      "symmetry": "c1",
      "basis": "svp",
      "df_basis": "svp-jkfit",
      "angstrom": false,
      "geometry": [
        {"atom": "O", "xyz": [0.000000000000, 0.000000000000,-0.000000000000] },
        {"atom": "H", "xyz": [0.000000000000,-0.000000000000, 1.000000000000] },
        {"atom": "H", "xyz": [0.000000000000, 1.000000000000, 1.000000000000] }
      ]
    },

    {
      "title" : "hf"
    }

  ]}
  """
  xyzregex = r' *{{"atom" *: *"@Atom", *"xyz" *: *\[ *@XCoord, *@YCoord, *@ZCoord *\] *}},? *\n'
  xyzfinder = rehelper.XYZFinder(xyzregex)
  xyzstring = XYZString(string, xyzfinder)
  # Make a molecule object from the coordinates contained in the template file.
  labels = xyzstring.extract_labels()
  coordinates = xyzstring.extract_coordinates()
  mol = Molecule(labels, coordinates)
  print(labels)
  print(coordinates)
  template = xyzstring.replace_coordinates_with_placeholder('{:.12f}')
  print(repr(template))
  c = list(coordinates.flatten())
  print(template.format(*c))
  print(template.format(*c) == string)
