from psider.parse import CoordinateString
import numpy as np


def test__with_mol_string():
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
  coordstring = CoordinateString(psi_input_string)
  assert(coordstring.extract_labels() == ('O', 'H', 'H'))
  assert(np.allclose(coordstring.extract_coordinates(),
                    [[ 0.,  0.      , -0.06471629],
                     [ 0., -0.749046,  0.51354724],
                     [ 0.,  0.749046,  0.51354724]]))

def test__with_bagel_input_string():
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

def test__coordinate_replacement():
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
  
