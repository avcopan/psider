"""Module for the job input template file.
"""


class InputTemplate(object):
    """A formattable template for a job input file.
  
    Attributes:
        string: A string with 3*n formatting placeholders, '{:.12f}', where n is
            an integer.  All other brackets are doubled ('{{' instead of '{') so
            that we can call 'string.format(*list)' to fill the placeholders
            with a list of 3*n floats.
    """

    @classmethod
    def from_coord_string(cls, coord_string, units):
        string = coord_string.replace_coordinates_with_placeholder('{:.12f}')
        return cls(string, units)

    def __init__(self, string, units):
        self.string = string
        self.units = units

    def __str__(self):
        return self.string.__str__()

    def __repr__(self):
        return self.string.__repr__()

    def fill(self, molecule):
        """Generate an input file from the template string.
    
        Args:
            molecule: A Molecule object, defining the coordinates to be filled
                into the job input file.
        """
        molecule = molecule.copy()
        molecule.set_units(self.units)
        coord_list = list(molecule.coordinates.flatten())
        return self.string.format(*coord_list)
