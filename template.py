"""Module for the job template file.
"""

class TemplateFile(object):
  """A formattable template for a job input file.

  Attributes:
    template: A string with 3*n formatting placeholders, '{:.12f}', where n is
      an integer.  All other brackets are doubled ('{{' instead of '{') so that
      we can call 'template.format(*list)' to fill the placeholders with a list
      of 3*n floats.
  """

  def __init__(self, template):
    self.template = template

  def make_input(self, coordinates):
    """Generate an input file from the template.

    Args:
      coordinates: A numpy array.  The number of elements must correspond to the
        number of placeholders in `self.template`.
    """
    coordslist = list(coordinates.flatten())
    return self.template.format(*coordslist)


