import os
import sys
sys.path.insert(0, os.path.abspath('..'))

project = 'E-Commerce Manager'
copyright = '2025, Marat Khasanov'
author = 'Marat Khasanov'
release = '0.99'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
]

templates_path = ['_templates']
exclude_patterns = []

language = 'ru'


html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
