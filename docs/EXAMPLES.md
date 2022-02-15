<p align="center">
    <img src="https://github.com/bytebutcher/python-dict-display-filter/raw/main/images/python_dict_display_filter_logo.png" alt="python_dict_display_filter Logo"/>
</p>
<h1 align="center" style="margin-top: 0px;">Python Dictionary Display Filter</h1>
<h1 align="center" style="margin-top: 0px;">Examples</h1>
<br>

## CSV Display Filter

This example shows how easy it is to create a display filter for CSV-files:
```commandline
python3 examples/csv_display_filter.py data/example.csv
# Enter ?help for a list of commands.
```
```
> fields
name
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

See <a href="https://github.com/bytebutcher/python-dict-display-filter/raw/main/examples/csv_display_filter.py">examples/csv_display_filter.py</a> for the actual source code.

## Nmap Display Filter

This example shows how easy it is to create a display filter for nmap-xml-files:
```commandline
python3 examples/nmap_display_filter.py -iC data/nmap_example.xml
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

See <a href="https://github.com/bytebutcher/python-dict-display-filter/raw/main/examples/nmap_display_filter.py">examples/nmap_display_filter.py</a> for the actual source code.
