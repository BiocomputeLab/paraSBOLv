# paraSBOLv

A lightweight Python library designed to simplify the rendering of highly-customisable SBOL Visual glyphs and diagrams. To do this, `paraSBOLv` uses the Parametric Scalable Vector Graphic (SVG) format to enable the encoding of shape geometry and allowed parametric variations on this. The best way to learn how to use `paraSBOLv` is to dive into our [`gallery`](./gallery/) of examples.

## Dependancies

`paraSBOLv` does not require any other dependancies when installed. However, internally it does make use of the wonderful [`svgpath2mpl`](https://github.com/nvictus/svgpath2mpl) library to handle the generation of [`matplotlib`](https://matplotlib.org) compatible paths from an SVG path string. Do check this out if you'd like to know more about using SVG with [`matplotlib`](https://matplotlib.org).

## Support

If you use this tool to create diagrams or as a basis for new software please cite the following paper that provides an overview of the tool and possible use cases. Without citations the support of this tool become difficult.

`Clark C., Scott-Brown J. & Gorochowski T.E. "paraSBOLv: a foundation for standard-compliant genetic design visualisation tools" (in prep.)`
