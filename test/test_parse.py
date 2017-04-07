import re
import numpy as np
from psider.parse import (
    CoordinateFinder, EnergyFinder, GradientFinder,
    CoordinateString, EnergyString, GradientString
)


def test__energy_finder():
    psi_output_str = """
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
    energy_finder = EnergyFinder(r' *Total Energy *= *@Energy *\n')
    pattern, = energy_finder.get_energy_patterns()
    match = re.search(pattern, psi_output_str)
    assert (match.group(1) == '-74.9610739291330503')


def test__gradient_finder():
    psi_output_str = """
  -Total Gradient:
     Atom            X                  Y                   Z
    ------   -----------------  -----------------  -----------------
       1        0.000000000000     0.000000000000     0.080750158386
       2       -0.000000000000     0.036903026214    -0.040375079193
       3        0.000000000000    -0.036903026214    -0.040375079193
    """
    grad_finder = GradientFinder(r' +\d +@XGrad +@YGrad +@ZGrad *\n')
    pattern = grad_finder.line_finder.get_gradient_pattern()
    assert (re.findall(pattern, psi_output_str) ==
            [('0.000000000000', '0.000000000000', '0.080750158386'),
             ('-0.000000000000', '0.036903026214', '-0.040375079193'),
             ('0.000000000000', '-0.036903026214', '-0.040375079193')])


def test__coordinate_string_with_molecule_str():
    mol_str = """
    units angstrom
    O  0.0000000000  0.0000000000 -0.0647162893
    H  0.0000000000 -0.7490459967  0.5135472375
    H  0.0000000000  0.7490459967  0.5135472375
    """
    coord_string = CoordinateString(mol_str)
    assert (coord_string.extract_units() == 'angstrom')
    assert (coord_string.extract_labels() == ('O', 'H', 'H'))
    assert (np.allclose(coord_string.extract_coordinates(),
                        [[0., 0., -0.06471629],
                         [0., -0.749046, 0.51354724],
                         [0., 0.749046, 0.51354724]]))


def test__coordinate_string_with_psi_input_str():
    psi_input_str = """
    memory 270 mb

    molecule {
      O  0.0000000000  0.0000000000 -0.0647162893
      H  0.0000000000 -0.7490459967  0.5135472375
      H  0.0000000000  0.7490459967  0.5135472375
    }

    set basis sto-3g
    energy('scf')
    """
    coord_string = CoordinateString(psi_input_str)
    assert (coord_string.extract_labels() == ('O', 'H', 'H'))
    assert (np.allclose(coord_string.extract_coordinates(),
                        [[0., 0., -0.06471629],
                         [0., -0.749046, 0.51354724],
                         [0., 0.749046, 0.51354724]]))


def test__coordinate_string_with_bagel_input_str():
    bagel_input_str = """
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
    pattern = (r' *{"atom" *: *"@Atom", *"xyz" *: *\[ *@XCoord, *@YCoord, '
               r'*@ZCoord *\] *},? *\n')
    coord_finder = CoordinateFinder(pattern)
    coord_string = CoordinateString(bagel_input_str, coord_finder)
    assert (coord_string.extract_labels() == ('O', 'H', 'H'))
    assert (np.allclose(coord_string.extract_coordinates(),
                        [[0., 0., -0.],
                         [0., -0., 1.],
                         [0., 1., 1.]]))


def test__coordinate_string_replacement():
    bagel_input_str = """
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
    formattable_string = bagel_input_str.replace('{', '{{').replace('}', '}}')
    pattern = (r' *{{"atom" *: *"@Atom", *"xyz" *: *\[ *@XCoord, *@YCoord, '
               r'*@ZCoord *\] *}},? *\n')
    coord_finder = CoordinateFinder(pattern)
    coord_string = CoordinateString(formattable_string, coord_finder)
    bagel_input_template = coord_string.replace_coordinates_with_placeholder(
        '{:.12f}')
    assert (bagel_input_template != bagel_input_str)
    coordinates = coord_string.extract_coordinates()
    coords_list = list(coordinates.flatten())
    assert (bagel_input_template.format(*coords_list) == bagel_input_str)


def test__energy_string_with_psi_output_str():
    psi_output_str = """
  -----------------------------------------------------------                    
   ==================> DF-MP2 Energies <====================                     
  -----------------------------------------------------------                    
   Reference Energy          =     -74.9610739291330503 [Eh]                     
   Singles Energy            =      -0.0000000000000000 [Eh]                     
   Same-Spin Energy          =      -0.0019556413348118 [Eh]                     
   Opposite-Spin Energy      =      -0.0326322815886586 [Eh]                     
   Correlation Energy        =      -0.0345879229234704 [Eh]                     
   Total Energy              =     -74.9956618520565144 [Eh]                     
  -----------------------------------------------------------                    
    """
    energy_finder = EnergyFinder([
        r"Reference Energy += +@Energy",
        r"Correlation Energy += +@Energy"
    ])
    success_pattern = r'\*\*\* P[Ss][Ii]4 exiting successfully.'
    energy_string = EnergyString(psi_output_str, energy_finder, success_pattern)
    assert (np.isclose(energy_string.extract_energy(), -74.9956618520565144))
    assert (energy_string.was_successful() is False)


def test__gradient_string_with_psi_output_str():
    psi_output_str = """
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
    pattern = r' +\d +@XGrad +@YGrad +@ZGrad *\n'
    header = r'-Total Gradient: *\n +Atom +X +Y +Z *\n.*\n'
    footer = ''
    grad_finder = GradientFinder(pattern, header, footer)
    grad_string = GradientString(psi_output_str, grad_finder)
    assert (np.allclose(grad_string.extract_gradient(),
                        [[0., 0., 0.08075016],
                         [-0., 0.03690303, -0.04037508],
                         [0., -0.03690303, -0.04037508]]))
