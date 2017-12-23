# colour-detection
python module for doing colour detection

# Installing
clone -> `cd colour-detection -> python3 setup.py install` - may eventually put this on pip

# Usage
```
from colourdetection import calibrate, test, detect

test(<absolute-path-to-image>, <list-of-str-colours>)
```
This will run calibrate, which allows you to calibrate the image according to light levels, then detects based on the result
of the calibrate stage. Docstrings should be enough to understand what's going on, if unclear contact me or raise an issue/PR.