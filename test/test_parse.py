from psider.parse import CoordinateString, EnergyString
import numpy as np


def test__coordinatestring_with_molecule_string():
  mol_string = """
    units angstrom
    O  0.0000000000  0.0000000000 -0.0647162893
    H  0.0000000000 -0.7490459967  0.5135472375
    H  0.0000000000  0.7490459967  0.5135472375
  """
  coordstring = CoordinateString(mol_string)
  assert(coordstring.extract_units() == 'angstrom')
  assert(coordstring.extract_labels() == ('O', 'H', 'H'))
  assert(np.allclose(coordstring.extract_coordinates(),
                    [[ 0.,  0.      , -0.06471629],
                     [ 0., -0.749046,  0.51354724],
                     [ 0.,  0.749046,  0.51354724]]))

def test__coordinatestring_with_psi_input_string():
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
  coordstring = CoordinateString(psi_input_string)
  assert(coordstring.extract_labels() == ('O', 'H', 'H'))
  assert(np.allclose(coordstring.extract_coordinates(),
                    [[ 0.,  0.      , -0.06471629],
                     [ 0., -0.749046,  0.51354724],
                     [ 0.,  0.749046,  0.51354724]]))

def test__coordinatestring_with_bagel_input_string():
  from psider.rehelper import CoordinatesLineFinder, CoordinatesFinder

  bagel_input_string = """
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
  lineregex = r' *{"atom" *: *"@Atom", *"xyz" *: *\[ *@XCoord, *@YCoord, *@ZCoord *\] *},? *\n'
  linefinder = CoordinatesLineFinder(lineregex)
  coordsfinder = CoordinatesFinder(linefinder)
  coordstring = CoordinateString(bagel_input_string, coordsfinder)
  assert(coordstring.extract_labels() == ('O', 'H', 'H'))
  assert(np.allclose(coordstring.extract_coordinates(),
                    [[ 0.,  0., -0.],
                     [ 0., -0.,  1.],
                     [ 0.,  1.,  1.]]))

def test__coordinatestring_replacement():
  from psider.rehelper import CoordinatesLineFinder, CoordinatesFinder

  bagel_input_string = """
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
  formattable_string = bagel_input_string.replace('{', '{{').replace('}', '}}')
  lineregex = r' *{{"atom" *: *"@Atom", *"xyz" *: *\[ *@XCoord, *@YCoord, *@ZCoord *\] *}},? *\n'
  linefinder = CoordinatesLineFinder(lineregex)
  coordsfinder = CoordinatesFinder(linefinder)
  coordstring = CoordinateString(formattable_string, coordsfinder)
  bagel_input_template = coordstring.replace_coordinates_with_placeholder('{:.12f}')
  assert(bagel_input_template != bagel_input_string)
  coordinates = coordstring.extract_coordinates()
  coords_list = list(coordinates.flatten())
  assert(bagel_input_template.format(*coords_list) == bagel_input_string)


def test__energystring_with_psi_output_string():
  from psider.rehelper import EnergyFinder
  psi_output_string = """
   => Energetics <=

    Nuclear Repulsion Energy =              9.3006650611521877
    One-Electron Energy =                -122.5548262505967756
    Two-Electron Energy =                  38.2930872603115446
    DFT Exchange-Correlation Energy =       0.0000000000000000
    Empirical Dispersion Energy =           0.0000000000000000
    PCM Polarization Energy =               0.0000000000000000
    EFP Energy =                            0.0000000000000000
    Total Energy =                          0.0000000000000000
    Total Energy =                        -74.9610739291330503

    Alert: EFP and PCM quantities not currently incorporated into SCF psivars.
  """
  energyfinder = EnergyFinder(r' *Total Energy *= *@Energy *\n')
  successregex = r'\*\*\* P[Ss][Ii]4 exiting successfully.'
  energystring = EnergyString(psi_output_string, energyfinder, successregex)
  assert(np.isclose(energystring.extract_energy(), -74.9610739291330503))
  assert(energystring.check_success() == False)
