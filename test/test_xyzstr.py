from psinglepoint.xyzstr import UnitsFinder, XYZFinder, XYZString
import numpy as np


def test__with_mol_string():
  mol_string = """
    units angstrom
    O  0.0000000000  0.0000000000 -0.0647162893
    H  0.0000000000 -0.7490459967  0.5135472375
    H  0.0000000000  0.7490459967  0.5135472375
  """
  unitsfinder = UnitsFinder()
  xyzfinder = XYZFinder()
  xyzstring = XYZString(mol_string, xyzfinder, unitsfinder)
  assert(xyzstring.extract_units() == 'angstrom')
  assert(xyzstring.extract_labels() == ('O', 'H', 'H'))
  assert(np.allclose(xyzstring.extract_coordinates(),
                    [[ 0.,  0.      , -0.06471629],
                     [ 0., -0.749046,  0.51354724],
                     [ 0.,  0.749046,  0.51354724]]))

def test__with_psi_input_string():
  psi_input_string = """
    memory 270 mb

    molecule {
      O  0.0000000000  0.0000000000 -0.0647162893
      H  0.0000000000 -0.7490459967  0.5135472375
      H  0.0000000000  0.7490459967  0.5135472375
    }

    set basis sto-3g
    energy('scf')
  """
  xyzfinder = XYZFinder()
  xyzstring = XYZString(psi_input_string, xyzfinder)
  assert(xyzstring.extract_labels() == ('O', 'H', 'H'))
  assert(np.allclose(xyzstring.extract_coordinates(),
                    [[ 0.,  0.      , -0.06471629],
                     [ 0., -0.749046,  0.51354724],
                     [ 0.,  0.749046,  0.51354724]]))

