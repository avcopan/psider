from psi4 import core
import numpy as np
import re
from . import regex
from . import atomdata
from . import physconst

class Molecule(object):                                                          
  """A class to store information about a chemical system.                       
                                                                                 
  Attributes:                                                                    
    labels (`tuple` of `str`s): Atomic symbols.                                  
    coordinates (`np.ndarray`): An `self.natoms` x 3 array of Cartesian          
      coordinates corresponding to the atoms in `self.labels`.                   
    units (str): Either 'angstrom' or 'bohr', indicating the units of            
      `self.coordinates`.                                                        
  """                                                                            

  @classmethod
  def from_psi4_molecule(cls, mol_psi4):
    mol_psi4.update_geometry()
    mol_string = mol_psi4.create_psi4_string_from_molecule()
    return cls.from_string(mol_string)

  @classmethod
  def from_string(cls, mol_string):
    units_regex = regex.line("units", regex.capture(regex.word))
    label_regex = regex.line(regex.capture(regex.atomic_symbol),
                             *(3 * [regex.float_]))
    xyz_regex = regex.spaced(regex.atomic_symbol,
                             *(3 * [regex.capture(regex.float_)]))
    units = re.search(units_regex, mol_string).group(1).lower()
    labels = [match.group(1).upper()
              for match in re.finditer(label_regex, mol_string)]
    coordinates = np.array([[float(coord) for coord in match.groups()]
                            for match in re.finditer(xyz_regex, mol_string)])
    return cls(labels, coordinates, units)


  def __init__(self, labels, coordinates, units = "angstrom"):
    """Initialize this Molecule object.                                          
    """                                                                          
    self.labels = tuple(labels)
    self.coordinates = np.array(coordinates)
    self.units = str(units.lower())
    self.masses = [atomdata.get_mass(label) for label in labels]
    self.natom = len(labels)
    assert self.units in ("angstrom", "bohr")

  def set_units(self, units):
    if units == "angstrom" and self.units == "bohr":
      self.units = "angstrom"
      self.coordinates *= physconst.bohr2angstrom
    elif units == "bohr" and self.units == "angstrom":
      self.units  = "bohr"
      self.coordinates /= physconst.bohr2angstrom

  def set_coordinates(self, coordinates, units = None):
    if units is None: units = self.units
    self.units = units
    self.coordinates = coordinates

  def make_psi4_molecule_object(self):
    core.efp_init()
    mol = core.Molecule.create_molecule_from_string(str(self))
    mol.update_geometry()
    return mol


if __name__ == "__main__":
  mol_string = """
units angstrom
  O  0.0000000000  0.0000000000 -0.0647162893
  H  0.0000000000 -0.7490459967  0.5135472375
  H  0.0000000000  0.7490459967  0.5135472375
"""
  mol = Molecule.from_string(mol_string)
  print(mol.units)
  print(mol.labels)
  print(mol.coordinates)
