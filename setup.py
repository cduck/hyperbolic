from setuptools import setup, find_packages

try:
    with open('DESCRIPTION.rst', 'r') as f:
        longDesc = f.read()
except:
    print('Warning: Could not open DESCRIPTION.rst.  long_description will be set to None.')
    longDesc = None

setup(
    name = 'hyperbolic',
    packages = find_packages(),
    version = '1.1',
    description = 'This is a Python 3 library for generating hyperbolic geometry and drawing it with the drawSvg library.  Currently only the Poincaré disk model is supported.',
    long_description = longDesc,
    author = 'Casey Duckering',
    #author_email = '',
    url = 'https://github.com/cduck/hyperbolic',
    download_url = 'https://github.com/cduck/hyperbolic/archive/1.0.0.tar.gz',
    keywords = ['hyperbolic', 'geometry', 'draw'],
    classifiers = [
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
    install_requires = [
        'numpy',
    ],
)

