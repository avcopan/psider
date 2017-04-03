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
      raise Exception("This regex must contain the placeholder @Units.")

  def get_units_regex(self):
    """Return capturing units line regex.
    """
    return re.sub('@Units', capture(word), self.regex)


class EnergyFinder(object):
  """Helper for processing line in an output string containing the energy.

  Attributs:
    energy_regex: Regex for finding the energy in the output file.  Must
      contain the placeholder @Energy and end in a newline character.
  """
  def __init__(self, regex):
    self.regex = regex
    if not '@Energy' in self.regex:
      raise Exception("This regex must contain the placeholder @Energy.")

  def get_energy_regex(self):
    """Return capturing energy regex.
    """
    return re.sub('@Energy', capture(float_), self.regex)


class XYZFinder(object):
  """Helper for processing coordinate-containing lines in a string.

  Attributes:
    regex: Regex for finding a line containing Cartesian coordinates. Contains
      the placeholders '@Atom', '@XCoord', '@YCoord', and '@ZCoord' at the
      positions of the atomic symbol and its associated coordinate values in the
      string. Always must end in ' *\n'.
  """
  def __init__(self, regex = ' *@Atom +@XCoord +@YCoord +@ZCoord *\n'):
    self.regex = regex
    placeholders = ('@Atom', '@XCoord', '@YCoord', '@ZCoord')
    if not all(placeholder in self.regex for placeholder in placeholders):
      raise Exception("This regex must contain the following placeholders: "
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
