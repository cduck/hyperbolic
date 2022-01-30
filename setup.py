from setuptools import setup, find_packages
import logging
logger = logging.getLogger(__name__)

name = 'hyperbolic'
package_name = name
version = '1.4.0'

try:
    with open('README.md', 'r') as f:
        long_desc = f.read()
except:
    logger.warning('Could not open README.md.  long_description will be set to None.')
    long_desc = None

setup(
    name = package_name,
    packages = find_packages(),
    version = version,
    description = 'A Python 3 library for constructing and drawing hyperbolic geometry',
    long_description = long_desc,
    long_description_content_type = 'text/markdown',
    author = 'Casey Duckering',
    #author_email = '',
    url = f'https://github.com/cduck/{name}',
    download_url = f'https://github.com/cduck/{name}/archive/{version}.tar.gz',
    keywords = ['hyperbolic', 'geometry', 'draw', 'SVG'],
    classifiers = [
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
    install_requires = [
        'numpy',
    ],
)
