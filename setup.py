from setuptools import setup

setup(
    name='colour-detection',
    version='0.1',
    packages=['colourdetection'],
    url='https://github.com/godley/colour-detection',
    license='MIT',
    author='Charlotte Godley',
    author_email='charlotte.godley@hotmail.co.uk',
    description='python module for colour detection. Abstracted from opencv',
    install_requires=['opencv-python']
)
