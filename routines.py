import os

class Energy(object):

  @classmethod
  def from_options_object(cls, options):
    #self.submit = lambda: submitter(**submitter_kwargs)
    raise NotImplemented("Not yet implemented")

  def __init__(self,
               molecule,
               template,
               energy_finder,
               job_dir = os.getcwd(),
               input_name = "input.dat",
               output_name = "output.dat",
               submit = lambda: None,
               ):
    self.molecule = molecule
    self.template = template
    self.energy_finder = energy_finder
    self.job_dir = job_dir
    self.input_name = input_name
    self.output_name = output_name
    self.correction_regexes = correction_regexes
    self.files_to_copy = files_to_copy
