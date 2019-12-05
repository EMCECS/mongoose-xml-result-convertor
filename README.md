# mongoose-xml-result-convertor
The script allows to convert the mongoose logs to the xml format.

### Environemnt
* Python 3

### Usage

Go to the project root and run the script:
```
python xml-converter/xml-converter.py $HOME/.mongoose/<version>/log/<step_id>
```
To create a file, use output redirection:
```
python xml-converter/xml-converter.py $HOME/.mongoose/<version>/log/<step_id>  >  <filename>.xml
```
