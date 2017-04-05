"""Module for general user-specified options.
"""
from psi4 import core

class Options(object):
  """Store job-control options and pass additional options on to Psi4.
  """

  def __init__(self,
               # Required keywords:
               template_file_path = "template.dat",
               coord_units = "angstrom",
               coord_regex = r" *@Atom +@XCoord +@YCoord +@ZCoord *\n",
               energy_regex = r"",
               success_regex = r"",
               input_name = "input.dat",
               output_name = "output.dat",
               submitter = lambda kwargs: None,
               submitter_kwargs = {},
               # Optional keywords:
               disp_dir = "@Disp",
               batch_submission = False,
               correction_regexes = None,
               files_to_copy = None,
               gradient_finder = None,
               gradient_output_name = None,
               **psi4kwargs):
    """Initialize the Options object.

    Args:
      template_file_path: Path to the template job-input file.  This should be a
        complete job input file containing Cartesian coordinates that match
        `coord_regex` with units `coord_units`.
      coord_units: A string indicating the distance units used for coordinates
        in the job-input file.  Either "angstrom" or "bohr".
      coord_regex: Regex for finding a line containing Cartesian coordinates,
        to be used for parsing the template file.  Must contain the placeholders
        @Atom, @XCoord, @YCoord, and @ZCoord, indicating where the atomic symbol
        and its associated coordinate lie in the string, and must end in a
        newline.  If the line contains brackets, they must be doubled (i.e.
        replace '{' with '{{').
        Alternatively, this can be a parse.CoordinateFinder object which
        augments the above regex with a header and a footer for more
        fine-grained control.
      energy_regex: Regex for finding the energy in the output file.  Must
        contain the placeholder @Energy in place of the energy, which is assumed
        to be in standard floating-point format, and end in a newline.
      success_regex: A regex that will match the output only if the job ran
        successfully.
      input_name: The name of the job input file.
      output_name: The name of the job output file.
      submitter: A user-defined job submission function.  This function must
        accept the keyword arguments in `submitter_kwargs` and must be synced
        (i.e. it must not quit until the jobs have finished running).  Unless
        `batch_submission` is set to True, this will be executed in each
        individual job directory.

        Example:

          >>> import subprocess as sp
          >>> def submit(**kwargs):
          >>>   program = kwargs['program']
          >>>   sp.call([program, "-i", "input.dat", "-o", "output.dat"])
          >>> 
          >>> options = Options(...,
          >>>                   input_name = "input.dat",
          >>>                   output_name = "output.dat",
          >>>                   submitter = submit,
          >>>                   submitter_kwargs = {'program': "psi4"},
          >>>                   disp_dir = "@Disp",
          >>>                   batch_submission = False)

        If this options object is passed to a finite difference job with five
        displacements, it will execute 'psi4 -i input.dat -o output.dat' in
        once in each of the job directories 0/, 1/, 2/, 3/, and 4/.
      submitter_kwargs: User-defined keyword arguments for the user-defined
        submission function.
      disp_dir: The naming scheme to be used for the job directories in a
        finite-difference computation.  Must contain the placeholder "@Disp",
        which will be replaced 
      batch_submission: A boolean.  False means that the submitter will be
        executed in each individual job directory.  For finite difference
        computations this may be set to True, in which case the submitter
        will be executed only once a directory back from the individual
        job directories.  This enables the use of array job submission on
        clusters running Sun Grid Engine, for example.
      correction_regexes: Regex for energy corrections.  Each one should have
        the form of an energy regex.
      files_to_copy: A list of files to be copied over into each job directory.
      gradient_finder: A parse.GradientFinder object for finding the Gradient
        in an analytic gradient computation.
      gradient_output_name: A string with the name of the file containing the
        gradient. If set to None and the gradient is needed, it will be assumed
        that the gradient is in main job output file (`output_name`).
      **psi4kwargs: A dictionary of Psi4 keyword arguments.  For submodule
        keywords, use the submodule name as key and pass a dictionary with the
        submodule keys/values as its value.
    """
    # Required keywords:
    self.template_file_path   = template_file_path
    self.coord_units          = coord_units
    self.coord_regex          = coord_regex
    self.energy_regex         = energy_regex
    self.success_regex        = success_regex
    self.input_name           = input_name
    self.output_name          = output_name
    self.submitter            = submitter
    self.submitter_kwargs     = submitter_kwargs
    # Optional keywords:
    self.disp_dir             = disp_dir
    self.batch_submission     = batch_submission
    self.correction_regexes   = correction_regexes
    self.files_to_copy        = files_to_copy
    self.gradient_finder      = gradient_finder
    self.gradient_output_name = gradient_output_name
    self.psi4kwargs           = psi4kwargs


def set_psi4_options(**kwargs):
  """Sets Psi4 run-time options.

  Args:
    **kwargs: A dictionary of Psi4 keyword arguments.  For submodule keywords,
      use the submodule name as key (e.g. 'findif') and pass a dictionary with
      the submodule keys/values as its value (e.g. {'points': 5}).
  """
  for key, value in kwargs.items():
    key = key.upper()
    core.print_options()
    if key in core.get_global_option_list():
      core.set_global_option(key, value)
      core.print_out("{:s} set to {:s}\n".format(key, str(value).upper()))
    elif type(value) is dict:
      try:
        for subkey, subvalue in value.items():
          subkey = subkey.upper()
          core.set_local_option(key, subkey, subvalue)
          core.print_out("{:s} {:s} set to {:s}\n"
                         .format(key, subkey, str(subvalue).upper()))
      except:
        raise Exception("Attempt to set local psi4 option {:s} with {:s} "
                        "failed.".format(key, str(value)))
    else:
      raise ValueError("Unrecognized keyword {:s}".format(str(key)))


