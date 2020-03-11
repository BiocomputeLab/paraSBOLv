#!/usr/bin/env python
"""
Animated CDS with random shape and style
"""

import numpy as np
import parasbolv as psv
import matplotlib.pyplot as plt
import matplotlib.animation as animation

__author__  = 'Thomas E. Gorochowski <tom@chofski.co.uk>'
__license__ = 'MIT'
__version__ = '1.0'

# Fixing random state for reproducibility
np.random.seed(1)
renderer = psv.GlyphRenderer(glyph_path='../glyphs/')

def data_gen():
    for cnt in range(1000):
        t = cnt / 10
        yield t, np.sin(2*np.pi*t) * np.exp(-t/10.)

def init():
    ax.set_ylim([25,75])
    ax.set_xlim([0,70])
    return None

user_parameters = {}
cds_style = {}
fig, ax = plt.subplots()

def run(data):
    # update the data
    t, y = data
    ax.clear()
    ax.set_ylim([25,75])
    ax.set_xlim([0,70])
    user_parameters['arrowbody_width'] = np.random.uniform(15, 30)
    user_parameters['arrowbody_height'] = np.random.uniform(4, 10)
    user_parameters['arrowhead_height'] = np.random.uniform(0, 10)
    user_parameters['arrowhead_width'] = np.random.uniform(5, 9)
    cds_style['cds'] = {'facecolor': (np.random.uniform(0, 1),np.random.uniform(0, 1),np.random.uniform(0, 1)), 
                        'edgecolor': (np.random.uniform(0, 1),np.random.uniform(0, 1),np.random.uniform(0, 1)), 
                        'linewidth': np.random.uniform(1, 10)}
    renderer.draw_glyph(ax, 'CDS', (20, 50), user_parameters=user_parameters, user_style=cds_style)
    return None

ani = animation.FuncAnimation(fig, run, data_gen, blit=False, interval=10,
                              repeat=False, init_func=init)
# Let the rave begin!
plt.show()