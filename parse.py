"""Module for extracting information from a string.
"""
import re
import numpy as np
from . import rehelper

class CoordinateString(object):
  """A container for a string containing Cartesian coordinates.

  A helper for parsing a coordinate-containing string.  Assumes the coordinates
  are contained in the last block of more than two consecutive lines matching
  the given rehelper.CoordinatesFinder.

  Attributes:
    string: A string containing a block of more than two consecutive lines that
      match coordinatesfinder.get_regex().
    coordsfinder: An rehelper.CoordinatesFinder() object.
    unitsfinder: A rehelper.UnitsFinder object.
    body: The lines in `string` containing the Cartesian coordinates.
    head: The lines above the body.
    foot: The lines below the body.
  """

  def __init__(self, string, coordsfinder = rehelper.CoordinatesFinder(),
                             unitsfinder = rehelper.UnitsFinder()):
    self.string = string
    self.coordsfinder = coordsfinder
    if not isinstance(self.coordsfinder, rehelper.CoordinatesFinder):
      raise Exception("The 'coordsfinder' argument must be an instance of the "
                      "class rehelper.CoordinatesFinder.")
    self.unitsfinder = unitsfinder
    # Split the string into a head, a foot, and a body containing the 
    regex = self.coordsfinder.get_regex()
    match = rehelper.get_last_match(regex, self.string, re.MULTILINE)
    start, end = match.span()
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
    regex = self.coordsfinder.linefinder.get_label_regex()
    return tuple(re.findall(regex, self.body))

  def extract_coordinates(self):
    """Extract coordinates from the coordinate block.

    Returns:
      numpy.ndarray: A numpy array of coordinates.
    """
    regex = self.coordsfinder.linefinder.get_coordinates_regex()
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
    regex = self.coordsfinder.linefinder.get_coordinates_inverse_regex()
    for line in self.body.splitlines():
      line += '\n'
      match = re.search(regex, line)
      if not match:
        body += line
      else:
        body += (placeholder).join(match.groups())
    return ''.join([self.head, body, self.foot])


def EnergyString(object):
  """A container for a string containing the energy, and possibly the gradient.

  Attributes:
  """

  def __init__(self, string, successregex, energyfinder,
               gradheader = None, gradlinefinder = None, gradfooter = None):
    self.string = self.string
    self.successregex = successregex
    self.energyfinder = energyfinder
    if not isinstance(self.energyfinder, rehelper.EnergyFinder):
      raise Exception("The 'energyfinder' argument must be an instance of the "
                      "class rehelper.EnergyFinder.")
    self.gradlinefinder = gradientfinder
    if not isinstance(self.energyfinder, rehelper.EnergyFinder):
      raise Exception("The 'energyfinder' argument must be an instance of the "
                      "class rehelper.EnergyFinder.")


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
  rstring = string.replace('{', '{{').replace('}', '}}')
  linefinder = rehelper.CoordinatesLineFinder(r' *{{"atom" *: *"@Atom", *"xyz" *: *\[ *@XCoord, *@YCoord, *@ZCoord *\] *}},? *\n')
  print(linefinder)
  coordsfinder = rehelper.CoordinatesFinder(linefinder)
  coordstring = CoordinateString(rstring, coordsfinder)
  labels = coordstring.extract_labels()
  coordinates = coordstring.extract_coordinates()
  print(labels)
  print(coordinates)
  template = coordstring.replace_coordinates_with_placeholder('{:.12f}')
  print(template)
  c = list(coordinates.flatten())
  print(template.format(*c))
  print(template.format(*c) == string)
