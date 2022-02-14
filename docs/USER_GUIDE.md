<p align="center">
    <img src="https://github.com/bytebutcher/python-dict-display-filter/raw/main/images/python_dict_display_filter_logo.png" alt="python_dict_display_filter Logo"/>
</p>
<p align="center"><font size="5">Python Dictionary Display Filter</font></p>
<p align="center"><font size="5">User Guide</font></p>
<br>

## Display Filter Fields

The simplest display filter is one that displays only items where a specific field is present in the dataset:
```
name
```

This works also for nested fields, whereby keys are joined by a dot (.):
```
age.born
```

## Comparing Values

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

## Display Filter Field Types

### Numbers

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

### Text string

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

### Ethernet address

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

### IPv4 address

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

### IPv6 address

IPv6 addresses are hexadecimal parts separated by colons (:). Both compact- and expressive IPv6 notations are supported:
```
ipv6 == 2001:0db8:0000:08d3:0000:8a2e:0070:7344 and ipv6 == 2001:db8:0:8d3:0:8a2e:70:7344
```
```
ipv6 == 2001:db8:0:0:0:0:1428:57ab and ipv6 == 2001:db8::1428:57ab
```

### Date and time

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

## Combining Expressions

Expressions can be combined using the following logical operators:

| English   | C-like       | Description | Example                                 |
|-----------|--------------|-------------|-----------------------------------------|
| and       | &&           | Logical AND | ```age >= 32 and gender == male```      |
| or        | &#124;&#124; | Logical OR  | ```name == Neo or name == Trinity```    |
| xor       | ^^           | Logical XOR | ```gender == female xor power```        |
| not       | !            | Logical NOT | ```gender == male and not (age > 35)``` |

## Slice Operator

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

### Ethernet Slicing
```
mac[0] == 00
mac[:2] == 00:83
mac[1-2] == 00:83
mac[1-2,1-2] == 00:83:00:83
```
### IPv4 Address Slicing
```
ipv4[0] == 127
ipv4[0:2] == 127.0
ipv4[:2] == 127.0
ipv4[1-2] == 127.0
ipv4[0,1] == 127.0
ipv4[1-2,1-2] == 127.0.127.0
```
### IPv6 Address Slicing
```
ipv6[0] == 2001
ipv6[0:2] == 2001:0db8
ipv6[:2] == 2001:0db8
ipv6[1-2] == 2001:0db8
ipv6[0,1] == 2001:0db8
ipv6[1-2,1-2] == 2001:0db8:2001:0db8
```

## Membership Operator

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

## Functions

The display filter language has a number of functions to convert fields:

|  Function | Description                           | Example                  | 
|-----------|---------------------------------------|--------------------------|
| upper     | Converts a string field to uppercase. | ```upper(name) == NEO``` | 
| lower     | Converts a string field to lowercase. | ```lower(name) == neo``` |
| len       | Returns the length of a string.       | ```len(name) == 3```     |
