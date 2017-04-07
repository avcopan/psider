import os
import shutil
from . import parse


class Submitter(object):
    """A class for executing the submission script.    
    """

    def __init__(self, submit_function, submit_dir_path):
        self.submit_function = submit_function
        self.submit_dir_abs_path = os.path.abspath(submit_dir_path)
        if not callable(self.submit_function):
            raise ValueError("This class requires a callable submit function.")

    def submit(self):
        """Executes the submit function in the requested directory.
        
        Returns:
            The output of the submit function.
        """
        original_working_directory = os.getcwd()
        os.chdir(self.submit_dir_abs_path)
        submit_function_output = self.submit_function()
        os.chdir(original_working_directory)
        return submit_function_output


class Job(object):
    """Framework for an individual computation.
    
    Attributes:
        input_str: A string holding the contents of the job-input file.
        input_path: The absolute path of the job-input file.
        output_path: The absolute path of the job-output file.
    """

    def __init__(self, molecule, input_template, input_name, output_name,
                 job_dir_path, job_file_paths):
        """Initialize Job object.
       
        In addition to setting the object's attributes, this creates the job
        directory and copies the auxiliary job files into it.
        
        Args:
            molecule: A Molecule object to be placed in the input file.
            input_template: An InputTemplate object defining the input file.
            input_name: The name of the input file.
            output_name: The name of the output file.
            job_dir_path: The path to the job directory.
            job_file_paths: Paths to additional job files, which will be copied
                into the job directory.
        """
        self.input_str = input_template.fill(molecule)
        # Create the job directory, unless it already exists
        job_dir_abs_path = os.path.abspath(job_dir_path)
        if not os.path.exists(job_dir_abs_path):
            os.makedirs(job_dir_abs_path)
        self.input_path = os.path.join(job_dir_abs_path, input_name)
        self.output_path = os.path.join(job_dir_abs_path, output_name)
        # Copy the job files into the job directory
        if job_file_paths is not None:
            for file_path in job_file_paths:
                file_abs_path = os.path.abspath(file_path)
                shutil.copy(file_abs_path, job_dir_abs_path)

    def write_input(self):
        """Write the job input file.
        """
        input_file = open(self.input_path, 'w')
        input_file.write(self.input_str)
        input_file.close()

    def read_output(self):
        """Read the job output file
        
        Returns:
            str: The contents of the output file.
        """
        return open(self.output_path).read()


class EnergyRoutine(object):
    """Computes energies.
    """

    def __init__(self, molecule, input_template, energy_finder,
                 success_pattern, submit_function, input_name="input.dat",
                 output_name="output.dat", job_dir_path=os.getcwd(),
                 job_file_paths=None):
        self.job = Job(molecule, input_template, input_name, output_name,
                       job_dir_path, job_file_paths)
        self.submitter = Submitter(submit_function, job_dir_path)
        self.energy_finder = energy_finder
        self.success_pattern = success_pattern
        if not isinstance(energy_finder, parse.EnergyFinder):
            raise ValueError("'energy_finder' must be an instance of the "
                             "parse.EnergyFinder class.")

    def sow(self):
        self.job.write_input()

    def run(self):
        self.submitter.submit()

    def reap(self):
        output_str = self.job.read_output()
        energy_string = parse.EnergyString(output_str, self.energy_finder,
                                           self.success_pattern)
        if not energy_string.was_successful():
            raise RuntimeError("Success pattern not found in output.")
        energy = energy_string.extract_energy()
        return energy


if __name__ == "__main__":
    import subprocess as sp
    import tempfile
    from .molecule import Molecule
    from .template import InputTemplate
    psi_input_str = """
memory 270 mb

molecule {
  O  0.0000000000  0.0000000000 -0.0647162893
  H  0.0000000000 -0.7490459967  0.5135472375
  H  0.0000000000  0.7490459967  0.5135472375
}

set basis sto-3g
energy('mp2')
    """
    psi_input_format_str = psi_input_str.replace('{', '{{').replace('}', '}}')
    coord_string = parse.CoordinateString(psi_input_format_str)
    molecule = Molecule.from_coord_string(coord_string, 'angstrom')
    input_template = InputTemplate.from_coord_string(coord_string, 'angstrom')
    energy_finder = parse.EnergyFinder([
        r"Reference Energy += +@Energy",
        r"Correlation Energy += +@Energy"
    ])
    success_pattern = r'\*\*\* P[Ss][Ii]4 exiting successfully.'
    def submit():
        sp.call(["psi4"])
    energy_routine = EnergyRoutine(
        molecule = molecule,
        input_template = input_template,
        energy_finder = energy_finder,
        success_pattern = success_pattern,
        submit_function = submit,
        job_dir_path = tempfile.gettempdir()
    )
    energy_routine.sow()
    energy_routine.run()
    energy = energy_routine.reap()
    print(energy)
