"""Module for extracting information from a string.
"""
import re
import numpy as np
from . import rehelper

class CoordinateString(object):
  """A container for a string containing Cartesian coordinates.

  A helper for parsing a coordinate-containing string.  Assumes the coordinates
  are contained in the last block of more than two consecutive lines matching
  the given rehelper.CoordinateFinder.

  Attributes:
    string: A string containing a block that matches coordsfinder.get_regex().
    coordsfinder: An rehelper.CoordinateFinder object.
    unitsfinder: A rehelper.UnitsFinder object.
    _body: The lines in `string` containing the Cartesian coordinates.
    _head: The lines above the body.
    _foot: The lines below the body.
  """

  def __init__(self, string, coordsfinder = rehelper.CoordinateFinder(),
                             unitsfinder = rehelper.UnitsFinder()):
    self.string = string
    self.coordsfinder = coordsfinder
    if not isinstance(self.coordsfinder, rehelper.CoordinateFinder):
      raise ValueError("The 'coordsfinder' argument must be an instance of the "
                       "class rehelper.CoordinateFinder.")
    self.unitsfinder = unitsfinder
    # Split the string into a head, a foot, and a body containing the geometry.
    regex = self.coordsfinder.get_regex()
    match = rehelper.get_last_match(regex, self.string, re.MULTILINE)
    start, end = match.span()
    self._head = self.string[:start]
    self._body = self.string[start:end]
    self._foot = self.string[end:]

  def extract_units(self):
    """Extract the units from `string`, if present.

    Returns:
      str: A string indicating the units, 'bohr' or 'angstrom'.
    """
    if not isinstance(self.unitsfinder, rehelper.UnitsFinder):
      raise ValueError("This method requires the 'unitsfinder' attribute to be "
                       "an instance of the class rehelper.UnitsFinder.")
    regex = self.unitsfinder.get_units_regex()
    match = rehelper.get_last_match(regex, self.string)
    if not match:
      raise ValueError("Couldn't find a match for the units regex.")
    return match.group(1).lower()

  def extract_labels(self):
    """Extract the labels from the body.

    Returns:
      tuple: A tuple of atomic labels.
    """
    regex = self.coordsfinder.linefinder.get_label_regex()
    return tuple(re.findall(regex, self._body))

  def extract_coordinates(self):
    """Extract coordinates from the body.

    Returns:
      numpy.ndarray: A numpy array of coordinates.
    """
    regex = self.coordsfinder.linefinder.get_coordinates_regex()
    coordinates = np.array(re.findall(regex, self._body))
    return coordinates.astype(np.float)

  def replace_coordinates_with_placeholder(self, placeholder):
    """Replace coordinates in the body with a placeholder.

    Args:
      placeholder: The string to put in place of the coordinates

    Returns:
      str: A copy of `self.string`, with coordinates replaced by `placeholder`.
    """
    body = ''
    regex = self.coordsfinder.linefinder.get_coordinates_inverse_regex()
    for line in self._body.splitlines():
      line += '\n'
      match = re.search(regex, line)
      if not match:
        body += line
      else:
        body += (placeholder).join(match.groups())
    return ''.join([self._head, body, self._foot])


class EnergyString(object):
  """A container for a string containing the energy.

  Attributes:
    string: A string containing the energy.
    energyfinder: An rehelper.EnergyFinder object.
    successregex: A regex that matches `string` if the job ran successfully.
  """

  def __init__(self, string, energyfinder, successregex = None):
    self.string = string
    self.successregex = successregex
    self.energyfinder = energyfinder
    if not isinstance(self.energyfinder, rehelper.EnergyFinder):
      raise ValueError("The 'energyfinder' argument must be an instance of the "
                       "class rehelper.EnergyFinder.")

  def extract_energy(self):
    """Extract the energy from `string`.

    Returns:
      float: The last energy found in the string.
    """
    regex = self.energyfinder.get_energy_regex()
    match = rehelper.get_last_match(regex, self.string)
    if not match:
      raise ValueError("Couldn't find a match for the energy regex.")
    return float(match.group(1))

  def check_success(self):
    """Determine success value.

    Returns:
      bool: Whether or not `self.successregex` has a match.
    """
    if not isinstance(self.successregex, str):
      raise ValueError("This method requires the 'successregex' attribute to "
                       "be set to a string value.")
    match = re.search(self.successregex, self.string)
    return bool(match)

class GradientString(object):
  """A container for a string containing the gradient.

  Attributes:
    string: A string containing a block that matches gradfinder.get_regex().
    gradfinder: An rehelper.GradientFinder object.
    _body: The lines in `string` containing the Gradient.
    _head: The lines above the body.
    _foot: The lines below the body.
  """

  def __init__(self, string, gradfinder):
    self.string = string
    self.gradfinder = gradfinder
    if not isinstance(self.gradfinder, rehelper.GradientFinder):
      raise ValueError("The 'gradfinder' argument must be an instance of the "
                       "class rehelper.GradientFinder.")
    # Split the string into a head, a foot, and a body containing the gradient.
    regex = self.gradfinder.get_regex()
    match = rehelper.get_last_match(regex, self.string, re.MULTILINE)
    start, end = match.span()
    self._head = self.string[:start]
    self._body = self.string[start:end]
    self._foot = self.string[end:]

  def extract_gradient(self):
    """Extract the gradient from the body.
    """
    regex = self.gradfinder.linefinder.get_gradient_regex()
    gradient = np.array(re.findall(regex, self._body))
    return gradient.astype(np.float)


if __name__ == "__main__":
  string = open('output.dat').read()
  energyfinder = rehelper.EnergyFinder(r' *Total Energy *= *@Energy *\n')
  successregex = r'\*\*\* P[Ss][Ii]4 exiting successfully.'
  energystring = EnergyString(string, energyfinder, successregex)
  print(energystring.extract_energy())
  print(energystring.check_success())
  regex = r' +\d +@XGrad +@YGrad +@ZGrad *\n'
  head = r'-Total Gradient: *\n +Atom +X +Y +Z *\n.*\n'
  foot = ''
  gradfinder = rehelper.GradientFinder(regex, head, foot)
  gradstring = GradientString(string, gradfinder)
  print(gradstring.extract_gradient())
