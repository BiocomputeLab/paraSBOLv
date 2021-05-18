#!/usr/bin/env python
"""
Animated CDS with random shape and style
"""

import numpy as np
import parasbolv as psv
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Setup the animation
np.random.seed(1)
renderer = psv.GlyphRenderer()
user_parameters = {}
cds_style = {}
fig, ax = plt.subplots()

def run(data):
	# Clear the axis and then draw
    ax.clear()
    ax.set_aspect('equal')
    ax.set_xticks([])
    ax.set_yticks([])
    ax.axis('off')
    ax.set_ylim([25,75])
    ax.set_xlim([0,70])
    user_parameters['height'] = np.random.uniform(10, 20)
    user_parameters['width'] = np.random.uniform(10, 20)
    user_parameters['arrowbody_height'] = np.random.uniform(4, 10)
    user_parameters['arrowhead_width'] = np.random.uniform(5, 9)
    cds_style['cds'] = {'facecolor': (np.random.uniform(0, 1),
    	                              np.random.uniform(0, 1),
    	                              np.random.uniform(0, 1)), 
                        'edgecolor': (np.random.uniform(0, 1),
                        	          np.random.uniform(0, 1),
                        	          np.random.uniform(0, 1)), 
                        'linewidth': np.random.uniform(1, 10)}
    renderer.draw_glyph(ax, 'CDS', (20, 50), user_parameters=user_parameters, user_style=cds_style)

ani = animation.FuncAnimation(fig, run, None, blit=False, interval=10,
                              repeat=False, init_func=None)


ani.save('02_animated_CDS.gif', fps=30)

# Let the rave begin!
plt.show()