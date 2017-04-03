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

  def get_coords_regex(self):
    """Return XYZ line regex capturing all of the coordinates.
    """
    ret = re.sub('@Atom', rehelper.atomic_symbol, self.regex)
    ret = re.sub('@.Coord', rehelper.capture(rehelper.float_), ret)
    return ret

  def iter_label_matches(self, string):
    for match in re.finditer(self.get_label_regex(), string):
      yield match

  def iter_coords_matches(self, string):
    for match in re.finditer(self.get_coords_regex(), string):
      yield match

  def iter_labels(self, string):
    for match in self.iter_label_matches(string):
      yield match.group(1)

  def iter_coords(self, string):
    for match in self.iter_coords_matches(string):
      yield [float(coord) for coord in match.groups()]


class XYZString(object):
  """A container for a file containing cartesian coordinates.

  A helper for parsing a coordinate-containing string.

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
    self.foot = self.string[:end]

  def extract_units(self):
    if self.unitsfinder is None:
      raise Exception('This method requires the unitsfinder argument')
    return self.unitsfinder.get_units(self.string)

  def extract_labels(self):
    return tuple(self.xyzfinder.iter_labels(self.body))

  def extract_coordinates(self):
    return np.array(list(self.xyzfinder.iter_coords(self.body)))

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
  xyzregex = r' *{{"atom" *: *"@Atom", *"xyz" *: *\[ *@XCoord, *@YCoord, *@ZCoord *] *}},? *\n'
  xyzfinder = XYZFinder(xyzregex)
  xyzstring = XYZString(string, xyzfinder)
  # Make a molecule object from the coordinates contained in the template file.
  labels = xyzstring.extract_labels()
  coords = xyzstring.extract_coordinates()
  mol = Molecule(labels, coords)
  print(labels)
  print(coords)

  '''
  molstring = str(mol)
  xyzfinder = XYZFinder()
  unitsfinder = UnitsFinder()
  xyzstring = XYZString(molstring, xyzfinder, unitsfinder)
  print(xyzstring.extract_units())
  print(xyzstring.extract_labels())
  print(xyzstring.extract_coordinates())
  '''
