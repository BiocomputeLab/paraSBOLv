# Creating parametric SVG files for new glyphs

To create a parametric SVG glyph that is compatible with `paraSBOLv` it is necessary to follow some basic guidelines. First, it should be noted that all parametric glyphs at their core are standard SVG files. These can be created using graphic design software or by hand-coding the paths making up the glyph.

Once you have a starting SVG file that you wish to parameterise it is necessary to add the `parametric` namespace to the XML file. This is done by adding the following attribute to the main `svg` tag:

    xmlns:parametric="https://parametric-svg.github.io/v0.2"
    
Next, there are three additional attributes that must also be added to this tag:

1. `glyphtype` - This is a unique name for the type of glyph.

2. `terms` - This is a comma separated list of terms that are generally connected to the SO Terms of the corresponding SBOL part. This may be used in the future to help connect, glyphs to parts in an SBOL data file. At present though it is not used.

3. `parametric:defaults` - This is a semi-colon separated list of key=value pairs where the keys are parameters used and their default values.

This results in a final `svg` tag that looks something like the following (taken from the CDS glyph):

    <svg xmlns="http://www.w3.org/2000/svg" xmlns:parametric="https://parametric-svg.github.io/v0.2" version="1.1" width="100" height="100" glyphtype="CDS" terms="SO:0000316" parametric:defaults="arrowbody_height=15;arrowhead_width=7;width=30;height=15">

Now that the file is able to include parametric attributes, it is useful to parameterise each of the core paths making up the glyph. This is done by adding a `parametric:d` attribute to each `path` tag with the hard-coded values of each path, edited to include parametric definitions based on the parameters defined in the core `svg` tags `parametric:defaults` attribute. To ensure new glyphs are consistent in their parameter use with expect all glyphs to use the minimal number of parameters possible and conform to the same naming of parameters where possible. For example, nearly all existing glyphs have parameters for the `width` and `height` used to appropriately scale the glyph. To give an example of what

    <path class="filled-path" d="M2,25 L2,17.5 L26,17.5 L26,17.5 L32,25 L26,32.5 L26,32.5 L2,32.5 Z" style="fill:rgb(230,230,230);fill-rule:nonzero;stroke:black;stroke-width:1pt;stroke-linejoin:miter;stroke-linecap:butt" />
   
is transformed into:

    <path class="filled-path" d="M2,25 L2,17.5 L26,17.5 L26,17.5 L32,25 L26,32.5 L26,32.5 L2,32.5 Z" parametric:d="M{0},{0} L{0},{-arrowbody_height/2} L{width - arrowhead_width},{-arrowbody_height/2} L{width - arrowhead_width},{-height/2} L{width},{0}  L{width - arrowhead_width},{height/2} L{width - arrowhead_width},{arrowbody_height/2} L{0},{arrowbody_height/2} Z" style="fill:rgb(230,230,230);fill-rule:nonzero;stroke:black;stroke-width:1pt;stroke-linejoin:miter;stroke-linecap:butt" />

In addition to parameterising the paths making up the glyph, some additional paths and bounding box should be provided to ensure that `paraSBOLv` knows where the baseline of a design is located and to capture the bounds of the glyph to avoid overlapping of visual content where possible. Again, these two elements should be parameterised such that their shape changes in accordance with the glyph and new parameters are supplied.

As an example, here are the `bounding-box` and `baseline` elements for the CDS glyph:

     <rect class="bounding-box" id="bounding-box" parametric:x="{0}" x="0" parametric:y="{-height/2}" y="14.5" parametric:width="{width}" width="34" parametric:height="{height}" height="21.0" style="fill:none;stroke:rgb(150,150,150);stroke-opacity:0.5;stroke-width:1pt;stroke-linecap:butt;stroke-linejoin:miter;stroke-dasharray:1.5,0.8" />

     <path class="baseline" id="baseline" parametric:d="M{0},{0} L{width},{0}" d="M0,25 L34,25" parametric:y="{0}" style="fill:none;stroke:black;stroke-width:1pt" />

And that is it! With these additional elements the glyph is now usable by `paraSBOLv`.

# More information

For more information regarding the parametric SVG format see: [http://parametric-svg.js.org](http://parametric-svg.js.org)