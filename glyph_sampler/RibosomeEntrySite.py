
import parasbolv as psv
import matplotlib.pyplot as plt

part_list = []

part_list.append(['RibosomeEntrySite', None, None])
part_list.append(['RibosomeEntrySite', {'rotation':3.14}, None])
renderer = psv.GlyphRenderer()
construct = psv.Construct(part_list, renderer)

fig, ax, baseline_start, baseline_end, bounds = construct.draw()
ax.plot([baseline_start[0]-1, baseline_end[0]+1], [baseline_start[1], baseline_end[1]], color=(0,0,0), linewidth=1.5, zorder=0)

ax.set_ylim([-40,40])
ax.set_xlim([-10,80])
      
fig.savefig('RibosomeEntrySite.pdf', transparent=True, dpi=300)

plt.show()
              