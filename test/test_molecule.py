from psider.molecule import Molecule
import numpy as np

def test__from_string():
  mol_string = """
    units angstrom
    O  0.0000000000  0.0000000000 -0.0647162893
    H  0.0000000000 -0.7490459967  0.5135472375
    H  0.0000000000  0.7490459967  0.5135472375
  """
  mol = Molecule.from_string(mol_string)
  assert(mol.units == 'angstrom')
  assert(mol.labels == ('O', 'H', 'H'))
  assert(np.allclose(mol.coordinates,
                    [[ 0.,  0.      , -0.06471629],
                     [ 0., -0.749046,  0.51354724],
                     [ 0.,  0.749046,  0.51354724]]))

