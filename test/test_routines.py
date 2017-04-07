from psider.routines import EnergyRoutine
import numpy as np


def test__energy_routine(tmpdir):
    import subprocess as sp
    from psider.molecule import Molecule
    from psider.template import InputTemplate
    from psider.parse import CoordinateString, EnergyFinder

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
    input_coord_string = CoordinateString(psi_input_format_str)
    molecule = Molecule.from_coord_string(input_coord_string, 'angstrom')
    input_template = InputTemplate.from_coord_string(input_coord_string,
                                                     'angstrom')
    energy_finder = EnergyFinder([r"\n[ \t]+Reference Energy += +@Energy",
                                  r"\n[ \t]+Correlation Energy += +@Energy"])
    success_pattern = r"\*\*\* P[Ss][Ii]4 exiting successfully."
    energy_routine = EnergyRoutine(molecule, input_template, energy_finder,
                                   success_pattern,
                                   submit_function=lambda: sp.call(["psi4"]),
                                   input_name="input.dat",
                                   output_name="output.dat",
                                   job_dir_path=tmpdir.dirname,
                                   job_file_paths=None)
    energy_routine.execute()
    assert(np.isclose(energy_routine.energy, -74.9956618520565144))
