#!/usr/bin/env python
"""
Basic example of plotting parametric SBOL Visual glyphs using the parasbolv library.
"""

import parasbolv as psv
import matplotlib.pyplot as plt

__author__  = 'Thomas E. Gorochowski <tom@chofski.co.uk>'
__license__ = 'MIT'
__version__ = '1.0'

renderer = psv.GlyphRenderer(glyph_path='../glyphs_2.0/')

fig = plt.figure(figsize=(6,6))
ax = fig.add_axes([0.0, 0.0, 1.0, 1.0], frameon=False, aspect=1)
renderer.draw_glyph(ax, 'CDS', (50, 50))
ax.plot([0,250], [50,50])
ax.set_ylim([0,250])
ax.set_xlim([0,250])
plt.show()
