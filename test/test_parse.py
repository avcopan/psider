from psider.parse import (
  CoordinateFinder, EnergyFinder, GradientFinder,
  CoordinateString, EnergyString, GradientString
)
import numpy as np
import re


def test__energy_finder():
  psi_output_string = """
   => Energetics <=

    Nuclear Repulsion Energy =              9.3006650611521877
    One-Electron Energy =                -122.5548262505967756
    Two-Electron Energy =                  38.2930872603115446
    DFT Exchange-Correlation Energy =       0.0000000000000000
    Empirical Dispersion Energy =           0.0000000000000000
    PCM Polarization Energy =               0.0000000000000000
    EFP Energy =                            0.0000000000000000
    Total Energy =                        -74.9610739291330503
  """
  energyfinder = EnergyFinder(r' *Total Energy *= *@Energy *\n')
  regex = energyfinder.get_energy_regex()
  match = re.search(regex, psi_output_string)
  assert(match.group(1) == '-74.9610739291330503')


def test__gradient_finder():
  psi_output_string = """
  -Total Gradient:
     Atom            X                  Y                   Z
    ------   -----------------  -----------------  -----------------
       1        0.000000000000     0.000000000000     0.080750158386
       2       -0.000000000000     0.036903026214    -0.040375079193
       3        0.000000000000    -0.036903026214    -0.040375079193
  """
  gradfinder = GradientFinder(r' +\d +@XGrad +@YGrad +@ZGrad *\n')
  regex = gradfinder.linefinder.get_gradient_regex()
  assert(re.findall(regex, psi_output_string) ==
    [('0.000000000000',  '0.000000000000',  '0.080750158386'),
     ('-0.000000000000', '0.036903026214', '-0.040375079193'),
     ('0.000000000000', '-0.036903026214', '-0.040375079193')])



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
  regex = r' *{"atom" *: *"@Atom", *"xyz" *: *\[ *@XCoord, *@YCoord, *@ZCoord *\] *},? *\n'
  coordsfinder = CoordinateFinder(regex)
  coordstring = CoordinateString(bagel_input_string, coordsfinder)
  assert(coordstring.extract_labels() == ('O', 'H', 'H'))
  assert(np.allclose(coordstring.extract_coordinates(),
                    [[ 0.,  0., -0.],
                     [ 0., -0.,  1.],
                     [ 0.,  1.,  1.]]))

def test__coordinatestring_replacement():
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
  regex = r' *{{"atom" *: *"@Atom", *"xyz" *: *\[ *@XCoord, *@YCoord, *@ZCoord *\] *}},? *\n'
  coordsfinder = CoordinateFinder(regex)
  coordstring = CoordinateString(formattable_string, coordsfinder)
  bagel_input_template = coordstring.replace_coordinates_with_placeholder('{:.12f}')
  assert(bagel_input_template != bagel_input_string)
  coordinates = coordstring.extract_coordinates()
  coords_list = list(coordinates.flatten())
  assert(bagel_input_template.format(*coords_list) == bagel_input_string)


def test__energystring_with_psi_output_string():
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


def test__gradientstring_with_psi_output_string():
  psi_output_string = """
  -Total Gradient:
     Atom            X                  Y                   Z
    ------   -----------------  -----------------  -----------------
       1        0.000000000000     0.000000000000     0.000000000000
       2        0.000000000000     0.000000000000     0.000000000000
       3        0.000000000000     0.000000000000     0.000000000000
  -Total Gradient:
     Atom            X                  Y                   Z
    ------   -----------------  -----------------  -----------------
       1        0.000000000000     0.000000000000     0.080750158386
       2       -0.000000000000     0.036903026214    -0.040375079193
       3        0.000000000000    -0.036903026214    -0.040375079193
  -Totally Not The Gradient:
     Atom            X                  Y                   Z
    ------   -----------------  -----------------  -----------------
       1        0.000000000000     0.000000000000     0.000000000000
       2        0.000000000000     0.000000000000     0.000000000000
       3        0.000000000000     0.000000000000     0.000000000000
  """
  regex = r' +\d +@XGrad +@YGrad +@ZGrad *\n'
  head = r'-Total Gradient: *\n +Atom +X +Y +Z *\n.*\n'
  foot = ''
  gradfinder = GradientFinder(regex, head, foot)
  gradstring = GradientString(psi_output_string, gradfinder)
  assert(np.allclose(gradstring.extract_gradient(),
                    [[ 0.,  0.        ,  0.08075016],
                     [-0.,  0.03690303, -0.04037508],
                     [ 0., -0.03690303, -0.04037508]]))

