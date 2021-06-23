#!/usr/bin/env python
"""
Generative art project using SBOLv glyphs as building blocks.
"""

import parasbolv as psv
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import math

##############################################################################

def calc_frac_val_between (val1, val2, frac):
    # Handle tuples for colours and normal floating point values
    if type(val1) == tuple:
        param_diff1 = float(val2[0]) - val1[0]
        param_diff2 = float(val2[1]) - val1[1]
        param_diff3 = float(val2[2]) - val1[2]
        return (val1[0] + (float(param_diff1)*frac), 
                val1[1] + (float(param_diff2)*frac), 
                val1[2] + (float(param_diff3)*frac))
    elif type(val1) == float:
        param_diff = val2 - val1
        return val1 + (float(param_diff)*frac)
    elif type(val1) == int:
        param_diff = val2 - val1
        return val1 + (float(param_diff)*frac)
    return None


def draw_glyph(ax, renderer, glyph_type, glyph_position, glyph_size, glyph_angle, frac_out, waypoints, frame_frac):
    # Calculate the current parameters for the point in spiral
    glyph_params = {}
    glyph_params['Terminator'] = {'user_parameters': {}, 'user_style': {}}
    glyph_params['CDS'] = {'user_parameters': {}, 'user_style': {}}
    glyph_params['Promoter'] = {'user_parameters': {}, 'user_style': {}}
    
    for k_type in waypoints.keys():
        for k_param_type in waypoints[k_type].keys():
            for k_param in waypoints[k_type][k_param_type][0].keys():
                if k_param_type == 'user_parameters':
                    val1 = calc_frac_val_between(waypoints[k_type][k_param_type][0][k_param][0], waypoints[k_type][k_param_type][0][k_param][1], frac_out)
                    val2 = calc_frac_val_between(waypoints[k_type][k_param_type][1][k_param][0], waypoints[k_type][k_param_type][1][k_param][1], frac_out)
                    glyph_params[k_type][k_param_type][k_param] = calc_frac_val_between(val1, val2, frame_frac)
                else:
                    glyph_params[k_type][k_param_type][k_param] = {}
                    for k_el in waypoints[k_type][k_param_type][0][k_param].keys():
                        val1 = calc_frac_val_between(waypoints[k_type][k_param_type][0][k_param][k_el][0], waypoints[k_type][k_param_type][0][k_param][k_el][1], frac_out)
                        val2 = calc_frac_val_between(waypoints[k_type][k_param_type][1][k_param][k_el][0], waypoints[k_type][k_param_type][1][k_param][k_el][1], frac_out)
                        glyph_params[k_type][k_param_type][k_param][k_el] = calc_frac_val_between(val1, val2, frame_frac)

    if glyph_type == 'Terminator':
        bounds, end_point = renderer.draw_glyph(ax, glyph_type, glyph_position, rotation=glyph_angle, user_parameters=glyph_params['Terminator']['user_parameters'], user_style=glyph_params['Terminator']['user_style'])
    elif glyph_type == 'CDS':
        bounds, end_point = renderer.draw_glyph(ax, glyph_type, glyph_position, rotation=glyph_angle, user_parameters=glyph_params['CDS']['user_parameters'], user_style=glyph_params['CDS']['user_style'])
    elif glyph_type == 'Promoter':
        bounds, end_point = renderer.draw_glyph(ax, glyph_type, glyph_position, rotation=glyph_angle, user_parameters=glyph_params['Promoter']['user_parameters'], user_style=glyph_params['Promoter']['user_style'])


def generate_spiral(part_type, waypoints, frame_frac, angle_shift=91.0, size_shift=0.2, glyph_angle_shift=1.0):
    cur_position = (0.0, 0.0)
    cur_angle = 0.0
    cur_size = 1.0
    cur_glyph_angle = 0.0
    steps = 1000
    for idx in range(steps):
        draw_glyph(ax, renderer, part_type, cur_position, 20, cur_glyph_angle, idx/(float(steps)), waypoints, frame_frac)
        cur_position = (cur_size*math.sin(math.radians(cur_angle)), cur_size*math.cos(math.radians(cur_angle)))
        cur_angle += angle_shift
        cur_size += size_shift
        cur_glyph_angle += math.radians(glyph_angle_shift)


def generate_frame(spiral_params, waypoints, frame_frac):
    generate_spiral('Terminator', waypoints, frame_frac, angle_shift=spiral_params['Terminator']['angle_shift'], size_shift=spiral_params['Terminator']['size_shift'], glyph_angle_shift=spiral_params['Terminator']['glyph_angle_shift'])
    generate_spiral('CDS', waypoints, frame_frac, angle_shift=spiral_params['CDS']['angle_shift'], size_shift=spiral_params['CDS']['size_shift'], glyph_angle_shift=spiral_params['CDS']['glyph_angle_shift'])
    generate_spiral('Promoter', waypoints, frame_frac, angle_shift=spiral_params['Promoter']['angle_shift'], size_shift=spiral_params['Promoter']['size_shift'], glyph_angle_shift=spiral_params['Promoter']['glyph_angle_shift'])

##############################################################################

# Generate matplotlib Figure and Axes
fig = plt.figure(figsize=(3,3))
ax = fig.add_axes([0.0, 0.0, 1.0, 1.0], frameon=False, aspect=1)

# Generate renderer object
renderer = psv.GlyphRenderer()

##############################################################################

# Parameter ranges for glyphs
terminator_waypoint_0 = {'width': [10, 15], 'height': [15, 18]}
terminator_waypoint_1 = {'width': [10, 15], 'height': [15, 18]}
cds_waypoint_0 = {'width': [3, 15], 'height': [4, 7], 'arrowbody_height': [4, 7], 'arrowhead_width': [2, 10]}
cds_waypoint_1 = {'width': [34, 20], 'height': [3, 10], 'arrowbody_height': [3, 10], 'arrowhead_width': [5, 8]}
promoter_waypoint_0 = {'width': [3, 6], 'height': [5, 8], 'arrowbody_height': [3, 5], 'arrowhead_width': [1.5, 3]}
promoter_waypoint_1 = {'width': [20, 25], 'height': [30, 37], 'arrowbody_height': [24, 35], 'arrowhead_width': [10, 20]}
params_waypoints = {'Terminator': [terminator_waypoint_0, terminator_waypoint_1],
                    'CDS': [cds_waypoint_0, cds_waypoint_1],
                    'Promoter': [promoter_waypoint_0, promoter_waypoint_1]}

# Parameter ranges for glyphs
terminator_waypoint_0 = {'terminator-head': {'edgecolor': [(0.0,1,0.8),(1,0.5,0)], 'linewidth': [1, 0.4]},
                         'terminator-body': {'edgecolor': [(0.0,1,0.8),(1,0.5,0)], 'linewidth': [0.5, 0.4]}}
terminator_waypoint_1 = {'terminator-head': {'edgecolor': [(0.0,1,0.8),(1,0.5,0)], 'linewidth': [1, 0.4]},
                         'terminator-body': {'edgecolor': [(0.0,1,0.8),(1,0.5,0)], 'linewidth': [1, 0.4]}}
cds_waypoint_0 = {'cds': {'facecolor': [(0,0.5,1.0), (0,1.0,1)], 'edgecolor': [(0.0,0.1,0.5),(0.5,0.1,0)], 'linewidth': [0.2, 0.1]}}
cds_waypoint_1 = {'cds': {'facecolor': [(0.84,0.15,0.1), (0.9,0.1,0.0)], 'edgecolor': [(0.1,0.1,0.1),(0.2,0.3,0.1)], 'linewidth': [0.1, 0.7]}}
promoter_waypoint_0 = {'promoter-body': {'edgecolor': [(0.0,0.2,0.8),(1,0.5,0)], 'linewidth': [0.2, 0.4]},
                       'promoter-head': {'edgecolor': [(0.0,0.2,0.8),(1,0.5,0)], 'linewidth': [0.2, 0.4]}}
promoter_waypoint_1 = {'promoter-body': {'edgecolor': [(0.0,1,0.3),(0.1,0.5,0.0)], 'linewidth': [0.8, 1.2]},
                       'promoter-head': {'edgecolor': [(0.0,1,0.3),(0.1,0.5,0.0)], 'linewidth': [0.8, 1.2]}}
style_waypoints = {'Terminator': [terminator_waypoint_0, terminator_waypoint_1],
                   'CDS': [cds_waypoint_0, cds_waypoint_1],
                   'Promoter': [promoter_waypoint_0, promoter_waypoint_1]}

waypoints = {'Terminator': {'user_parameters': {}, 'user_style': {}},
             'CDS': {'user_parameters': {}, 'user_style': {}},
             'Promoter': {'user_parameters': {}, 'user_style': {}}}
waypoints['Terminator']['user_parameters'] = params_waypoints['Terminator']
waypoints['Terminator']['user_style'] = style_waypoints['Terminator']
waypoints['CDS']['user_parameters'] = params_waypoints['CDS']
waypoints['CDS']['user_style'] = style_waypoints['CDS']
waypoints['Promoter']['user_parameters'] = params_waypoints['Promoter']
waypoints['Promoter']['user_style'] = style_waypoints['Promoter']

##############################################################################

spiral_params_waypoints = {}
spiral_params_waypoints['Terminator'] = {'angle_shift': [95.0, 91.0], 'size_shift': [0.25, 0.2], 'glyph_angle_shift': [0.1, 4.0]}
spiral_params_waypoints['CDS'] = {'angle_shift': [91.0, 93.0], 'size_shift': [0.5, 0.05], 'glyph_angle_shift': [1.0, 3.0]}
spiral_params_waypoints['Promoter'] = {'angle_shift': [91.0, 92.0], 'size_shift': [0.1, 0.15], 'glyph_angle_shift': [3.0, 0.6]}

# Create each frame of the animation
spiral_params = {}
spiral_params['Terminator'] = {}
spiral_params['CDS'] = {}
spiral_params['Promoter'] = {}
num_of_frames = 50
for frame in range(num_of_frames):
    print('Generating frame:', frame+1, 'of', num_of_frames)
    # Calculate the current parameters for the frame
    run_frac = frame/float(num_of_frames)
    for k_type in spiral_params_waypoints.keys():
        for k_param in spiral_params_waypoints[k_type].keys():
            param_diff = spiral_params_waypoints[k_type][k_param][1] - spiral_params_waypoints[k_type][k_param][0]
            param_val_to_add = float(param_diff)*run_frac
            spiral_params[k_type][k_param] = spiral_params_waypoints[k_type][k_param][0]+param_val_to_add

    # Create the frame with current parameters
    generate_frame(spiral_params, waypoints, run_frac)

    # Add black background patch and bound plot
    rect = patches.Rectangle((-1000, -1000), 2000, 2000, facecolor='orange', zorder=-100)
    ax.add_patch(rect)
    ax.set_ylim([-100, 100])
    ax.set_xlim([-100, 100])

    # Save frame to file
    new_filename = "{:04d}{}".format(int(frame), '.png')
    fig.savefig('./frames/'+new_filename, dpi=180)
    plt.cla()
