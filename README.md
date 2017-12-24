# colour-detection
python module for doing colour detection

# Installing
clone -> `cd colour-detection -> python3 setup.py install` - may eventually put this on pip.
You can also run `pip install git+https://github.com/godley/colour-detection` to achieve the same thing or add `git+https://github.com/godley/colour-detection` to your requirements.txt file.

# Usage
```
from colourdetection import calibrate, test, detect

test(<absolute-path-to-image>, <list-of-str-colours>)
```
This will run calibrate, which allows you to calibrate the image according to light levels, then detects based on the result
of the calibrate stage. Docstrings should be enough to understand what's going on, if unclear contact me or raise an issue/PR.

# Thanks!
Thanks to [piborg](https://piwars.org/2018-competition/challenges/somewhere-over-the-rainbow/over-the-rainbow-sample-code/) for the original sample code.