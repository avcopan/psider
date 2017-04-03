import re
import numpy as np
from . import rehelper


class UnitsFinder(object):
  """Helper for processing line in a coordinate string indicating its units.

  Attributes:
    regex: Regex for finding the line that indicates the units ('bohr' or
      'angstrom') of the molecular geometry.  Contains the placeholder
      '@Units' at the position of the units in the string, and ends in ' *\n'.
  """
  def __init__(self, regex = ' *units +@Units *\n'):
    self.regex = regex

  def get_units_regex(self):
    """Return capturing units line regex.
    """
    return re.sub('@Units', rehelper.capture(rehelper.word), self.regex)

  def get_units(self, string):
    match = re.search(self.get_units_regex(), string)
    if not match:
      raise Exception('No match found for this regex.')
    return match.group(1).lower()


class XYZFinder(object):
  """Helper for processing coordinate-containing lines in a file string.

  Attributes:
    regex: Regex for finding a line containing Cartesian coordinates. Contains
      the placeholders '@Atom', '@XCoord', '@YCoord', and '@ZCoord' at the
      positions of the atomic symbol and its associated coordinate values in the
      string. Always must end in ' *\n'.
  """
  def __init__(self, regex = ' *@Atom +@XCoord +@YCoord +@ZCoord *\n'):
    self.regex = regex

  def get_regex(self):
    """Return non-capturing XYZ line regex.
    """
    ret = re.sub('@Atom', rehelper.atomic_symbol, self.regex)
    ret = re.sub('@.Coord', rehelper.float_, ret)
    return ret

  def get_label_regex(self):
    """Return XYZ line regex capturing the atom label.
    """
    ret = re.sub('@Atom', rehelper.capture(rehelper.atomic_symbol), self.regex)
    ret = re.sub('@.Coord', rehelper.float_, ret)
    return ret

  def get_coordinates_regex(self):
    """Return XYZ line regex capturing all of the coordinates.
    """
    ret = re.sub('@Atom', rehelper.atomic_symbol, self.regex)
    ret = re.sub('@.Coord', rehelper.capture(rehelper.float_), ret)
    return ret

  def get_coordinates_inverse_regex(self):
    """Return XYZ line regex capturing everything but the coordinates.
    """
    ret = re.sub('@Atom', rehelper.atomic_symbol, self.regex)
    parts = re.sub('.Coord', '', ret).split('@')
    ret = (rehelper.float_).join(rehelper.capture(part) for part in parts)
    return ret

  def iter_labels(self, string):
    """Iterate over atom labels in a string

    Args:
      string: A string containing a block of more than two consecutive lines
        that match self.regex.

    Yields:
      str: The next atomic symbol.
    """
    for match in re.finditer(self.get_label_regex(), string):
      yield match.group(1)

  def iter_coordinates(self, string):
    """Iterate over coordinates in a string

    Args:
      string: A string containing a block of more than two consecutive lines
        that match self.regex.

    Yields:
      list: The next set of three Cartesian coordinate values.
    """
    for match in re.finditer(self.get_coordinates_regex(), string):
      yield [float(coord) for coord in match.groups()]

  def replace_coordinates_with_placeholder(self, string, placeholder):
    """Replace the coordinates in a string with a placeholder.

    Args:
      string: A string containing a block of more than two consecutive lines
        that match self.regex.
      placeholder: The string to replace the coordinates with.

    Returns:
      str: A copy of `string`, with coordinates replaced by `placeholder`.
    """
    regex = self.xyzline.get_coordinates_inverse_regex()
    ret = ''
    for line in string.splitlines():
      line += '\n'
      match = re.search(regex, line)
      if not match:
        ret += line
      else:
        ret += (placeholder).join(match.groups())
    return ret


class XYZString(object):
  """A container for a file containing cartesian coordinates.

  A helper for parsing a coordinate-containing string.  Assumes the coordinates
  are contained in the last block of more than two consecutive lines matching
  the given XYZFinder.

  Attributes:
    string: A string containing a block of more than two consecutive lines that
      match xyzfinder.regex.
    xyzfinder: An XYZFinder object.
    unitsfinder: A UnitsFinder object.
    regex: Regex for finding the Cartesian coordinates within the string.
  """

  def __init__(self, string, xyzfinder, unitsfinder=None):
    self.string = string.replace('{', '{{').replace('}', '}}')
    self.xyzfinder = xyzfinder
    self.unitsfinder = unitsfinder
    self.regex = rehelper.two_or_more(xyzfinder.get_regex())
    start, end = self.get_last_match().span()
    self.head = self.string[:start]
    self.body = self.string[start:end]
    self.foot = self.string[end:]

  def extract_units(self):
    """Extract the units from `string`, if present.

    Returns:
      str: A string indicating the units, 'bohr' or 'angstrom'.
    """
    if self.unitsfinder is None:
      raise Exception('This method requires the unitsfinder argument')
    return self.unitsfinder.get_units(self.string)

  def extract_labels(self):
    """Extract the labels from the coordinate block.

    Returns:
      tuple: A tuple of atomic labels.
    """
    return tuple(self.xyzfinder.iter_labels(self.body))

  def extract_coordinates(self):
    """Extract coordinates from the coordinate block.

    Returns:
      numpy.ndarray: A numpy array of coordinates.
    """
    return np.array(list(self.xyzfinder.iter_coordinates(self.body)))

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

  def get_last_match(self):
    match = None
    for match in re.finditer(self.regex, self.string, re.MULTILINE):
      pass
    if not match:
      raise Exception("No Cartesian coordinates found in this string.")
    return match



if __name__ == "__main__":
  from .molecule import Molecule
  from .options import Options
  # Build some helper objects.
  string = """
{ "bagel" : [                                                                    
                                                                                 
{                                                                                
    "title" : "molecule",                                                        
    "symmetry" : "C1",                                                           
    "basis" : "svp",                                                             
    "df_basis" : "svp-jkfit",                                                    
    "angstrom" : false,                                                          
    "geometry" : [                                                               
        {"atom" : "O",  "xyz" : [ 0.0000000000, 0.0000000000,-0.0000000000] },   
        {"atom" : "H",  "xyz" : [ 0.0000,-0.0000000000, 1.0000000000] },         
        {"atom" : "H",  "xyz" : [ 0.0000000000, 1.0000000000, 1.0000000000] }    
    ]                                                                            
},                                                                               
                                                                                 
{                                                                                
    "title" : "hf"                                                               
}                                                                                
                                                                                 
]}                                                                               

"""
  xyzregex = r' *{{"atom" *: *"@Atom", *"xyz" *: *\[ *@XCoord, *@YCoord, *@ZCoord *\] *}},? *\n'
  xyzfinder = XYZFinder(xyzregex)
  xyzstring = XYZString(string, xyzfinder)
  # Make a molecule object from the coordinates contained in the template file.
  labels = xyzstring.extract_labels()
  coordinates = xyzstring.extract_coordinates()
  mol = Molecule(labels, coordinates)
  print(labels)
  print(coordinates)
  template = xyzstring.replace_coordinates_with_placeholder('{:> 17.12f}')
  print(template)
  c = list(coordinates.flatten())
  print(template.format(*c))
