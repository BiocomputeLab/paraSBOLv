#!/usr/bin/env python
"""
Basic example of plotting parametrix SBOL Visual glyphs
using matplotlib.
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

# Renderer to create the 
renderer = psv.GlyphRenderer(glyph_path='../glyphs/')


def data_gen():
    for cnt in range(1000):
        t = cnt / 10
        yield t, np.sin(2*np.pi*t) * np.exp(-t/10.)


def init():
    ax.set_ylim(-1.1, 1.1)
    ax.set_xlim(0, 10)
    del xdata[:]
    del ydata[:]
    line.set_data(xdata, ydata)
    return line,

fig, ax = plt.subplots()
line, = ax.plot([], [], lw=2)
ax.grid()
xdata, ydata = [], []


def run(data):
    # update the data
    t, y = data
    xdata.append(t)
    ydata.append(y)
    xmin, xmax = ax.get_xlim()

    if t >= xmax:
        ax.set_xlim(xmin, 2*xmax)
        ax.figure.canvas.draw()
    line.set_data(xdata, ydata)

    return line,

ani = animation.FuncAnimation(fig, run, data_gen, blit=False, interval=10,
                              repeat=False, init_func=init)
plt.show()