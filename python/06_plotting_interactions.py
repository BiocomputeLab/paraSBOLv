#!/usr/bin/env python
"""
Plot interactions to and from glyphs.
"""

import parasbolv as psv
import matplotlib.pyplot as plt

part_list = []
part_list.append( ['CDS',
                   None,
                   {'cds': {'facecolor': (0.5,0,0), 'edgecolor': (0.5,0,0), 'linewidth': 2}},
                   {'interaction_type':'process',
                    'interaction_key':'this is an arbitrary key',
                    'interaction_direction':'receive',
                    'interaction_parameters': {'color': (0,0,0),
                                               'heightskew': 8,
                                               'headheight': 3,
                                               'headwidth': 3,
                                               'z_priority': 0,
                                               'linewidth': 2,
                                               'xy_skew': (-2,0)}
                   }
                  ] )
part_list.append( ['Promoter',
                   None,
                   {'promoter-body': {'edgecolor': (0,0.5,0), 'linewidth': 2}, 'promoter-head': {'edgecolor': (0,0.5,0), 'linewidth': 2}},
                   {'interaction_type':'inhibition',
                    'interaction_key':'key1',
                    'interaction_direction':'receive',
                    'interaction_parameters': {'color': (0,0.5,0),
                                               'heightskew': -1,
                                               'headwidth': 14,
                                               'linewidth': 2,
                                               'z_priority': 5,
                                               'linewidth': 2}
                   }
                  ] )
part_list.append( ['CDS',
                   None,
                   {'cds': {'facecolor': (0,0.5,0), 'edgecolor': (0,0.5,0), 'linewidth': 2}},
                   {'interaction_type':'inhibition',
                    'interaction_key':'key1',
                    'interaction_direction':'send',
                    'interaction_parameters': {'xy_skew': (-2,0)}
                   }
                  ] )
part_list.append( ['Promoter',
                   None,
                   {'promoter-body': {'edgecolor': (0,0,0.5), 'linewidth': 2}, 'promoter-head': {'edgecolor': (0,0,0.5), 'linewidth': 2}},
                   {'interaction_type':'inhibition',
                    'interaction_key':'a_key',
                    'interaction_direction':'receive',
                    'interaction_parameters': {'color': (0,0,0.5),
                                               'heightskew': -1,
                                               'headwidth': 14,
                                               'linewidth': 2,
                                               'z_priority': 5,
                                               'linewidth': 2}
                   }
                  ] )
part_list.append( ['CDS',
                   None,
                   {'cds': {'facecolor': (0,0,0.5), 'edgecolor': (0,0,0.5), 'linewidth': 2}},
                   {'interaction_type':'inhibition',
                    'interaction_key':'a_key',
                    'interaction_direction':'send',
                    'interaction_parameters': {'color': (0,0.5,0),
                                               'z_priority': 5,
                                               'linewidth': 2,
                                               'xy_skew': (-2,0)}
                   }
                  ] )
part_list.append( ['CDS',
                   None,
                   {'cds': {'facecolor': (0,0,0.5), 'edgecolor': (0,0,0.5), 'linewidth': 2}},
                   {'interaction_type':'inhibition',
                    'interaction_key':'a_key',
                    'interaction_direction':'send',
                    'interaction_parameters': {'color': (0,0.5,0),
                                               'z_priority': 5,
                                               'linewidth': 2,
                                               'xy_skew': (-2,0)}
                   }
                  ] )
part_list.append( ['CDS',
                   None,
                   {'cds': {'facecolor': (0,0,0), 'edgecolor': (0,0,0), 'linewidth': 2}},
                   {'interaction_type':'process',
                    'interaction_key':'this is an arbitrary key',
                    'interaction_direction':'send',
                    'interaction_parameters': {'xy_skew': (-2,0)}
                   }
                  ] )



fig, ax, baseline_start, baseline_end = psv.render_part_list(part_list,glyph_path='../glyphs/', padding=0.2)
ax.plot([baseline_start[0], baseline_end[0]], [baseline_start[1], baseline_end[1]], color=(0,0,0), linewidth=1.5, zorder=0)

plt.show()
