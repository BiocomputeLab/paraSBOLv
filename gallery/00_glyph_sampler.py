"""
Displays all parametric SBOL Visual glyphs within the glyphs directory.
"""
import parasbolv as psv
import matplotlib.pyplot as plt

renderer = psv.GlyphRenderer()

parts = list(renderer.glyphs_library.keys())

# Identify glyphs that aren't drawn on a backbone
no_baselines = ['Macromolecule',
                'No Glyph',
                'Simple Chemical (Circle)',
                'Double-Stranded Nucleic Acid',
                'Single-Stranded Nucleic Acid',
                'Polypeptide Chain']
for glyph in no_baselines:
    if glyph in parts:
        parts.remove(glyph)

# Reused variables
start_position = (0, 0)
bounds_list = []
fig, ax = plt.subplots()

# Plot glyphs on backbone
part_list = []
for part in parts:
    part_list.append([part, None, None])
    part_list.append([part, {'rotation': 3.14}, None])

length = len(part_list)
r = length%12
number_of_rows = int((length - r)/12)

for n in range(number_of_rows+1):
    parts_to_draw = part_list[n*12:((n+1)*12)]
    if len(parts_to_draw) == 0:
        break
    start_position = (start_position[0], start_position[1]-40)
    construct = psv.Construct(parts_to_draw,
                              renderer,
                              fig = fig,
                              ax = ax,
                              start_position = start_position,
                              gapsize = 25)
    fig, ax, baseline_start, baseline_end, bounds = construct.draw()
    ax.plot([baseline_start[0], baseline_end[0]],
            [baseline_start[1], baseline_end[1]],
            color=(0,0,0), linewidth=1.5, zorder=0)
    bounds_list.append(bounds)

# Plot glyphs not on backbone
parts = list(renderer.glyphs_library.keys())

part_list = []
for part in no_baselines:
    if part in parts:
        part_list.append([part, None, None])
        part_list.append([part, {'rotation': 3.14}, None])

length = len(part_list)
r = length%12
number_of_rows = int((length - r)/12)

for n in range(number_of_rows+1):
    parts_to_draw = part_list[n*12:((n+1)*12)]
    if len(parts_to_draw) == 0:
        break
    start_position = (start_position[0], start_position[1]-40)
    construct = psv.Construct(parts_to_draw,
                              renderer,
                              fig = fig,
                              ax = ax,
                              start_position = start_position,
                              gapsize = 25)
    fig, ax, baseline_start, baseline_end, bounds = construct.draw()
    bounds_list.append(bounds)

# Get bounds
bounds = psv.__find_bound_of_bounds(bounds_list)
ax.set_ylim(bounds[0][1]-10, bounds[1][1]+10)
ax.set_xlim(bounds[0][0]-10, bounds[1][0]+10)

fig.savefig('00_glyph_sampler.pdf', transparent=True, dpi=300)

plt.show()
