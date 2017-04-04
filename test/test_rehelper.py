from psider.rehelper import EnergyFinder, GradientLineFinder
import re


def test__energy_finder():
  psi_output_string = """
   => Energetics <=

    Nuclear Repulsion Energy =              9.3006650611521877
    One-Electron Energy =                -122.5548262505967756
    Two-Electron Energy =                  38.2930872603115446
    DFT Exchange-Correlation Energy =       0.0000000000000000
    Empirical Dispersion Energy =           0.0000000000000000
    PCM Polarization Energy =               0.0000000000000000
    EFP Energy =                            0.0000000000000000
    Total Energy =                        -74.9610739291330503
  """
  energyfinder = EnergyFinder(r' *Total Energy *= *@Energy *\n')
  regex = energyfinder.get_energy_regex()
  match = re.search(regex, psi_output_string)
  assert(match.group(1) == '-74.9610739291330503')


def test__gradient_finder():
  psi_output_string = """
  -Total Gradient:
     Atom            X                  Y                   Z
    ------   -----------------  -----------------  -----------------
       1        0.000000000000     0.000000000000     0.080750158386
       2       -0.000000000000     0.036903026214    -0.040375079193
       3        0.000000000000    -0.036903026214    -0.040375079193
  """
  gradlinefinder = GradientLineFinder(r' +\d +@XGrad +@YGrad +@ZGrad *\n')
  regex = gradlinefinder.get_gradient_regex()
  assert(re.findall(regex, psi_output_string) ==
    [('0.000000000000',  '0.000000000000',  '0.080750158386'),
     ('-0.000000000000', '0.036903026214', '-0.040375079193'),
     ('0.000000000000', '-0.036903026214', '-0.040375079193')])
