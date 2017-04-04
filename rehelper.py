"""Regex helper module.

Defines some helpers for defining regular expressions.
"""
import re

#Module-level variables.
float_           = r'-?\d+\.\d+'
atomic_symbol    = r'[a-zA-Z]{1,4}'
word             = r'[a-zA-Z]{2,}'


#Module functions.
def capture(string):
  return r'({:s})'.format(string)

def two_or_more(string):
  return r'(?:{:s}){{2,}}'.format(string)

def get_last_match(pattern, string, flags = 0):
  match = None
  for match in re.finditer(pattern, string, flags):
    pass
  if not match:
    raise ValueError("No match found in string.")
  return match


#Module classes.
class UnitsFinder(object):
  """Helper for processing line in a coordinate string indicating its units.

  Attributes:
    regex: Regex for finding the line that indicates the units ('bohr' or
      'angstrom') of the molecular geometry.  Contains the placeholder
      '@Units' at the position of the units in the string, and ends in ' *\n'.
  """
  def __init__(self, regex = ' *units +@Units *\n'):
    self.regex = regex
    if not '@Units' in self.regex:
      raise ValueError("This regex must contain the placeholder @Units.")

  def get_units_regex(self):
    """Return capturing units line regex.
    """
    return re.sub('@Units', capture(word), self.regex)


class CoordinatesLineFinder(object):
  """Helper for processing coordinate-containing lines in a string.

  Attributes:
    regex: Regex for finding a line containing Cartesian coordinates. Contains
      the placeholders '@Atom', '@XCoord', '@YCoord', and '@ZCoord' at the
      positions of the atomic symbol and its associated coordinate values in the
      string. Always must end in a newline.
  """
  def __init__(self, regex = ' *@Atom +@XCoord +@YCoord +@ZCoord *\n'):
    self.regex = regex
    placeholders = ('@Atom', '@XCoord', '@YCoord', '@ZCoord')
    if not all(placeholder in self.regex for placeholder in placeholders):
      raise ValueError("This regex must contain the following placeholders: "
                       "@Atom, @XCoord, @YCoord, @ZCoord.")

  def get_regex(self):
    """Return non-capturing XYZ line regex.
    """
    ret = re.sub('@Atom', atomic_symbol, self.regex)
    ret = re.sub('@.Coord', float_, ret)
    return ret

  def get_label_regex(self):
    """Return XYZ line regex capturing the atom label.
    """
    ret = re.sub('@Atom', capture(atomic_symbol), self.regex)
    ret = re.sub('@.Coord', float_, ret)
    return ret

  def get_coordinates_regex(self):
    """Return XYZ line regex capturing all of the coordinates.
    """
    ret = re.sub('@Atom', atomic_symbol, self.regex)
    ret = re.sub('@.Coord', capture(float_), ret)
    return ret

  def get_coordinates_inverse_regex(self):
    """Return XYZ line regex capturing everything but the coordinates.
    """
    ret = re.sub('@Atom', atomic_symbol, self.regex)
    parts = re.sub('.Coord', '', ret).split('@')
    ret = (float_).join(capture(part) for part in parts)
    return ret

class CoordinatesFinder(object):
  """Helper for grabbing the coordinates from a string.

  Attributes:
    linefinder: A CoordinatesLineFinder object.
    header: Text immediately preceding the coordinates.
    footer: Text immediately following the coordinates.
  """

  def __init__(self, linefinder = CoordinatesLineFinder(),
                     header = '', footer = ''):
    self.linefinder = linefinder
    self.header = str(header)
    self.footer = str(footer)
    if not isinstance(self.linefinder, CoordinatesLineFinder):
      raise ValueError("The 'linefinder' argument must be an instance of "
                       "the CoordinatesLineFinder class.")

  def get_regex(self):
    """Return non-capturing gradient regex.
    """
    ret = self.header
    ret += two_or_more(self.linefinder.get_regex())
    ret += self.footer
    return ret


class EnergyFinder(object):
  """Helper for processing the line in an output string containing the energy.

  Attributes:
    regex: Regex for finding the energy in the output file.  Must contain the
      placeholder @Energy and end in a newline character.
  """
  def __init__(self, regex):
    self.regex = regex
    if not '@Energy' in self.regex:
      raise ValueError("This regex must contain the placeholder @Energy.")

  def get_energy_regex(self):
    """Return capturing energy regex.
    """
    return re.sub('@Energy', capture(float_), self.regex)


class GradientLineFinder(object):
  """Helper for grabbing the lines in a string containing the gradient.

  Attributes:
    regex: Regex for finding a line containing elements of the gradient.  Must
      contain the placeholders '@XGrad', '@YGrad', and '@ZGrad' and end in
      a newline.
  """
  def __init__(self, regex):
    self.regex = regex
    placeholders = ('@XGrad', '@YGrad', '@ZGrad')
    if not all(placeholder in self.regex for placeholder in placeholders):
      raise ValueError("This regex must contain the following placeholders: "
                       "@XGrad, @YGrad, @ZGrad.")

  def get_regex(self):
    """Return non-capturing gradient line regex.
    """
    ret = re.sub('@.Grad', float_, self.regex)
    return ret

  def get_gradient_line_regex(self):
    """Return capturing gradient line regex.
    """
    ret = re.sub('@.Grad', capture(float_), self.regex)
    return ret


class GradientFinder(object):
  """Helper for grabbing the gradient from a string.

  Attributes:
    linefinder: A GradientLineFinder object.
    header: Text immediately preceding the gradient lines.
    footer: Text immediately following the gradient lines.
  """
  def __init__(self, linefinder, header = '', footer = ''):
    self.linefinder = linefinder
    self.header = str(header)
    self.footer = str(footer)
    if not isinstance(self.linefinder, GradientLineFinder):
      raise ValueError("The 'linefinder' argument must be an instance of "
                       "the GradientLineFinder class.")

  def get_regex(self):
    """Return non-capturing gradient regex.
    """
    ret = self.header
    ret += two_or_more(self.linefinder.get_regex())
    ret += self.footer
    return ret


if __name__ == "__main__":
  s = open('output.dat').read()
  linefinder = GradientLineFinder(r' +\d +@XGrad +@YGrad +@ZGrad *\n')
  header = r'-Total Gradient: *\n +Atom +X +Y +Z *\n.*\n'
  footer = ''
  gradientfinder = GradientFinder(linefinder, header, footer)
  regex = gradientfinder.get_regex()
  
