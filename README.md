# CAASP Analysis

Execution notes:
- requires several mathematics libraries
  - numpy
    - specific version required due to python jank; use `pip install "numpy<2" --upgrade`
  - scipy
  - matplotlib
- may require libraries for scraping if you're running that part
  - urllib
  - bs4

Furthermore, this code is intended for Python 3.12. Newer or older versions may fail to function properly. It was tested on a MacOS machine on Apple Silicon; systems with incompatible matrix routines may differ in float handling.

