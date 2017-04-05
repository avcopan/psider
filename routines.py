import os

class Energy(object):

  @classmethod
  def from_options_object(cls, options):
    #self.submit = lambda: submitter(**submitter_kwargs)
    raise NotImplemented("Not yet implemented")

  def __init__(self,
               molecule,
               template_file,
               units,
               energy_finders,
               success_regex,
               job_dir = os.getcwd(),
               job_files = [],
               input_name = "input.dat",
               output_name = "output.dat",
               submit = lambda: None,
               ):
    self.molecule = molecule
    self.template_file = template_file
    self.energy_finders = energy_finders
    self.success_regex = success_regex
    self.job_dir = job_dir
    self.input_name = input_name
    self.output_name = output_name
    self.files_to_copy = files_to_copy



if __name__ = "__main__":
  
  energy = Energy(
