from psider.options import Options


def test__options_with_psi_input_str():
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
  options = Options(reference_input_str = psi_input_str)
  assert(str(options.molecule) == """units angstrom
O     0.0000000000    0.0000000000   -0.0647162893
H     0.0000000000   -0.7490459967    0.5135472375
H     0.0000000000    0.7490459967    0.5135472375
"""
  )
  assert(str(options.template_file) == """
    memory 270 mb

    molecule {{
      O  {:12.f}  {:12.f} {:12.f}
      H  {:12.f} {:12.f}  {:12.f}
      H  {:12.f}  {:12.f}  {:12.f}
    }}

    set basis sto-3g
    energy('scf')
  """
  )
