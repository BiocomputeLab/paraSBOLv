from distutils.core import setup

setup(name='parasbolv',

      version='0.2.0',

      description='A lightweight Python library designed to simplify the rendering of ' +
                  'highly-customisable SBOL Visual glyphs and diagrams',

      author='Thomas E. Gorochowski, Charlie Clark, James Scott-Brown',

      author_email='tom@chofski.co.uk, charlieclark1.e.e.2019@bristol.ac.uk, james@jamesscottbrown.com',

      url='https://github.com/BiocomputeLab/paraSBOLv/blob/master/parasbolv/parasbolv.py',

      packages=['parasbolv'],

      requires=[
          'numpy',
          'matplotlib'
      ]
      )
