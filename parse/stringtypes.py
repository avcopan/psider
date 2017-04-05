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
    string: A string containing a block that matches coords_finder.get_regex().
    coords_finder: An rehelper.CoordinateFinder object.
    units_finder: A rehelper.UnitsFinder object.
    _body: The lines in `string` containing the Cartesian coordinates.
    _head: The lines above the body.
    _foot: The lines below the body.
  """

  def __init__(self, string, coords_finder = rehelper.CoordinateFinder(),
                             units_finder = rehelper.UnitsFinder()):
    self.string = string
    self.coords_finder = coords_finder
    if not isinstance(self.coords_finder, rehelper.CoordinateFinder):
      raise ValueError("The 'coords_finder' argument must be an instance of the "
                       "class rehelper.CoordinateFinder.")
    self.units_finder = units_finder
    # Split the string into a head, a foot, and a body containing the geometry.
    regex = self.coords_finder.get_regex()
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
    if not isinstance(self.units_finder, rehelper.UnitsFinder):
      raise ValueError("This method requires the 'units_finder' attribute to be "
                       "an instance of the class rehelper.UnitsFinder.")
    regex = self.units_finder.get_units_regex()
    match = rehelper.get_last_match(regex, self.string)
    if not match:
      raise ValueError("Couldn't find a match for the units regex.")
    return match.group(1).lower()

  def extract_labels(self):
    """Extract the labels from the body.

    Returns:
      tuple: A tuple of atomic labels.
    """
    regex = self.coords_finder.line_finder.get_label_regex()
    return tuple(re.findall(regex, self._body))

  def extract_coordinates(self):
    """Extract coordinates from the body.

    Returns:
      numpy.ndarray: A numpy array of coordinates.
    """
    regex = self.coords_finder.line_finder.get_coordinates_regex()
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
    regex = self.coords_finder.line_finder.get_coordinates_inverse_regex()
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
    energy_finder: An rehelper.EnergyFinder object.
    success_regex: A regex that matches `string` if the job ran successfully.
  """

  def __init__(self, string, energy_finder, success_regex = None):
    self.string = string
    self.success_regex = success_regex
    self.energy_finder = energy_finder
    if not isinstance(self.energy_finder, rehelper.EnergyFinder):
      raise ValueError("The 'energy_finder' argument must be an instance of the "
                       "class rehelper.EnergyFinder.")

  def extract_energy(self):
    """Extract the energy from `string`.

    Returns:
      float: The last energy found in the string.
    """
    regex = self.energy_finder.get_energy_regex()
    match = rehelper.get_last_match(regex, self.string)
    if not match:
      raise ValueError("Couldn't find a match for the energy regex.")
    return float(match.group(1))

  def check_success(self):
    """Determine success value.

    Returns:
      bool: Whether or not `self.success_regex` has a match.
    """
    if not isinstance(self.success_regex, str):
      raise ValueError("This method requires the 'success_regex' attribute to "
                       "be set to a string value.")
    match = re.search(self.success_regex, self.string)
    return bool(match)

class GradientString(object):
  """A container for a string containing the gradient.

  Attributes:
    string: A string containing a block that matches grad_finder.get_regex().
    grad_finder: An rehelper.GradientFinder object.
    _body: The lines in `string` containing the Gradient.
    _head: The lines above the body.
    _foot: The lines below the body.
  """

  def __init__(self, string, grad_finder):
    self.string = string
    self.grad_finder = grad_finder
    if not isinstance(self.grad_finder, rehelper.GradientFinder):
      raise ValueError("The 'grad_finder' argument must be an instance of the "
                       "class rehelper.GradientFinder.")
    # Split the string into a head, a foot, and a body containing the gradient.
    regex = self.grad_finder.get_regex()
    match = rehelper.get_last_match(regex, self.string, re.MULTILINE)
    start, end = match.span()
    self._head = self.string[:start]
    self._body = self.string[start:end]
    self._foot = self.string[end:]

  def extract_gradient(self):
    """Extract the gradient from the body.
    """
    regex = self.grad_finder.line_finder.get_gradient_regex()
    gradient = np.array(re.findall(regex, self._body))
    return gradient.astype(np.float)


if __name__ == "__main__":
  string = open('output.dat').read()
  energy_finder = rehelper.EnergyFinder(r' *Total Energy *= *@Energy *\n')
  success_regex = r'\*\*\* P[Ss][Ii]4 exiting successfully.'
  energy_string = EnergyString(string, energy_finder, success_regex)
  print(energy_string.extract_energy())
  print(energy_string.check_success())
  regex = r' +\d +@XGrad +@YGrad +@ZGrad *\n'
  head = r'-Total Gradient: *\n +Atom +X +Y +Z *\n.*\n'
  foot = ''
  grad_finder = rehelper.GradientFinder(regex, head, foot)
  grad_string = GradientString(string, grad_finder)
  print(grad_string.extract_gradient())
