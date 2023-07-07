<p align="center">
    <img src="https://github.com/bytebutcher/pydfql/raw/main/images/pydfql_logo.png" alt="pydfql Logo"/>
</p>
<h1 align="center" style="margin-top: 0px;">Python Display Filter Query Language</h1>
<div align="center">

![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)
![PyPI](https://img.shields.io/pypi/v/pydfql)
![GitHub](https://img.shields.io/github/license/bytebutcher/pydfql)
![Build Status](https://img.shields.io/travis/com/bytebutcher/pydfql)
![Coverage](https://img.shields.io/codecov/c/github/bytebutcher/pydfql)
</div>
<br>

A Wireshark-like display filter various data formats, including Python dictionaries, lists, objects, and SQL databases. 

## Table of Contents
1. [Quick Start](#quick-start)

    1.1 [Installation](#installation)

    1.2 [Initialization](#initialization)

    1.3 [Filtering Data](#filtering-data)

2. [Examples](#examples)
3. [Acknowledgements](#acknowledgements)

## Quick Start

To quickly get started follow the steps below:

### Installation
First, install the package using pip:

```commandline
pip3 install pydfql
```

### Initialization
Next, import the necessary module and initialize the appropriate display filter with some data.
In the example below we are initializing the ```ObjectDisplayFilter``` with a list of objects:
```python
from dataclasses import dataclass
from pydfql import ObjectDisplayFilter

@dataclass
class Actor:
    name: list
    age: dict
    gender: str

actors = [
    Actor(["Laurence", "Fishburne"], {"born": "1961"}, "male"),
    Actor(["Keanu", "Reeves"], {"born": "1964"}, "male"),
    Actor(["Joe", "Pantoliano"], {"born": "1951"}, "male"),
    Actor(["Carrie-Anne", "Moss"], {"born": "1967"}, "female")
]

df = ObjectDisplayFilter(actors)
```

### Filtering Data
Once the display filter is initialized, you can start filtering the data using the 
<a href="https://github.com/bytebutcher/pydfql/blob/main/docs/USER_GUIDE.md#4-query-language">display filter query language</a>.
For example, let's filter the actors whose birth year is after 1960:
```python
filter_query = "age.born > 1960"
filtered_data = df.filter(filter_query)
print(list(filtered_data))
[
    Actor(name=['Laurence', 'Fishburne'], age={'born': '1961'}, gender='male'),
    Actor(name=['Keanu', 'Reeves'], age={'born': '1964'}, gender='male'),
    Actor(name=['Carrie-Anne', 'Moss'], age={'born': '1967'}, gender='female')
]
```

You can also use more complex queries to filter the data. 
For example, let's filter male actors born between 1960 and 1964 whose names end with "e":

```python
filter_query = "gender == male and (age.born > 1960 and age.born < 1965) and name matches .*e$"
filtered_data = df.filter(filter_query)
print(list(filtered_data))
```

This will output the filtered data:
```python
[Actor(name=['Laurence', 'Fishburne'], age={'born': '1961'}, gender='male')]
```

Overall, PyDFQL supports a wide range of features, including:
* **Data Types**: ```Dictionaries```, ```Lists```, ```Objects```, ```SQL```
* **Comparison Operators:** ```==```, ```!=```, ```<=```, ```<```, ```>=```, ```>```, ```~=```, ```~```, ```&```
* **Combining Operators:** ```and```, ```or```, ```xor```, ```not``` 
* **Membership Operators:** ```in```
* **Types:** ```Text```, ```Number```, ```Date & Time```, ```Ethernet-```, ```IPv4-```, ```IPv6-Address```
* **Slicing:** ```Text```, ```Ethernet-```, ```IPv4-```, ```IPv6-Address```
* **Functions:** ```upper```, ```lower```, ```len```

For a detailed description of the individual features check out the
<a href="https://github.com/bytebutcher/pydfql/blob/main/docs/USER_GUIDE.md">User Guide</a>.

## Examples 

For detailed examples of how the display filter can be utilized, please refer to the following:

* [CSV Display Filter](https://github.com/bytebutcher/pydfql/blob/main/docs/USER_GUIDE.md#51-csv-display-filter)
* [JSON Display Filter](https://github.com/bytebutcher/pydfql/blob/main/docs/USER_GUIDE.md#52-json-display-filter)
* [SQLite Display Filter](https://github.com/bytebutcher/pydfql/blob/main/docs/USER_GUIDE.md#53-sqlite-display-filter)
* [Nmap Display Filter](https://github.com/bytebutcher/pydfql/blob/main/docs/USER_GUIDE.md#54-nmap-display-filter)

## Acknowledgements

This project wouldn't be possible without these awesome projects:

* <a href="https://wiki.wireshark.org/DisplayFilters">wireshark display filter</a>: Display filter for filtering network packages
* <a href="https://github.com/wolever/parameterized">parameterized</a>: Parameterized testing with any Python test framework
* <a href="https://github.com/pyparsing/pyparsing/">pyparsing</a>: Creating PEG-parsers made easy
* <a href="https://github.com/bytebutcher/ipranger/">ipranger</a>: Parsing and matching IPv4-addresses
* <a href="https://pypi.org/project/python-dateutil/">python-dateutil</a>: Parsing and comparing dates 
