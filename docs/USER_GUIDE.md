<p align="center">
    <img src="https://github.com/bytebutcher/pydfql/raw/main/images/pydfql_logo.png" alt="pydfql Logo"/>
</p>
<h1 align="center" style="margin-top: 0px;">Python Display Filter Query Language</br>User Guide</h1>
<br>

## Table of Contents

1. [Introduction](#1-introduction)

2. [Installation](#2-installation)

3. [Usage](#3-usage)
   
   3.1 [ObjectDisplayFilter](#31-objectdisplayfilter)

   3.1 [DictDisplayFilter](#32-dictdisplayfilter)
   
   3.2 [ListDisplayFilter](#33-listdisplayfilter)
   
   3.4 [SQLDisplayFilter](#34-sqldisplayfilter)

4. [Query Language](#4-query-language)

   4.1 [Fields](#41-fields)
   
   4.2 [Comparing Values](#42-comparing-values)
   
   4.3 [Field Types](#43-field-types)
   
   4.4 [Combining Expressions](#44-combining-expressions)
   
   4.5 [Slice Operator](#45-slice-operator)
   
   4.6 [Membership Operator](#46-membership-operator)
   
   4.7 [Functions](#47-functions)

5. [Examples](#5-examples)

   5.1 [CSV Display Filter](#51-csv-display-filter)
 
   5.2 [JSON Display Filter](#52-json-display-filter)
 
   5.3 [Nmap Display Filter](#53-nmap-display-filter)

   5.4 [SQLite Display Filter](#54-sqlite-display-filter)

6. [Acknowledgements](#6-acknowledgements)

## 1. Introduction

The Python Display Filter Query Language allows filtering data using a Wireshark-like 
query language. It provides a flexible and efficient way to extract specific information from various data 
formats, including dictionaries, objects, lists, and SQL databases.

In this user guide, we will explore the installation process, provide an overview of how to work with various data 
formats, give a detailed explanation of the query language, and provide practical examples to demonstrate real-world 
usage.

By the end of this guide, you will have a comprehensive understanding of the 
Python Display Filter Query Language and be equipped to effectively filter and extract the data you need 
from diverse sources.

## 2. Installation

To install ```pydfql``, you can use the pip package manager. 
Open your terminal or command prompt and run the following command:
```commandline
pip3 install pydfql
```

Now that you have installed ```pydfql```, 
let's move on to the next section and explore how to quickly get started with it.

## 3. Usage

The ```pydfql``` library provides support for filtering data from various sources.
This section will provide an overview of how ```pydfql``` can be used for different data sources.


### 3.1 ObjectDisplayFilter
The ```ObjectDisplayFilter``` enables filtering a list of objects.

**Example:**

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

filter_query = "age.born > 1960"
filtered_data = ObjectDisplayFilter(actors).filter(filter_query)
print(list(filtered_data))
```

### 3.2 DictDisplayFilter
The ```DictDisplayFilter``` allows to filter a list of dictionaries. 

**Example:**

```python
from pydfql import DictDisplayFilter

actors = [
   {"name": ["Laurence", "Fishburne"], "age": {"born": "1961"}, "gender": "male"},
   {"name": ["Keanu", "Reeves"], "age": {"born": "1964"}, "gender": "male", "power": ["flight", "bullet-time"]},
   {"name": ["Joe", "Pantoliano"], "age": {"born": "1951"}, "gender": "male"},
   {"name": ["Carrie-Anne", "Moss"], "age": {"born": "1967"}, "gender": "female"}
]

filter_query = "age.born > 1960 and age.born < 1965"
filtered_data = DictDisplayFilter(actors).filter(filter_query)
print(list(filtered_data))
```

### 3.3 ListDisplayFilter

The ```ListDisplayFilter``` allows filtering a list of lists. 

**Example:**

```python
from pydfql import ListDisplayFilter

data = [
   ["Morpheus", "Laurence Fishburne", 38, "male", False],
   ["Neo", "Keanu Reeves", 35, "male", False],
   ["Cipher", "Joe Pantoliano", 48, "male", True],
   ["Trinity", "Carrie-Anne Moss", 32, "female", False]
]

filter_query = "age < 40"
field_names = ["name", "actor", "age", "gender", "killed"]
filtered_data = ListDisplayFilter(data).filter(filter_query)
print(filtered_data)
```

### 3.4 SQLDisplayFilter

The ```SQLDisplayFilter``` allows filtering a SQL database table. 

**Example:**

```python
from pydfql import SQLDisplayFilter
import sqlite3

database_file = './data/sqlite_example.sqlite'
connection = sqlite3.connect(database_file)
table_name = "Actors"
filter_query = "age > 30"

filtered_data = SQLDisplayFilter(connection, table_name).filter(filter_query)
print(filtered_data)
```

## 4. Query Language

The query language provides a wide range of operations, comparisons, and 
logical operators to help retrieving the desired subset of data. 
This section introduces the query language and its components, including fields, comparisons, field types, 
combining expressions, slice operator, membership operator, and functions. 
Through examples and explanations, you will learn how to construct effective filter queries to extract the
desired data.


### 4.1 Fields

The simplest display filter is one that displays only items where a specific field is present in the dataset:
```
name
```

This works also for nested fields, whereby keys are joined by a dot (.):
```
age.born
```

### 4.2 Comparing Values

You can build display filters that compare values using a number of different comparison operators.
A complete list of available comparison operators is shown in the following table:

| English  | C-like | Description                                          | Example          |
|----------|---------|------------------------------------------------------|-----------------|
| eq       | ==      | Equal                                                | name == Neo     |
| ne       | !=      | Not equal                                            | name != Neo     |
| gt       | \>      | Greater than                                         | age > 10        |
| lt       | <       | Less than                                            | age < 128       |
| ge       | \>=     | Greater than or equal to                             | age <= 128      |
| le       | <=      | Less than or equal to                                | age <= 128      |
| contains | ~=      | field contains a value                               | age contains 3  |
| matches  | ~       | field matches a Perl-compatible regular expression   | name matches 3  |
|          | &       | Bitwise AND is non-zero                              | age & 0x20      | 

### 4.3 Field Types

#### Numbers

You can express integers in decimal, octal, or hexadecimal. The following display filters are equivalent:
```
age.born == 32
```
```
age.born == 0x02
```
```
age.born == 040
```

#### Text string

Strings are a sequence of characters. Characters can also be specified using a byte escape sequence using hex \xhh.
String comparison can be done using the ```==```, ```!=```, ```contains``` and ```matches```-operator:
```
name == Neo and name == \x4e\x65\x6f
```
```
name contains e
```
```
name matches *.e$
```

When using strings containing special characters like brackets and spaces they should be enclosed by single- or double-quotes:
```
name == "(Neo)"
name == 'Trin ity'
```

#### Ethernet address

Ethernet addresses are 6 bytes separated by a colon (:), dot (.), or dash (-) with one or two bytes between separators:
```
eth.dst == ff:ff:ff:ff:ff:ff
```
```
eth.dst == ff-ff-ff-ff-ff-ff
```
```
eth.dst == ffff.ffff.ffff
```

#### IPv4 address

IPv4 addresses are octets separated by a dot (.). In addition, IPv4 address ranges can be specified using a nmap like 
notation:
```
ip.addr in { 192.168.0.1/24 }
```
```
ip.addr in { 192.168.0.1-254 }
```
```
ip.addr in { 192.168.0.1,2,3 }
```

For more information regarding the nmap like IPv4 address notation see the <a href="https://github.com/bytebutcher/ipranger">IPRanger documentation</a>.

#### IPv6 address

IPv6 addresses are hexadecimal parts separated by colons (:). Both compact- and expressive IPv6 notations are supported:
```
ipv6 == 2001:0db8:0000:08d3:0000:8a2e:0070:7344 and ipv6 == 2001:db8:0:8d3:0:8a2e:70:7344
```
```
ipv6 == 2001:db8:0:0:0:0:1428:57ab and ipv6 == 2001:db8::1428:57ab
```

#### Date and time

The value of a date- or time-field is expressed as a string. You can find some examples below: 
```
published > 2000
```
```
published < 2000
```
```
published <= 2003/05/11
```
```
published <= 2003-05-11
```

See the <a href="https://dateutil.readthedocs.io/en/stable/">python-dateutil documentation</a> for more information.

### 4.4 Combining Expressions

Expressions can be combined using the following logical operators:

| English   | C-like       | Description | Example                                 |
|-----------|--------------|-------------|-----------------------------------------|
| and       | &&           | Logical AND | ```age >= 32 and gender == male```      |
| or        | &#124;&#124; | Logical OR  | ```name == Neo or name == Trinity```    |
| xor       | ^^           | Logical XOR | ```gender == female xor power```        |
| not       | !            | Logical NOT | ```gender == male and not (age > 35)``` |

### 4.5 Slice Operator

The values of fields can be sliced similar to Pythons slice operator. This can be done by placing a pair of brackets [] 
containing a comma separated list of range specifiers.

The following example uses the ```n:m``` format to specify a single range. In this case n is the beginning offset and m is 
the length of the range being specified:
```
name[0:2] == Ne
```

The example below uses the ```n-m``` format to specify a single range. In this case n is the beginning offset and m is the 
ending offset:
```
name[1-2] == Ne
```

The example below uses the ```:m``` format, which takes everything from the beginning of a sequence to offset m. 
It is equivalent to ```0:m```:
```
name[:2] == Ne
```

The example below uses the ```n:``` format, which takes everything from offset n to the end of the sequence:
```
name[2:] == o
```

The example below uses the ```n``` format to specify a single range. In this case the element in the sequence at offset
n is selected. This is equivalent to ```n:1```:
```
name[0] == N
name[-1] == o
```

It is also possible to string together single ranges in a comma separated list to form compound ranges as shown below:
```
name[:1,2-3] == Neo
```

The slice operator is content aware and currently recognizes ```Strings```, ```IPv4-```, ```IPv6-```, and 
```Ethernet-Addresses```. The examples below show their usage:

#### Ethernet Slicing
```
mac[0] == 00
mac[:2] == 00:83
mac[1-2] == 00:83
mac[1-2,1-2] == 00:83:00:83
```
#### IPv4 Address Slicing
```
ipv4[0] == 127
ipv4[0:2] == 127.0
ipv4[:2] == 127.0
ipv4[1-2] == 127.0
ipv4[0,1] == 127.0
ipv4[1-2,1-2] == 127.0.127.0
```
#### IPv6 Address Slicing
```
ipv6[0] == 2001
ipv6[0:2] == 2001:0db8
ipv6[:2] == 2001:0db8
ipv6[1-2] == 2001:0db8
ipv6[0,1] == 2001:0db8
ipv6[1-2,1-2] == 2001:0db8:2001:0db8
```

### 4.6 Membership Operator

Expressions can be used to test a field for membership in a set of values or fields. 
After the field name, use the ```in```-operator followed by the set items surrounded by braces (```{}```). 
For example, to display packets with a TCP source or destination port of 80, 443, or 8080, 
you can use ```tcp.port in {80, 443, 8080}```. Set elements must be separated by commas. 
The set of values can also contain ranges e.g. ```tcp.port in {443,4430..4434}```.

Sets are not just limited to numbers, other types can be used as well:
```
http.request.method in {"HEAD", "GET"}
tcp.port in {443, 4430..4434}
ip.addr in { 10.2.2.2/24 }
```

### 4.7 Functions

The display filter language has a number of functions to convert fields:

|  Function | Description                           | Example                  | 
|-----------|---------------------------------------|--------------------------|
| upper     | Converts a string field to uppercase. | ```upper(name) == NEO``` | 
| lower     | Converts a string field to lowercase. | ```lower(name) == neo``` |
| len       | Returns the length of a string.       | ```len(name) == 3```     |


## 5. Examples

In this section, we will walk through various examples to demonstrate the practical usage of the 
```pydfql```.

### 5.1 CSV Display Filter

This example shows how to use the display filter to query CSV-files:
```commandline
python3 examples/csv_display_filter.py data/example.csv
# Enter ?help for a list of commands.
```
```
> fields
name
actor
age
gender
killed
```
```
> filter name == Neo

name | age | gender | killed
---- | --- | ------ | ------
Neo  | 35  | male   | False 

1 row in set (0.01 secs)
```

See <a href="https://github.com/bytebutcher/pydfql/raw/main/examples/csv_display_filter.py">examples/csv_display_filter.py</a> for implementation details.


### 5.2 JSON Display Filter

This example shows how to use the display filter to query JSON files:
```commandline
python3 examples/json_display_filter.py data/example.json
# Enter ?help for a list of commands.
```
```
> fields
gender
name
power
actor
age.born
```
```
> filter name == Neo
{"name": "Neo", "actor": ["Keanu", "Reeves"], "age": {"born": "1964"}, "gender": "male", "power": ["flight", "bullet-time"]}

1 row in set (0.01 secs)
```

See <a href="https://github.com/bytebutcher/pydfql/raw/main/examples/json_display_filter.py">examples/json_display_filter.py</a> for implementation details.

### 5.3 Nmap Display Filter

This example shows how to use a display filter to query Nmap XML files:
```commandline
python3 examples/nmap_display_filter.py data/nmap_example.xml
# Enter ?help for a list of commands.
```
```
> fields
host
port
protocol
status
service
```
```
> filter port == 179

host         | port | protocol | status | service
------------ | ---- | -------- | ------ | -------
72.14.207.99 | 179  | tcp      | closed | bgp    
72.14.253.83 | 179  | tcp      | closed | bgp    

2 rows in set (0.01 secs)
```
```
> filter lower(service) ~= apache

host           | port | protocol | status | service                                                                                                                                   
-------------- | ---- | -------- | ------ | ------------------------------------------------------------------------------------------------------------------------------------------
66.35.250.168  | 80   | tcp      | open   | product: Apache httpd version: 1.3.39 extrainfo: (Unix) PHP/4.4.7                                                                         
64.13.134.48   | 80   | tcp      | open   | product: Apache httpd version: 2.2.2 extrainfo: (Fedora)                                                                                  
204.152.191.37 | 80   | tcp      | open   | product: Apache httpd version: 2.2.2 extrainfo: (Fedora)                                                                                  
199.185.137.3  | 80   | tcp      | open   | product: Apache httpd                                                                                                                     
204.152.190.12 | 80   | tcp      | open   | product: Apache httpd version: 2.0.61 extrainfo: (Unix) mod_ssl/2.0.61  DAV/2 mod_fastcgi/2.4.2 mod_apreq2-20051231/2.6.0                 
204.152.190.12 | 443  | tcp      | open   | product: Apache httpd version: 2.0.61 extrainfo: mod_ssl/2.0.61  DAV/2 mod_fastcgi/2.4.2 mod_apreq2-20051231/2.6.0 hostname: rt.NetBSD.org

6 rows in set (0.01 secs)
```

See <a href="https://github.com/bytebutcher/pydfql/raw/main/examples/nmap_display_filter.py">examples/nmap_display_filter.py</a> for implementation details.

### 5.4 SQLite Display Filter

This example shows how to use the display filter to query a SQLite database:
```commandline
python3 examples/sqlite_display_filter.py data/example.sqlite
# Enter ?help for a list of commands.
```
```
> tables
Actors
```
```
> use Actors
Database changed
```
```
> fields
name
actor
age
gender
killed
```

```
> filter name == Neo

name | actor        | age | gender | killed
---- | ------------ | --- | ------ | ------
Neo  | Keanu Reeves | 35  | male   | 0 

1 row in set (0.01 secs)
```

See <a href="https://github.com/bytebutcher/pydfql/raw/main/examples/sqlite_display_filter.py">examples/sqlite_display_filter.py</a> for implementation details.


## 6. Acknowledgements

This project wouldn't be possible without these awesome projects:

* <a href="https://wiki.wireshark.org/DisplayFilters">wireshark display filter</a>: Display filter for filtering network packages
* <a href="https://github.com/wolever/parameterized">parameterized</a>: Parameterized testing with any Python test framework
* <a href="https://github.com/pyparsing/pyparsing/">pyparsing</a>: Creating PEG-parsers made easy
* <a href="https://github.com/bytebutcher/ipranger/">ipranger</a>: Parsing and matching IPv4-addresses
* <a href="https://pypi.org/project/python-dateutil/">python-dateutil</a>: Parsing and comparing dates 
