<p align="center">
    <img src="https://github.com/bytebutcher/python-dict-display-filter/raw/main/images/python_dict_display_filter_logo.png" alt="python_dict_display_filter Logo"/>
</p>
<h1 align="center" style="margin-top: 0px;">Python Dictionary Display Filter</h1>
<div align="center">

![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)
![PyPI](https://img.shields.io/pypi/v/python-dict-display-filter)
![GitHub](https://img.shields.io/github/license/bytebutcher/python-dict-display-filter)
![Build Status](https://img.shields.io/travis/com/bytebutcher/python-dict-display-filter)
![Coverage](https://img.shields.io/codecov/c/github/bytebutcher/python-dict-display-filter)
</div>
<br>

A Wireshark-like display filter for Python dictionaries and various other data 
sources, including objects, lists, and SQL databases. 

## Table of Contents
1. [Quick Start](#quick-start)
2. [Features](#features)
3. [Examples](#examples)
4. [Acknowledgements](#acknowledgements)

## Quick Start

To quickly get started with the python-dictionary-display-filter, follow the steps below:

### Installation
First, install the package using pip:

```commandline
pip3 install python-dict-display-filter
```

### Initialization
Next, import the necessary module and initialize the ```DictDisplayFilter``` with a list of dictionaries:
```python
from pydictdisplayfilter import DictDisplayFilter

actors = [
    {"name": ["Laurence", "Fishburne"], "age": {"born": "1961"}, "gender": "male"},
    {"name": ["Keanu", "Reeves"], "age": {"born": "1964"}, "gender": "male", "power": ["flight", "bullet-time"]},
    {"name": ["Joe", "Pantoliano"], "age": {"born": "1951"}, "gender": "male"},
    {"name": ["Carrie-Anne", "Moss"], "age": {"born": "1967"}, "gender": "female"}
]

ddf = DictDisplayFilter(actors)
```

### Filtering Data
Once the ```DictDisplayFilter``` is initialized, you can start filtering the data using the 
<a href="https://github.com/bytebutcher/python-dict-display-filter/blob/main/docs/USER_GUIDE.md#4-query-language">display filter query language</a>.
For example, let's filter the actors whose birth year is after 1960:
```python
filter_query = "age.born > 1960"
filtered_data = ddf.filter(filter_query)
print(list(filtered_data))
[
    {"name": ["Laurence", "Fishburne"], "age": {"born": "1961"}, "gender": "male"},
    {"name": ["Keanu", "Reeves"], "age": {"born": "1964"}, "gender": "male", "power": ["flight", "bullet-time"]},
    {"name": ["Carrie-Anne", "Moss"], "age": {"born": "1967"}, "gender": "female"}
]
```

You can also use more complex queries to filter the data. 
For example, let's filter male actors born between 1960 and 1964 whose names end with "e":

```python
filter_query = "gender == male and (age.born > 1960 and age.born < 1965) and name matches .*e$"
filtered_data = ddf.filter(filter_query)
print(list(filtered_data))
```

This will output the filtered data:
```python
[{'name': ['Laurence', 'Fishburne'], 'age': {'born': '1961'}, 'gender': 'male'}]
```

For more details and advanced usage, please refer to the 
<a href="https://github.com/bytebutcher/python-dict-display-filter/blob/main/docs/USER_GUIDE.md">User Guide</a>.

## Features

Python Dictionary Display Filter supports a wide range of features, including:
* **Comparison Operators:** ```==```, ```!=```, ```<=```, ```<```, ```>=```, ```>```, ```~=```, ```~```, ```&```
* **Combining Operators:** ```and```, ```or```, ```xor```, ```not``` 
* **Membership Operators:** ```in```
* **Types:** ```Text```, ```Number```, ```Date & Time```, ```Ethernet-```, ```IPv4-```, ```IPv6-Address```
* **Slicing:** ```Text```, ```Ethernet-```, ```IPv4-```, ```IPv6-Address```
* **Functions:** ```upper```, ```lower```, ```len```
* **Data Sources**: ```CSV```, ```Dictionaries```, ```JSON```, ```Objects```, ```SQLite```

For a detailed description of the individual features check out the
<a href="https://github.com/bytebutcher/python-dict-display-filter/blob/main/docs/USER_GUIDE.md">User Guide</a>.

## Examples 

For detailed examples of how the display filter can be utilized, please refer to the following sections of the 
<a href="https://github.com/bytebutcher/python-dict-display-filter/blob/main/docs/USER_GUIDE.md">User Guide</a>:

* [CSV Display Filter](https://github.com/bytebutcher/python-dict-display-filter/blob/main/docs/USER_GUIDE.md#51-csv-display-filter)
* [JSON Display Filter](https://github.com/bytebutcher/python-dict-display-filter/blob/main/docs/USER_GUIDE.md#52-json-display-filter)
* [SQLite Display Filter](https://github.com/bytebutcher/python-dict-display-filter/blob/main/docs/USER_GUIDE.md#53-sqlite-display-filter)
* [Nmap Display Filter](https://github.com/bytebutcher/python-dict-display-filter/blob/main/docs/USER_GUIDE.md#54-nmap-display-filter)

## Acknowledgements

This project wouldn't be possible without these awesome projects:

* <a href="https://wiki.wireshark.org/DisplayFilters">wireshark display filter</a>: Display filter for filtering network packages
* <a href="https://github.com/wolever/parameterized">parameterized</a>: Parameterized testing with any Python test framework
* <a href="https://github.com/pyparsing/pyparsing/">pyparsing</a>: Creating PEG-parsers made easy
* <a href="https://github.com/bytebutcher/ipranger/">ipranger</a>: Parsing and matching IPv4-addresses
* <a href="https://pypi.org/project/python-dateutil/">python-dateutil</a>: Parsing and comparing dates 
