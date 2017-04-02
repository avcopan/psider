"""Regex helper module.

Defines some convenient functions and constants for regular expressions.
"""

def capture(string):
  return r'({:s})'.format(string)

def maybe(string):
  return r'(?:{:s})?'.format(string)

def zero_or_more(string):
  return r'(?:{:s})*'.format(string)

def one_or_more(string):
  return r'(?:{:s})+'.format(string)

def two_or_more(string):
  return r'(?:{:s}){{2,}}'.format(string)

def spaced(*strings):
  return '\s+'.join(strings)

def line(*strings):
  return '\s*' + spaced(*strings) + '\s*\n'

character        = r'[a-zA-Z]'
digits           = r'\d+'
float_           = r'-?\d+\.\d+'
spaces           = r'\s+'
endline          = r'\n'
atomic_symbol    = character + maybe(character) + maybe(character)
word             = two_or_more(character)
