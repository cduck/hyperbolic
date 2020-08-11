[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.3978772.svg)](https://doi.org/10.5281/zenodo.3978772)

# hyperbolic

This is a Python 3 library for generating hyperbolic geometry and drawing it with the [drawSvg](https://github.com/cduck/drawSvg) library.  Currently the Poincaré disk and half-plane models are supported.

# Install
hyperbolic is available on PyPI:
```
$ pip3 install hyperbolic
```

Install drawSvg also to display the hyperbolic geometry:
```
$ pip3 install drawSvg
```

# Examples

See the iPython notebooks in [examples](https://github.com/cduck/hyperbolic/tree/master/examples):

- [Euclidean geometry](https://github.com/cduck/hyperbolic/blob/master/examples/euclid.ipynb)
- [Poincaré disk and plane](https://github.com/cduck/hyperbolic/blob/master/examples/poincare.ipynb)
- [Tiling the Poincaré disk and plane](https://github.com/cduck/hyperbolic/blob/master/examples/tiles.ipynb)

Using this library, along with the drawSvg library, you can create art like this hyperbolic weave:

![Hyperbolic weave](https://github.com/cduck/hyperbolic/raw/master/examples/images/weave.png)

This weave is built from a tiling of isosceles triangles:

![Hyperbolic weave structure](https://github.com/cduck/hyperbolic/raw/master/examples/images/weaveStructure.png)

