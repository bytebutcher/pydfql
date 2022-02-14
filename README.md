<p align="center">
    <img src="https://github.com/bytebutcher/python-dict-display-filter/raw/main/images/python_dict_display_filter_logo.png" alt="python_dict_display_filter Logo"/>
</p>
<p align="center"><font size="5">Python Dictionary Display Filter</font></p>
<div align="center">

![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)
![PyPI](https://img.shields.io/pypi/v/python-dict-display-filter)
![GitHub](https://img.shields.io/github/license/bytebutcher/python-dict-display-filter)
</div>
<br>

Wireshark-like display filter for python dictionaries.

## Setup
```commandline
pip3 install python-dict-display-filter
```

## Usage

The basics and the syntax of the display filter are described in the 
<a href="https://github.com/bytebutcher/python-dict-display-filter/blob/main/docs/USER_GUIDE.md">User Guide</a>.

If you want to see some advanced examples of how ```python-dict-display-filter``` can be put to use checkout the 
<a href="https://github.com/bytebutcher/python-dict-display-filter/blob/main/docs/EXAMPLES.md">Examples</a>.

If you want to use ```python-dict-display-filter``` in your own application and customize it to your needs 
check out the 
<a href="https://github.com/bytebutcher/python-dict-display-filter/blob/main/docs/DEVELOPER_GUIDE.md">Developer Guide</a>.

## Examples 

Initialize ```DictDisplayFilter``` with a dictionary:
```
> from pydictdisplayfilter import DictDisplayFilter
> actors = [
    {"name": ["Laurence", "Fishburne"], "age": {"born": "1961"}, "gender": "male"},
    {"name": ["Keanu", "Reeves"], "age": {"born": "1964"}, "gender": "male", "power": ["flight", "bulle-time"]},
    {"name": ["Joe", "Pantoliano"], "age": {"born": "1951"}, "gender": "male"},
    {"name": ["Carrie-Anne", "Moss"], "age": {"born": "1967"}, "gender": "female"}
]
> ddf = DictDisplayFilter(actors)
```

Show only actors with some kind of super-power:
```
> ddf.filter("power")
```

Show only actors which were born before 1965:
```
> ddf.filter("age.born < 1965")
```

Show only female actors:
```
> ddf.filter("gender == female")
```

Show all male actors which are born between 1960 and 1965:
```
> ddf.filter("gender == male and (age.born > 1960 and age.born < 1965)")
```

Show all actors which name contain the character 'e':
```
> ddf.filter("name contains e")
```

Show all actors which name matches a regular expression:
```
> ddf.filter("name matches .*e$")
```
