import re
import inspect


# Module functions.
def capture(pattern, name=None):
    """Convert a pattern to a capturing pattern, possibly with a name.
    
    Args:
        pattern: A string containing a regex pattern.
        name: An optional name for the captured group.

    Returns:
        str: The capturing pattern.

    Raises:
        ValueError if `name` is not None or a string.
    """
    if name is None:
        return r'({:s})'.format(pattern)
    elif isinstance(name, str):
        return r'(?P<{:s}>{:s})'.format(name, pattern)
    else:
        raise ValueError("Group name must be a string.")


def search(pattern, string, flags=0, find_last=False):
    """Scan through string looking for a match to the pattern.
    
    Generalizes re.search to allow us to search for the last match, rather than
    the first.
    
    Args:
        pattern: A regex pattern.
        string: The string to be searched.
        flags: Optional flags to be are passed on to re.search/re.finditer.
        find_last: A bool indicating whether to find the first or last match.

    Returns:
        re.MatchObject: The match. Defaults to None if nothing is found.
    """
    match = None
    if find_last is False:
        return re.search(pattern, string, flags=flags)
    elif find_last is True:
        for match in re.finditer(pattern, string, flags=flags):
            pass
        return match
    else:
        raise ValueError("Non-boolean value used for argument 'find_last'.")


# Module classes.
class PlaceholderPattern(object):
    """Generates regex patterns from strings with placeholders.

    Attributes:
        pattern: A regex pattern containing one or more placeholder strings, 
            such as '@ThingOne', '@ThingTwo', etc.  Each placeholder string must
            start with '@' and be used only once.
        placeholders: A dictionary of placeholders strings, such as
            {'ThingOne': '@ThingOne', 'ThingTwo': '@ThingTwo'}.
        subpatterns: A dictionary mapping keys to patterns, such as
            {'ThingOne': '[A-Za-z]+', 'ThingTwo': '\d\d'}.
        types: A dictionary mapping keys to data types, such as
            {'ThingOne': str, 'ThingTwo': int}.
    """

    def __init__(self, pattern, subpatterns, types=None):
        """Initializes a placeholder pattern object.
        
        Args:
            pattern: A regex pattern containing one or more placeholder strings, 
                such as '@ThingOne', '@ThingTwo', etc.  Each placeholder string
                must start with '@' and be used only once.
            subpatterns: A dictionary mapping keys to patterns, such as
                {'ThingOne': '[A-Za-z]+', 'ThingTwo': '\d\d'}.
            types: A dictionary mapping keys to data types, such as
                {'ThingOne': str, 'ThingTwo': int}.  Unspecified types will be
                set to str.
        """
        self.pattern = pattern
        self.subpatterns = subpatterns
        self.placeholders = {key: '@{:s}'.format(key) for key in
                             self.subpatterns.keys()}
        self.types = {} if types is None else types
        for key in self.subpatterns:
            placeholder = self.placeholders[key]
            if placeholder not in self.pattern:
                raise ValueError("Placeholder '@{:s}' not found.".format(key))
            elif self.pattern.count(placeholder) is not 1:
                raise ValueError("Repeated placeholder '@{:s}'.".format(key))
        for key, cls in self.types.items():
            if key not in self.subpatterns:
                raise ValueError("Invalid key '{:s}'.".format(key))
            elif not inspect.isclass(cls):
                raise ValueError("{:s} is not a type.".format(str(cls)))
        # Set remaining types to str.
        self.types.update({key: str for key in self.subpatterns
                           if key not in self.types})

    def get_pattern(self, *keys):
        """Get pattern capturing certain subpatterns.
        
        Args:
            *keys: A series of keys for `self.subpatterns` indicating that 
                these subpatterns should be captured in the final regex.
        
        Raises:
            ValueError if one of the keys is not in `self.subpatterns`.
        """
        # Make sure all keys are valid
        if not all(key in self.placeholders for key in keys):
            raise ValueError("Invalid key in {:s}.".format(str(keys)))
        # Build pattern.
        ret = self.pattern
        for key, placeholder in self.placeholders.items():
            if key in keys:
                subpattern = capture(self.subpatterns[key], name = key)
            else:
                subpattern = self.subpatterns[key]
            ret = re.sub(placeholder, subpattern, ret)
        return ret

    def get_inverse_pattern(self, *keys):
        """Get pattern capturing everything except for certain subpatterns.
        
        Args:
            *keys: A series of keys for `self.subpatterns`
                indicating that these subpatterns should not be captured in the
                final regex.

        Raises:
            ValueError if one of the subpatterns is not in `self.subpatterns`.
        """
        # Make sure all keys are valid
        if not all(key in self.placeholders for key in keys):
            raise ValueError("Invalid key in {:s}.".format(str(keys)))
        # Build pattern.
        ret = self.pattern
        for key, placeholder in self.placeholders.items():
            if key in keys:
                subpattern = '){:s}('.format(self.subpatterns[key])
            else:
                subpattern = self.subpatterns[key]
            ret = re.sub(placeholder, subpattern, ret)
        return capture(ret)

    def finditer(self, key, string, flags=0):
        """Iterate over matches to `self.pattern` in a string.
        
        Behaves like re.finditer, except that subpattern groups are converted to
        the pre-set data types stored in `self.types`.
        
        Args:
            key: A key for `self.subpatterns` indicating which value to extract.
                May also be a tuple of keys.
            string: The string to be searched.
            flags: Optional flags which are passed on to re.finditer.

        Yields:
            If `key` is a string, this yields a match group for 
            `self.subpatterns[key]`, converted to type `self.types[key]`.
            Alternatively, if `key`, is an iterable of subpattern keys, this
            yields a tuple of type-converted match groups.
        """
        if isinstance(key, str):
            key = (key,)
            def process_yield_value(value):
                return value[0]
        elif hasatter(key, "__iter__"):
            key = tuple(key)
            def process_yield_value(value):
                return tuple(value)
        else:
            raise ValueError("{:s} is not a string or an iterable."
                             .format(str(key)))
        pattern = self.get_pattern(*key)
        for match in re.finditer(pattern, string, flags=flags):



    def extract(self, keys, string, flags=0, find_last=False):
        """Extracts subpatterns and converts them to their data types.
        
        Finds the first or last pattern match and returns the captured 
        subpatterns, converted to the types set in `self.types`.
        
        Args:
            keys: One or more key(s) for `self.subpatterns` indicating which
                values to extract.
            string: The string to be searched.
            flags: Optional flags which are passed on to re.finditer.
            find_last: Find the last match, instead of the first?

        Returns:
            Extracted values.  If `keys` is a single string, the corresponding
            value will be returned.  If `keys` is an iterable with one or more
            items, the extracted values are returned as a tuple.  The order of
            the tuple will correspond to the order of the keys.
        """
        if isinstance(keys, str):
            keys = (keys,)
            process_return_value = lambda lst: lst[0]
        elif hasattr(keys, "__iter__"):
            keys = tuple(keys)
            process_return_value = tuple
        else:
            raise ValueError("{:s} is not a string or an iterable"
                             .format(str(keys)))
        pattern = self.get_pattern(*keys)
        match = search(pattern, string, flags=flags, find_last=find_last)
        if not match:
            raise ValueError("No match for pattern {:s}".format(repr(pattern)))
        ret = []
        for key in keys:
            cls = self.types[key]
            group = match.group(key)
            ret.append(cls(group))
        return process_return_value(ret)





if __name__ == "__main__":
    ppat = PlaceholderPattern(r' *@Atom +@XCoord +@YCoord +@ZCoord *\n',
                              subpatterns={'Atom': r'[a-zA-Z]{1,4}',
                                           'XCoord': '-?\d+\.\d+',
                                           'YCoord': '-?\d+\.\d+',
                                           'ZCoord': '-?\d+\.\d+'},
                              types={'XCoord': float,
                                     'YCoord': float,
                                     'ZCoord': float})
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
    print(ppat.extract('ZCoord', psi_input_str))
    print(ppat.extract(('XCoord', 'YCoord', 'ZCoord'), psi_input_str))
