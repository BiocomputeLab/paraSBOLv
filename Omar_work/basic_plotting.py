import parasbolv as psv
import matplotlib.pyplot as plt

# Generate Matplotlib Figure and Axes
fig = plt.figure(figsize=(6,6))
ax = fig.add_axes([0.0, 0.0, 1.0, 1.0], frameon=False, aspect=1)

# Generate renderer object
renderer = psv.GlyphRenderer()

bounds, end_point = renderer.draw_glyph(ax, 'Omar', (20, 50))

# Set Bounds
ax.set_ylim([0,100])
ax.set_xlim([0,100])

fig.savefig('01_basic_plotting.pdf', transparent=True, dpi=300)
fig.savefig('01_basic_plotting.jpg', dpi=300)
plt.show()