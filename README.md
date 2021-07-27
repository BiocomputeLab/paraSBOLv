# paraSBOLv

A lightweight Python library designed to simplify the rendering of highly-customisable SBOL Visual glyphs and diagrams. To do this, `paraSBOLv` uses the [Parametric Scalable Vector Graphic (pSVG)](https://parametric-svg.js.org) format to enable the encoding of the shape geometry and allowed parametric variations for each glyph. The best way to learn how to use `paraSBOLv` is to dive into our [`gallery`](./gallery/) of examples which cover most of the capabilities present. In addition, all functions and classes are extensively documented in code to allow usage to be easily inferred.

![Example image generated by paraSBOLv](gallery/04_plot_gff/04_plot_gff.jpg?raw=true "Example image generated by paraSBOLv")


## Relationship to DNAplotlib

We are regularly asked about the relationship of `parasbolv` and another genetic design visualisation tool we have developed called [`dnaplotlib`](http://www.dnaplotlib.org). The major difference between the two packages is that `parasbolv` is designed to be lightweight, include minimal additional functionality, and be tailored to tool developers to provide them with low level access to the rendering of SBOL Visual glyphs and interactions. In contrast, `dnaplotlib` is designed to provide a much fuller and wider range of functionalities to both developers and biologists.

As a note, `dnaplotlib` version 2.0, which is currently under development, will completely replace its legacy rendering pipeline with `paraSBOLv`. This will not only simplify maintenance, but also allow access to new glyphs ratified by the SBOL community as they become available.

## Dependancies

`paraSBOLv` does not require any other dependancies when installed. However, internally it does make use of the [`svgpath2mpl`](https://github.com/nvictus/svgpath2mpl) package to handle the generation of `matplotlib` compatible paths from an SVG path string. Do check this package out if you'd like to know more about using SVG with `matplotlib`.

## Installation

The easiest way to start playing with `parasbolv` is to clone this repository and place the `parasbolv` directory into you `PYTHONPATH` environment variable. Once done, it should be possible to then:

```
import parasbolv as psv
```

## Documentation

Automatically generated documentation can be accessed at: [https://biocomputelab.github.io/paraSBOLv/index.html](https://biocomputelab.github.io/paraSBOLv/index.html)

## Tutorials

- [Getting started with paraSBOLv](tutorials/getting_started.md) - This provides a basic introduction to the `paraSBOLV` library and the core data types of functions available. It is recommended that this is used together with the [examples gallery](./gallery/).

- [Creating parametric SVG glyph files](creating_psvg_glyphs) - If you are looking to create new parametric glyphs to use with this library then this provides an overview of the core elements that need to be added. If you are creating a new glyph that you think others in the synthetic biology might find useful, please consider also submitting to the [SBOL Visual standard](https://sbolstandard.org).

## Tools

To inspire you to make your own, we created some simple plotting tools using paraSBOLv as a convenient foundation. 

**[genbank2sbolv](gallery/genbank2sbolv)** - visualises the coding regions within a GenBank file.

**[sbolv-cli](gallery/sbolv-cli)** - streamlined CLI version of paraSBOLv for rapid generation of designs from the command line.

## Support

If you use this tool to create diagrams or as a basis for new software please cite the following paper. Without citations that demonstrate use it becomes difficult to support this tool.

`Clark C.J., Scott-Brown J. & Gorochowski T.E. "paraSBOLv: a foundation for standard-compliant genetic design visualisation tools" (in revision)`
