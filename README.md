# mongoose-xml-result-convertor
The script allows to convert the mongoose logs to the xml format.

### Environemnt
* Python 3

### Usage

Go to the project root and run the script:
```
python xml-converter/xml-converter.py -l $HOME/.mongoose/<version>/log
```
To create a file, use output redirection:
```
python xml-converter/xml-converter.py -l $HOME/.mongoose/<version>/log  >  <filename>.xml
```

[Pravega](https://github.com/emc-mongoose/mongoose-storage-driver-pravega) specific output:
```
python xml-converter/xml-converter.py -l $HOME/.mongoose/<version>/log -p
```

### Output format

1. Tag `id` == mongoose `load-step-id`
2. Each line `<result id= ... />` == test summary of 1 Load step.
3. Each Load step is located in a separate directory `.../log/<load_step_id>`. The script combines all Load step summary into a single Result XML report.

## Default
```
<result>
<result id="linear_20200129.050404.509" StartDate="2020-01-29 05:04:25.820000" StartTimestamp="1580263465.0" EndDate="2020-01-29 05:04:45.409000" EndTimestamp="1580263485.409" operation="CREATE" threads="1" RequestThreads="1" clients="1" error="0" runtime="20.409" filesize="1MB" tps="75002.65" tps_unit="op/s" bw="7.86459787264E10" bw_unit="MB/s" latency="5.619490511403867" latency_unit="us" latency_min="2" latency_loq="2" latency_med="3" latency_hiq="3" latency_max="146521" duration="22.971041051315144" duration_unit="us" duration_min="8" duration_loq="10" duration_med="11" duration_hiq="13" duration_max="210329"/>
<result id="linear_20200123.211156.039" .../>
...
</result>
```

## Pravega specific
```
<result>
<result id="linear_20200123.211340.379" operation="READ" pods="1" segment_size="1" producers="1" RequestThreads="0" clients="1" filesize="1B" tps="141238.17142857143" tps_unit="records/s" bw="141238.17142857143" bw_unit="MB/s" avglatency="3.9725487097832826" latency_unit="us" minavglatency="2" latency_loq="3" avg50latency="3" latency_hiq="3" maxavglatency="73170"/>
<result id="linear_20200123.211156.031" operation="READ" .../>
...
</result>
```
