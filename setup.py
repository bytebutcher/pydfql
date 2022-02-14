import pathlib
import setuptools
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="python-dict-display-filter",
    version="0.9.2",
    description="A Wireshark-like display filter for dictionaries.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/bytebutcher/python-dict-display-filter",
    author="bytebutcher",
    author_email="thomas.engel.web@gmail.com",
    license="GPL-3.0",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent"
    ],
    packages=setuptools.find_packages(),
    install_requires=[
        'parameterized==0.8.1',
        'pyparsing==3.0.6',
        'ipranger==1.1.2',
        'python-dateutil==2.8.2'
    ],
    include_package_data=True,
)
