"""Regex helper module.

Defines some helpers for defining regular expressions.
"""
import re

# Module-level variables.
float_ = r'-?\d+\.\d+'
atomic_symbol = r'[a-zA-Z]{1,4}'
word = r'[a-zA-Z]{2,}'


# Module functions.
def capture(string):
    return r'({:s})'.format(string)


def two_or_more(string):
    return r'(?:{:s}){{2,}}'.format(string)


def get_last_match(pattern, string, flags=0):
    match = None
    for match in re.finditer(pattern, string, flags):
        pass
    if not match:
        raise ValueError("No match found in string.")
    return match


# Module classes.
class UnitsFinder(object):
    """Helper for processing line in a coordinate string indicating its units.
  
    Attributes:
      pattern: Regex for finding the line that indicates the units ('bohr' or
        'angstrom') of the molecular geometry.  Contains the placeholder
        '@Units' at the position of the units in the string, and ends in ' *\n'.
    """

    def __init__(self, pattern=' *units +@Units *\n'):
        self.pattern = pattern
        if '@Units' not in self.pattern:
            raise ValueError("This regex must contain the placeholder @Units.")

    def get_units_pattern(self):
        """Return capturing units line regex.
        """
        return re.sub('@Units', capture(word), self.pattern)


class CoordinateLineFinder(object):
    """Helper for processing coordinate-containing lines in a string.
  
    Attributes:
        pattern: Regex for finding a line containing Cartesian coordinates.
            Contains the placeholders '@Atom', '@XCoord', '@YCoord', and
            '@ZCoord' at the positions of the atomic symbol and its associated
            coordinate values in the string. Always must end in a newline.
    """

    def __init__(self, pattern=' *@Atom +@XCoord +@YCoord +@ZCoord *\n'):
        self.pattern = pattern
        placeholders = ('@Atom', '@XCoord', '@YCoord', '@ZCoord')
        if not all(placeholder in self.pattern for placeholder in placeholders):
            raise ValueError(
                "This regex must contain the following placeholders: "
                "@Atom, @XCoord, @YCoord, @ZCoord.")

    def get_pattern(self):
        """Return non-capturing coordinate line regex.
        """
        ret = re.sub('@Atom', atomic_symbol, self.pattern)
        ret = re.sub('@.Coord', float_, ret)
        return ret

    def get_label_pattern(self):
        """Return coordinate line regex capturing the atom label.
        """
        ret = re.sub('@Atom', capture(atomic_symbol), self.pattern)
        ret = re.sub('@.Coord', float_, ret)
        return ret

    def get_coordinates_pattern(self):
        """Return coordinate line regex capturing coordinates.
        """
        ret = re.sub('@Atom', atomic_symbol, self.pattern)
        ret = re.sub('@.Coord', capture(float_), ret)
        return ret

    def get_coordinates_inverse_pattern(self):
        """Return coordinate line regex capturing everything but the coordinates.
        """
        ret = re.sub('@Atom', atomic_symbol, self.pattern)
        parts = re.sub('.Coord', '', ret).split('@')
        ret = float_.join(capture(part) for part in parts)
        return ret


class CoordinateFinder(object):
    """Helper for grabbing the coordinates from a string.
  
    Attributes:
        line_finder: A CoordinateLineFinder object.
        header: Text immediately preceding the coordinates.
        footer: Text immediately following the coordinates.
    """

    def __init__(self, pattern=' *@Atom +@XCoord +@YCoord +@ZCoord *\n',
                 header='', footer=''):
        """Initialize the coordinates finder
    
        Args:
            pattern: Regex for finding a line containing Cartesian coordinates.
                Contains the placeholders '@Atom', '@XCoord', '@YCoord', and
                '@ZCoord' at the positions of the atomic symbol and its
                associated coordinate values in the string. Always must end in a
                newline.
            header: Text immediately preceding the coordinates.
            footer: Text immediately following the coordinates.
        """
        self.line_finder = CoordinateLineFinder(pattern)
        self.header = str(header)
        self.footer = str(footer)

    def get_pattern(self):
        """Return non-capturing gradient regex.
        """
        ret = self.header
        ret += two_or_more(self.line_finder.get_pattern())
        ret += self.footer
        return ret


class EnergyFinder(object):
    """Helper for processing the line in an output string containing the energy.
  
    Attributes:
        patterns: Regex patterns for finding energies in the output file.  Must
            contain the placeholder '@Energy'.
    """

    def __init__(self, patterns):
        self.patterns = [patterns] if isinstance(patterns, str) else patterns
        try:
            for pattern in self.patterns:
                assert '@Energy' in pattern
        except:
            raise ValueError("Requires a list of regular expression patterns "
                             "containing the placeholder '@Energy'.")

    def get_energy_patterns(self):
        """Return capturing energy regex patterns.
        """
        return [re.sub('@Energy', capture(float_), pattern) for pattern in
                self.patterns]


class GradientLineFinder(object):
    """Helper for grabbing the lines in a string containing the gradient.
  
    Attributes:
        pattern: Regex for finding a line containing elements of the gradient.
            Must contain the placeholders '@XGrad', '@YGrad', and '@ZGrad' and
            end in a newline.
    """

    def __init__(self, pattern):
        self.pattern = pattern
        placeholders = ('@XGrad', '@YGrad', '@ZGrad')
        if not all(placeholder in self.pattern for placeholder in placeholders):
            raise ValueError(
                "This regex must contain the following placeholders: "
                "@XGrad, @YGrad, @ZGrad.")

    def get_pattern(self):
        """Return non-capturing gradient line regex.
        """
        ret = re.sub('@.Grad', float_, self.pattern)
        return ret

    def get_gradient_pattern(self):
        """Return capturing gradient line regex.
        """
        ret = re.sub('@.Grad', capture(float_), self.pattern)
        return ret


class GradientFinder(object):
    """Helper for grabbing the gradient from a string.
  
    Attributes:
        line_finder: A GradientLineFinder object.
        header: Text immediately preceding the gradient lines.
        footer: Text immediately following the gradient lines.
    """

    def __init__(self, pattern, header='', footer=''):
        """Initialize the gradient finder.
    
        Args:
            pattern: Regex for finding a line containing elements of the
                gradient.  Must contain the placeholders '@XGrad', '@YGrad', and
                '@ZGrad' and end in a newline.
            header: Text immediately preceding the coordinates.
            footer: Text immediately following the coordinates.
        """
        self.line_finder = GradientLineFinder(pattern)
        self.header = str(header)
        self.footer = str(footer)
        if not isinstance(self.line_finder, GradientLineFinder):
            raise ValueError(
                "The 'line_finder' argument must be an instance of "
                "the GradientLineFinder class.")

    def get_pattern(self):
        """Return non-capturing gradient regex.
        """
        ret = self.header
        ret += two_or_more(self.line_finder.get_pattern())
        ret += self.footer
        return ret


if __name__ == "__main__":
    psi_output_string = """
  -Total Gradient:
     Atom            X                  Y                   Z
    ------   -----------------  -----------------  -----------------
       1        0.000000000000     0.000000000000     0.080750158386
       2       -0.000000000000     0.036903026214    -0.040375079193
       3        0.000000000000    -0.036903026214    -0.040375079193
  """
    header = r'-Total Gradient: *\n +Atom +X +Y +Z *\n.*\n'
    grad_finder = GradientFinder(r' +\d +@XGrad +@YGrad +@ZGrad *\n', header)
    pattern = grad_finder.line_finder.get_gradient_pattern()
    print(re.findall(pattern, psi_output_string, re.MULTILINE))
