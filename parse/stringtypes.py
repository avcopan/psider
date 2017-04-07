"""Module for extracting information from a string.
"""
import re
import numpy as np
from . import rehelper


class CoordinateString(object):
    """A container for a string containing Cartesian coordinates.
  
    A helper for parsing a coordinate-containing string.  Assumes the
    coordinates are contained in the last block of more than two consecutive
    lines matching the given rehelper.CoordinateFinder.
  
    Attributes:
        string: A string that matches coords_finder.get_pattern().
        coords_finder: An rehelper.CoordinateFinder object.
        units_finder: A rehelper.UnitsFinder object.
        _body: The lines in `string` containing the Cartesian coordinates.
        _header: The lines above the body.
        _footer: The lines below the body.
    """

    def __init__(self, string, coords_finder=rehelper.CoordinateFinder(),
                 units_finder=rehelper.UnitsFinder()):
        self.string = string
        self.coord_finder = coords_finder
        if not isinstance(self.coord_finder, rehelper.CoordinateFinder):
            raise ValueError("The 'coords_finder' argument must be an instance"
                             "of the class rehelper.CoordinateFinder.")
        self.units_finder = units_finder
        # Split string into a header, a footer, and a geometry-containing body.
        pattern = self.coord_finder.get_pattern()
        match = rehelper.get_last_match(pattern, self.string, re.MULTILINE)
        start, end = match.span()
        self._header = self.string[:start]
        self._body = self.string[start:end]
        self._footer = self.string[end:]

    def extract_units(self):
        """Extract the units from `string`, if present.
    
        Returns:
            str: A string indicating the units, 'bohr' or 'angstrom'.
        """
        if not isinstance(self.units_finder, rehelper.UnitsFinder):
            raise ValueError("This method requires the 'units_finder' attribute"
                             "to be an rehelper.UnitsFinder instance.")
        pattern = self.units_finder.get_units_pattern()
        match = rehelper.get_last_match(pattern, self.string)
        if not match:
            raise ValueError("Couldn't find a match for the units regex.")
        return match.group(1).lower()

    def extract_labels(self):
        """Extract the labels from the body.
    
        Returns:
            tuple: A tuple of atomic labels.
        """
        pattern = self.coord_finder.line_finder.get_label_pattern()
        return tuple(re.findall(pattern, self._body))

    def extract_coordinates(self):
        """Extract coordinates from the body.
    
        Returns:
            numpy.ndarray: A numpy array of coordinates.
        """
        pattern = self.coord_finder.line_finder.get_coordinates_pattern()
        coordinates = np.array(re.findall(pattern, self._body))
        return coordinates.astype(np.float)

    def replace_coordinates_with_placeholder(self, placeholder):
        """Replace coordinates in the body with a placeholder.
    
        Args:
            placeholder: The string to put in place of the coordinates
    
        Returns:
            str: A copy of `self.string`, with coordinates replaced by
                `placeholder`.
        """
        body = ''
        line_finder = self.coord_finder.line_finder
        line_pattern = line_finder.get_coordinates_inverse_pattern()
        for line in self._body.splitlines():
            line += '\n'
            match = re.search(line_pattern, line)
            if not match:
                body += line
            else:
                body += placeholder.join(match.groups())
        return ''.join([self._header, body, self._footer])


class EnergyString(object):
    """A container for a string containing the energy.
  
    Attributes:
        string: A string containing energies.
        energy_finder: A list of rehelper.EnergyFinder objects.
        success_pattern: A regex that matches `string` if the job ran
            successfully.
    """

    def __init__(self, string, energy_finder, success_pattern=None):
        self.string = string
        self.success_pattern = success_pattern
        self.energy_finder = energy_finder
        if not isinstance(self.energy_finder, rehelper.EnergyFinder):
            raise ValueError("The 'energy_finder' argument must be an instance"
                             "of the class rehelper.EnergyFinder.")

    def extract_energy(self):
        """Extract the energy from `string`.
    
        Returns:
            float: The sum of the energies found in the string.
        """
        patterns = self.energy_finder.get_energy_patterns()
        energies = []
        for pattern in patterns:
            match = rehelper.get_last_match(pattern, self.string)
            if not match:
                raise ValueError("Couldn't find a match for the following "
                                 "energy pattern: {:s}".format(repr(pattern)))
            energies.append(float(match.group(1)))
        return sum(energies)

    def was_successful(self):
        """Determine success value.
    
        Returns:
            bool: Whether or not `self.success_pattern` has a match.
        """
        if not isinstance(self.success_pattern, str):
            raise ValueError("This method requires the 'success_pattern'"
                             "attribute to be set to a string value.")
        match = re.search(self.success_pattern, self.string)
        return bool(match)


class GradientString(object):
    """A container for a string containing the gradient.
  
    Attributes:
        string: A string that matches grad_finder.get_pattern().
        grad_finder: An rehelper.GradientFinder object.
        _body: The lines in `string` containing the Gradient.
        _header: The lines above the body.
        _footer: The lines below the body.
    """

    def __init__(self, string, grad_finder):
        self.string = string
        self.grad_finder = grad_finder
        if not isinstance(self.grad_finder, rehelper.GradientFinder):
            raise ValueError("The 'grad_finder' argument must be an instance of"
                             "the class rehelper.GradientFinder.")
        # Split string into a header, a footer, and a gradient-containing body.
        pattern = self.grad_finder.get_pattern()
        match = rehelper.get_last_match(pattern, self.string, re.MULTILINE)
        start, end = match.span()
        self._header = self.string[:start]
        self._body = self.string[start:end]
        self._footer = self.string[end:]

    def extract_gradient(self):
        """Extract the gradient from the body.
        """
        pattern = self.grad_finder.line_finder.get_gradient_pattern()
        gradient = np.array(re.findall(pattern, self._body))
        return gradient.astype(np.float)


if __name__ == "__main__":
    string = open('output.dat').read()
    energy_finder = rehelper.EnergyFinder(r' *Total Energy *= *@Energy *\n')
    success_pattern = r'\*\*\* P[Ss][Ii]4 exiting successfully.'
    energy_string = EnergyString(string, energy_finder, success_pattern)
    print(energy_string.extract_energy())
    print(energy_string.was_successful())
    pattern = r' +\d +@XGrad +@YGrad +@ZGrad *\n'
    header = r'-Total Gradient: *\n +Atom +X +Y +Z *\n.*\n'
    footer = ''
    grad_finder = rehelper.GradientFinder(pattern, header, footer)
    grad_string = GradientString(string, grad_finder)
    print(grad_string.extract_gradient())
