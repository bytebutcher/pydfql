<p align="center">
    <img src="https://github.com/bytebutcher/python-dict-display-filter/raw/main/images/python_dict_display_filter_logo.png" alt="python_dict_display_filter Logo"/>
</p>
<h1 align="center" style="margin-top: 0px;">Python Dictionary Display Filter</br>Developer Guide</h1>
<br>

## Customizing Display Filters

The display filter can be customized to your needs. The constructor of the ```BaseDisplayFilter``` accepts following
parameters:

| Parameter         | Description                                                                                                                                                                                                                                                                                                  |
|-------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| ```data```        | A list of dictionaries to filter on.                                                                                                                                                                                                                                                                         |  
| ```field_names``` | A list of field names which are allowed in the display filter. If no field names are given there are no restrictions regarding specifying field names in the display filter query.<br/> However, in some cases it may make sense to allow only a set of ```field names``` to be queried and disallow others. |  
| ```functions```   | A dictionary of functions whereby the key specifies the name of the function. If no functions are supplied "len", "lower" and "upper" are used as default ones. <br/>If you don't require functions you may provide an empty dictionary.                                                                     | 
| ```slicers```     | A list of slicers. If no slicers are supplied the BasicSlicer is used per default. If you require additional slicers you can provide your own list here.                                                                                                                                                     | 
| ```evaluator```   | A evaluator which does the evaluation of the expressions. If no evaluator is defined the ```DefaultEvaluator``` is used which supports all kind of types.<br/> If you want to down-trim or extend evaluation you can provide a custom evaluator here.                                                        | 

## Exceptions

The ```python-dict-display-filter``` defines some custom exceptions which may be thrown during runtime:

| Exception              | Description                                                                                                                                                                                   |
|------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| ```ParserError```      | This error indicates that there was an error during parsing the display filter which usually happens when the user input (aka the display filter) is not correctly specified.                 |
| ```EvaluationError```  | This error indicates that there was an error during evaluating an expression which usually happens when some illegal operations are performed (e.g. 'lower(int)' -> only works with strings). |
| ```ProgrammingError``` | This error indicates an internal error likely due to some programming error. If this error is thrown please open a ticket.                                                                    |

## Helpers

The ```python-dict-display-filter``` defines a set of helpers which may be used in standalone applications:

| Helper Class                 | Description                                                                                                                     |
|------------------------------|---------------------------------------------------------------------------------------------------------------------------------|
| ```DisplayFilterShell```     | A command line loop which allows to filter data on a provided data store. Uses Table to print the result in a pretty table.     |
| ```DictDisplayFilterShell``` | A command line loop which allows to filter data on a provided data store. Uses DictTable to print the result in a pretty table. |
| ```Table```                  | Initialized with a data store, provides a filter method, prints results in a pretty table.                                      | 
| ```DictTable```              | Initialized with a data store, provides a filter method, prints results in a pretty table.                                      | 
