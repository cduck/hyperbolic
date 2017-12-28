# hyperbolic

This is a Python 3 library for generating hyperbolic geometry and drawing it with the drawSvg library.  Currently only the Poincaré disk model is supported.

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
- [Poincaré disk model](https://github.com/cduck/hyperbolic/blob/master/examples/poincare.ipynb)
- [Tiling the Poincaré disk](https://github.com/cduck/hyperbolic/blob/master/examples/tiles.ipynb)

Using this library, along with the drawSvg library, you can create art like this hyperbolic weave:

![Hyperbolic weave](https://github.com/cduck/hyperbolic/raw/master/examples/images/weave.png)

This weave is built from a tiling of isosceles triangles:

![Hyperbolic weave structure](https://github.com/cduck/hyperbolic/raw/master/examples/images/weaveStructure.png)

