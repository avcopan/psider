"""Module for general user-specified options.
"""
import os
from psi4 import core
from .template import TemplateFile
from .molecule import Molecule
from . import parse

class Options(object):
  """Store job-control options and pass additional options on to Psi4.

  Attributes:
    molecule: A Molecule object containing the starting geometry.
    template_file: A TemplateFile for the job input.
    energy_finders: A list of EnergyFinder objects.
    success_regex: A regex that matches the output if the job ran successfully.
    input_name: The name of the job input file.
    output_name: The name of the job output file.
    job_dir: The name of the job directory.  For finite-difference
      computations, the jobs for each displaced geometry will be placed in
      sub-directories named according to `disp_dir`.
    job_file_paths: A list of files to be copied into the job directory.
  """

  def __init__(self,
               # Required keywords:
               reference_input_str,
               units            = "angstrom",
               coord_regex      = r" *@Atom +@XCoord +@YCoord +@ZCoord *\n",
               energy_regexes   = [],
               success_regex    = r"",
               input_name       = "input.dat",
               output_name      = "output.dat",
               job_dir          = os.getcwd(),
               job_file_names   = [],
               submitter        = None,
               # Optional keywords:
               disp_dir             = "@Disp",
               batch_submission     = False,
               gradient_finders     = [],
               gradient_output_name = None,
               **psi4kwargs):
    """Initialize the Options object.

    Args:
      reference_input_str: A complete job-input file string containing Cartesian
        coordinates that match `coord_regex` with units `units`.
      units: A string indicating the distance units used for coordinates in the
        job-input file.  Either "angstrom" or "bohr".
      coord_regex: Regex for finding a line containing Cartesian coordinates,
        to be used for parsing the template file.  Must contain the placeholders
        @Atom, @XCoord, @YCoord, and @ZCoord, indicating where the atomic symbol
        and its associated coordinate lie in the string, and must end in a
        newline.  If the line contains brackets, they must be doubled (i.e.
        replace '{' with '{{').
      energy_regexes: A list of regexes for finding energies in the output file.
        Each must contain the place holder @Energy at the position of the
        energy, which is assumed to have standard floating-point format.  If the
        list has multiple elements, these will be added together to obtain the
        final energy.
      success_regex: A regex that matches the output only if the job ran
        successfully.
      job_dir: The name of the job directory.  For finite-difference
        computations, the jobs for each displaced geometry will be placed in
        sub-directories named according to `disp_dir`.
      job_file_names: A list of file names to be copied over from the current
        directory into the job directory.
      input_name: The name of the job input file.
      output_name: The name of the job output file.
      submitter: A user-defined object which implements the method `submit`. 
        If `batch_submission` is set to False, then `submitter.submit()` will
        be executed in each individual job directory.  In a finite-difference
        routine, `batch_submission` may be set to True.  In this case,
        `submitter.submit()` will be executed only once, a level below the
        job directories for each displaced geometry.
      disp_dir: The naming scheme to be used for the job directories in a
        finite-difference routine.  Must contain the placeholder "@Disp",
        which will be replaced 
      batch_submission: A boolean.  False means that the submitter will be
        executed in each individual job directory.  For finite difference
        computations this may be set to True, in which case the submitter
        will be executed only once a directory back from the individual
        job directories.  This enables the use of array job submission on
        clusters running Sun Grid Engine, for example.
      correction_regexes: Regex for energy corrections.  Each one should have
        the form of an energy regex.
      gradient_finder: A parse.GradientFinder object for finding the Gradient
        in an analytic gradient computation.
      gradient_output_name: A string with the name of the file containing the
        gradient. If set to None and the gradient is needed, it will be assumed
        that the gradient is in main job output file (`output_name`).
      **psi4kwargs: A dictionary of Psi4 keyword arguments.  For submodule
        keywords, use the submodule name as key and pass a dictionary with the
        submodule keys/values as its value.
    """
    # Build a CoordinateString object for the job-input file.
    ref_input_str = (reference_input_str.replace('{', '{{')
                                        .replace('}', '}}'))
    coord_finder = parse.CoordinateFinder(coord_regex)
    ref_input = parse.CoordinateString(ref_input_str, coord_finder)
    # Build a Molecule object from the reference job-input file.
    self.molecule = Molecule.from_coord_string(ref_input, units)
    # Build a TemplateFile object from the reference job-input file.
    self.template_file = TemplateFile.from_coord_string(ref_input, units)
    # Other attributes
    self.energy_finders = [EnergyFinder(regex) for regex in energy_regexes]
    self.success_regex = success_regex
    self.input_name = input_name
    self.output_name = output_name
    self.job_dir = job_dir
    self.job_file_paths = [os.path.join(os.getcwd(), name)
                           for name in job_file_names]
    for file_path in self.job_file_paths:
      if not os.path.exists(file_path):
        raise ValueError("Could not find the job file {:s}".format(file_path))
    self.submitter = submitter
    if not hasattr(self.submitter, 'submit'):
      pass
      #raise ValueError("



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


if __name__ == "__main__":
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
  options = Options(
    reference_input_str = psi_input_str
  )
  print(repr(options.template_file))
