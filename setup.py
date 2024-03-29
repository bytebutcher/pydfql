import pathlib
import setuptools
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="pydfql",
    version="1.3.0",
    description="A Wireshark-like display filter for querying data.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/bytebutcher/pyqfql",
    author="bytebutcher",
    author_email="thomas.engel.web@gmail.com",
    license="GPL-3.0",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent"
    ],
    packages=setuptools.find_packages(),
    install_requires=[
        'packaging==23.1',
        'parameterized==0.8.1',
        'pyparsing==3.0.6',
        'ipranger==1.1.2',
        'python-dateutil==2.8.2'
    ],
    extras_require={
        'test': [
            'pytest==7.3.1',
            'pytest-cov==4.0.0',
            'pexpect==4.8.0',
            'python-libnmap==0.7.0'
        ]
    },
    include_package_data=True,
)
