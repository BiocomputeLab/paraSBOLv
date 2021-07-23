# Getting started

`paraSBOLv` is a lightweight Python library designed to simplify the rendering of highly-customisable SBOL Visual glyphs and diagrams. To begin, perform the following essential imports:

	import parasbolv as psv
    import matplotlib.pyplot as plt

**Initialising `fig` and `ax`**

`Figure` and `Axes` objects are required for `paraSBOLv` usage. We typically generate them like so:

    fig, ax = plt.subplots()

**Initialising `GlyphRenderer`**

Before drawing, an object from the `GlyphRenderer` class must first be initialised and a directory of parametric SVG files -- referred to as glyphs -- loaded:

    renderer = psv.GlyphRenderer(glyph_path = 'path')
    
    # If the glyph_path argument is unspecified, paraSBOLv
    # will attempt to search for and load a glyphs directory.

As the name suggests, `GlyphRenderer` renders glyphs from parametric SVG files and draws them on `fig` and `ax`.

**Drawing Glyphs**

With our `renderer` object initialised, we can draw glyphs using the `draw_glyph` method:
	
	bounds, end_point = renderer.draw_glyph(ax, 'GLYPH NAME', (0, 0) )
	
	# bounds: coordinates indicating the boundaries of the glyph
	# end_point: coordinates indicating where the glyph ends

For example, to draw a ribosome entry site glyph at position (0, 0) :

	bounds, end_point = renderer.draw_glyph(ax, 'RibosomeEntrySite', (0, 0) )

We can make use of the parameterised SVG files and customise our glyphs in many different ways. Here we draw a coding sequence glyph (CDS) that has been **widened** and **rotated** 90 degrees (π/2), with a **blue face** and **red edges**.

	user_parameters = {
					   'width' : 50
	}
	
	user_style = {
				  'cds' : {
						   'facecolor': (0,0,1),
						   'edgecolor': (1,0,0),
					                  # (R,G,B)
				  }
	}
	
	bounds,end_point = renderer.draw_glyph(
											ax,
											'CDS',
											(0,0),
											user_parameters = user_parameters,
											user_style = user_style,
											rotation = 3.14/2
						)


 - Rotation and position are passed directly to the `draw_glyph` method.
 - The `user_parameters` dictionary handles glyph size parameters and labels
 - The `user_style`dictionary handles colour and line widths

**Initialising a `Construct`**

The easiest way to plot many glyphs in succession is with the `Construct` class, which can apply parameters to and render  a `part_list`, an ordered list of glyphs. Glyphs in part lists are represented by `named_tuples` (https://bit.ly/2Tu8IMK) like so:

	Part = namedtuple(
				        	  'part', ['glyph_type',
							               'orientation',
							               'user_parameters', 
							               'style_parameters']
	)

	part_example = Part(
				          		'part_name',
					            'orientation', # Forward or Reverse
					          	{user_parameters}, # Falsy object if there is none
				          		{style_parameters} # Falsy object if there is none
						)
	
and formatted in part lists:

	part_list = [
	            	cds_part,
	             	promoter_part,
	            	cds_part
	]
	
	# All parts in the part list are named tuple objects

A construct is then created by passing (at least) a `GlyphRenderer` object and a `part_list` to `Construct`:

	construct = psv.Construct(part_list, renderer, fig=fig, ax=ax)

Note that `fig`and `ax` are keyword arguments; if excluded, `Construct` will generate them itself and hold them as attributes. The `draw`method then renders the construct,

	fig, ax, baseline_start, baseline_end, bounds = construct.draw()

and `Matplotlib` can be used to draw a baseline from `baseline_start`to `baseline_end`.

Among the construct parameters that can be specified are the start position, space between glyphs, and rotation of constructs:

	construct = psv.Construct(
						            	  part_list,
					              	  renderer,
					              	  start_position = (9,6),
							              gapsize = 8,
							              rotation = 3.14/4,
	)

**Specifying interactions**

Finally, interactions between glyphs can be defined by passing an `interaction_list` to a construct. Interactions, like parts, are defined as named tuples.

	Interaction = namedtuple(
							             'interaction', ['starting_glyph',
											                      'ending_glyph',
										                        'user_parameters', 
										                        'style_parameters']
							  )

	interaction_example = Interaction(
									                  part1
									                  part2
									                  'Interaction Name'
									                  interaction_parameters
						  )

They are then passed to `Construct` in a list.

	interaction_list = [
					          	interaction1,
		          				interaction2
	] 

	construct = psv.Construct(
					              		part_list,
					              		renderer,
						              	interaction_list = interaction_list
			   )

Please see the rest of the documentation for detailed information on all possible parameters for `user_parameters`, `user_style`, `interaction_parameters`, and `Construct`.

