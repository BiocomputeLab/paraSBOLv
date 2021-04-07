#!/usr/bin/env python
"""
Add customisable labels in or around glyphs.
"""

import parasbolv as psv
import matplotlib.pyplot as plt

renderer = psv.GlyphRenderer()

fig = plt.figure(figsize=(6,6))
ax = fig.add_axes([0.0, 0.0, 1.0, 1.0], frameon=False, aspect=1)

user_parameters = {}

# Draw labelled CDS
user_parameters['label'] = {'text':'label',
                            'rotation':(3.14 / 4)}
renderer.draw_glyph(ax, 'CDS', (15, 60), user_parameters=user_parameters, rotation=3.14 / 4)

# Draw fancily labelled CDS using Matplotlib font parameters
cds_style = {}
cds_style['cds'] = {'facecolor': (0,0,1), 'edgecolor': (0,0,0.5), 'linewidth': 5}

user_parameters['label'] = {'text':'gene',
                            'color':(1,0.5,0),
                            'userfont':{'family':'arial',
                                         'style':'italic',
                                         'variant':'normal',
                                         'stretch':'normal',
                                         'weight':'5',
                                         'size':'22'
                                        }
}
renderer.draw_glyph(ax, 'CDS', (55, 60), user_parameters=user_parameters, user_style=cds_style)

# Draw skewed labels
dnalocation_style = {}
dnalocation_style['location-top-path'] = {'facecolor': (1,0,0), 'edgecolor': (0,0,0), 'linewidth': 3}
user_parameters['label'] = {'text':'label',
                            'color':(1,0,0),
                            'rotation':(-3.14 / 4),
                            'xy_skew':(-7,10)
}
renderer.draw_glyph(ax, 'DNA Location', (15, 15), user_parameters=user_parameters, user_style=dnalocation_style)

signature_style = {}
signature_style['signature-box-path'] = {'facecolor': (1,1,0), 'edgecolor': (0,0,0), 'linewidth': 3}
user_parameters['label'] = {'text':'label',
                            'color':(0.5,0.5,0),
                            'xy_skew':(2,10)
}
renderer.draw_glyph(ax, 'Signature', (40, 15), user_parameters=user_parameters, user_style=signature_style)

dnalocation_style['location-top-path'] = {'facecolor': (0,1,0), 'edgecolor': (0,0,0), 'linewidth': 3}
user_parameters['label'] = {'text':'label',
                            'color':(0,0.75,0),
                            'rotation':(-3.14 / 4),
                            'xy_skew':(8,-3)
}
renderer.draw_glyph(ax, 'DNA Location', (75, 15), user_parameters=user_parameters, user_style=dnalocation_style)

ax.set_ylim([0,100])
ax.set_xlim([0,100])
plt.show()

