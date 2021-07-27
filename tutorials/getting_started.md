# Getting started with paraSBOLv

`paraSBOLv` is a lightweight Python library designed to simplify the rendering of highly-customisable SBOL Visual glyphs and diagrams. To begin, it is necessary to import the following packages:

	import parasbolv as psv
	import matplotlib.pyplot as plt
	
`paraSBOLv` contains all the code to render SBOL Visual compliant glyphs corresponding to biological parts and `matplotlib` is used as a canvas on which to draw the design.
	
## Initialising a figure and axis for drawing

Once the necessary imports have been made, `Figure` and `Axes` objects are required by `paraSBOLv` to act as a canvas. A typical way to generate these is using:

    fig, ax = plt.subplots()

The `fig` and `ax` objects are then used for all future drawing commands.

## Initialising `GlyphRenderer`

Before drawing a biological design, a `GlyphRenderer` object must first be created.

    renderer = psv.GlyphRenderer()

By default the `GlyphRenderer` constructor will use the built-in set of parametric SVG glyphs. However, if you would like to create a renderer able to access your own glyphs the named `glyph_path` argument can be provided with the path to the directory containing the parametric SVG files to be used:

    renderer = psv.GlyphRenderer(glyph_path = 'path')

As the name suggests, a `GlyphRenderer` objects renders glyphs from parametric SVG files to an `matplotlib` axis.

## Drawing Glyphs

With a `renderer` object now initialised, it is now possible to draw glyphs using the `draw_glyph` method:
	
	bounds, end_point = renderer.draw_glyph(ax, 'GLYPH NAME', (0, 0) )

The return values from this method provide the `bounds` of the drawn glyph (i.e. the bounding box that spans the glyph) and the `end_point` of the glyph, which is the end of the baseline that can be used as a starting point for the next glyph, if a more complex design needs to be drawn.

For example, to draw a promoter glyph at position (0, 0) you would use:

	bounds, end_point = renderer.draw_glyph(ax, 'Promoter', (0, 0))

Be aware that in order to see the design you have drawn it may be necessary to tell `matplotlib` to `show` the current figure on the screen:

    plt.show()

or to save the figure to file:

    plt.save_fig

We can make use of the parameterised SVG files to customise each glyphs in many different ways. For example, say we wanted to draw a coding sequence glyph (CDS) that has been **widened** and **rotated** 90 degrees (π/2), with a **blue colored face** and **red colored edges**. This can be achieved by using the following lines of code:

	user_parameters = { 'width' : 50 }
	
	user_style = {
		      'cds' : {
		  	       'facecolor': (0,0,1),
			       'edgecolor': (1,0,0)
		      }
	}
	
	bounds, end_point = renderer.draw_glyph(
					       ax,
					       'CDS',
					       (0,0),
					       user_parameters = user_parameters
					       user_style = user_style,
					       rotation = 3.14/2
	)

You will notice that two different dictionaries are sent to the `draw_glyph` function. The first, `user_parameters` holds parameter-value pairs for each parameter defined for the parametric SVG file. These tend to be parameters that affect the shape/geometry of the glyph. The second, `user_style`, captures standard `matplotlib` styling information for each path that makes up the glyph. In this example, a coding sequence glyph contains a single path called `cds`. The `user_style` dictionary has key-value pairs where each path name acts as a key with the value another dictionary containing standard `matplotlib` styling options (e.g. line widths and colors).

## Initialising a `Construct`

The easiest way to plot many glyphs in succession as a single design is using a `Construct` object. A `Construct` consists of a list of parts, where each part is represented by a [`named_tuple`](https://bit.ly/2Tu8IMK) like so:

	Part = namedtuple(
			  'part', ['glyph_type',
				   'orientation',
				   'user_parameters', 
				   'user_style']
	)

	part_example = Part(
			    'part_name',
			    'orientation', # forward or reverse
			    {user_parameters}, # Falsy object if there are none
			    {user_style} # Falsy object if there are none
	)
	
A part list is merely a standard list of these objects:

	part_list = [
	             cds_part,
	             promoter_part,
	             cds_part
	]

Finally, a construct can be created by passing (at least) a `GlyphRenderer` object and `part_list` to the constructor:

	construct = psv.Construct(part_list, renderer, fig=fig, ax=ax)

Note that `fig`and `ax` are keyword arguments; if excluded, `Construct` will generate them itself and hold them as attributes. The `draw` method of the `Construct` object can then be used to render the design,

	fig, ax, baseline_start, baseline_end, bounds = construct.draw()

By default, a backbone is not drawn for a design, but this can be easily added by using the `baseline_start` and `baseline_end` value:

    ax.plot([baseline_start[0], baseline_end[0]], [baseline_start[1], baseline_end[1]], color=(0,0,0), linewidth=1.5, zorder=0)

There are a number of additional options that can also be used when creating a construct to alter the start position, spacing between glyphs and the overall rotation: 

	construct = psv.Construct(
				  part_list,
				  renderer,
				  start_position = (9,6),
				  gapsize = 8,
				  rotation = 3.14/4,
	)

## Specifying interactions

Interactions between glyphs can be defined by passing an `interaction_list` to a construct. Interactions, like parts, are also defined as named tuples.

	Interaction = namedtuple(
				 'interaction', ['starting_glyph',
						 'ending_glyph',
						 'interaction_type', 
						 'interaction_parameters']
							  )

	interaction_example = Interaction(
					  part1,
					  part2,
					  'Interaction Name',
					  interaction_parameters,
						  )

They are then passed to the `Construct` constructor:

	interaction_list = [
			    interaction1,
			    interaction2
	] 

	construct = psv.Construct(
				  part_list,
				  renderer,
				  interaction_list = interaction_list
			   )

That covers the basics of using paraSBOLv. Please see the rest of the documentation for detailed information on other available options and the [gallery](../gallery/) for examples of paraSBOLv in use.