from psi4 import core

class Options(object):

  def __init__(self,
               template_file_path="template.dat",
               xyz_regex=" *@Atom +@XCoord +@YCoord +@ZCoord *\n",
               energy_regex="",
               success_regex="",
               correction_regexes=None,
               program="",
               input_name="input.dat",
               files_to_copy=None,
               output_name="output.dat",
               input_units="angstrom",
               submitter=lambda options:None,
               maxiter=20,
               job_array=False,
               queue="",
               **psi4kwargs):
    """Stores job-control options and passes additional options on to Psi4.

    Attributes:
      template_file_path: Path to the template input file
      xyz_regex: Regex for finding a line containing Cartesian coordinates.
        Must contain @Atom, @XCoord, @YCoord, and @ZCoord, indicating where the
        atomic symbol and its associated coordinate values are in the string,
        and must end with a newline character, '\n'.  If the line contains
        brackets, they must be doubled (i.e. replace '{' with '{{').
      energy_regex: Regex for finding the energy in the output file.  Must
        contain the placeholder @Energy and end in a newline character.
        For example, " *Total *Energy *= *@Energy *\n", would work for a simple
        Psi4 Hartree-Fock output.
      success_regex: Regex that shows the program ran sucessfully
      correction_regexes: Regex for energy corrections.  Each one should have
        the form of an energy regex.
      program: Name of program to be run (specifically the name used by the
        submision program)
      input_name: Name of input file
      files_to_copy: List of files to be copied over to running directory
      output_name: Name for output file
      input_units: Units of the template file geometry
      submitter: Submission function (either to queue or locally)
      maxiter: Maximum number of iterations for OPTKING geometry optimization
      job_array: Submit as a job array; True or False
      queue: Name Of queue that jobs should be submitted to
      psi4kwargs: Keyword arguments to pass to PSI4
    """

    self.template_file_path = template_file_path
    self.xyz_regex          = xyz_regex
    self.energy_regex       = energy_regex  
    self.success_regex      = success_regex 
    self.correction_regexes = correction_regexes if correction_regexes is not None else []
    self.program            = program       
    self.input_name         = input_name    
    self.files_to_copy      = files_to_copy if files_to_copy is not None else []
    self.output_name        = output_name   
    self.input_units        = input_units
    self.submitter          = submitter
    self.maxiter            = maxiter
    self.job_array          = job_array
    self.queue              = queue         
    self.job_array_range    = None # needs to be set by calling function
    for key, value in psi4kwargs.items():
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
            core.print_out("{:s} {:s} set to {:s}\n".format(key, subkey, str(subvalue).upper()))
        except:
          raise Exception("Attempt to set local psi4 option {:s} with {:s} failed.".format(key, str(value)))
      else:
        raise ValueError("Unrecognized keyword {:s}".format(str(key)))
