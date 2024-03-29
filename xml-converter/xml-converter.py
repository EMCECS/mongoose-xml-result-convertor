# !/usr/bin/env python3

import csv, yaml
import time
import re
import os, argparse
from datetime import datetime


def set_and_get_options():
    parser = argparse.ArgumentParser(description='Automation test steps.')
    parser.add_argument('-p', '--pravega', action="store_true", help='generate pravega specific report')
    parser.add_argument('-l', '--logpath', action='store', help="path to mongoose log", required=True)
    parser.add_argument('--disable-quantiles', action="store_true", help="when disabled lat/dur quantiles are not printed in xml")
    return parser.parse_args()


def build_xml(row, step_id, config, disable_quantiles):
    file_size = config["item"]["data"]["size"]
    result = "<result id=\"" + step_id + "\""
    dt_iso = row['DateTimeISO8601']
    start_dt = datetime.strptime(dt_iso, '%Y-%m-%dT%H:%M:%S,%f')
    start_timestamp = time.mktime(start_dt.timetuple())
    step_dur = float(row['StepDuration[s]'])
    end_timestamp = start_timestamp + step_dur
    end_dt = datetime.fromtimestamp(end_timestamp)
    result += " StartDate=\"" + str(start_dt.date()) + ' ' + str(start_dt.time())[0:8] + "\""
    result += " StartTimestamp=\"" + str(start_timestamp) + "\""
    result += " EndDate=\"" + str(end_dt.date()) + ' ' + str(end_dt.time())[0:8] + "\""
    result += " EndTimestamp=\"" + str(end_timestamp) + "\""
    result += " operation=\"" + row['OpType'] + "\""
    result += " threads=\"" + str(int(row['Concurrency']) * int(row['NodeCount'])) + "\""
    result += " RequestThreads=\"" + row['Concurrency'] + "\""
    result += " clients=\"" + row['NodeCount'] + "\""
    result += " error=\"" + row['CountFail'] + "\""
    result += " runtime=\"" + str(round(float(row['StepDuration[s]']),4)) + "\""
    result += " filesize=\"" + file_size + "\""
    result += " tps=\"" + str(round(float(row['TPAvg[op/s]']),4)) + "\""
    result += " tps_unit=\"" + "op/s" + "\""
    result += " bw=\"" + str(round(float(row['BWAvg[MB/s]']),4)) + "\""
    result += " bw_unit=\"" + "MB/s" + "\""
    result += " latency=\"" + str(round(float(row['LatencyAvg[us]']),4)) + "\""
    result += " latency_unit=\"" + "us" + "\""
    result += " latency_min=\"" + row['LatencyMin[us]'] + "\""
    if not disable_quantiles:
        regex = re.compile('LatencyQ_\d.\d{,7}')
        latencyQuantiles = filter(regex.match, row.keys())  #find all latency quantiles entries in metrics.total
        for latencyQuantile in latencyQuantiles:
            #latencyQuantile[9:-4] - in string LatencyQ_0.5[us] we delete everything but the number
            result += " latency_" + latencyQuantile[9:-4] + "=\"" + row[latencyQuantile] + "\""

    result += " latency_max=\"" + row['LatencyMax[us]'] + "\""
    result += " duration=\"" + str(round(float(row['DurationAvg[us]']),2)) + "\""
    result += " duration_unit=\"" + "us" + "\""
    result += " duration_min=\"" + row['DurationMin[us]'] + "\""

    if not disable_quantiles:
        regex = re.compile('DurationQ_\d.\d{,7}')
        durationQuantiles = filter(regex.match, row.keys())
        for durationQuantile in durationQuantiles:
            #durationQuantile[10:-4] - in string DurationQ_0.5[us] we delete everything but the number
            result += " duration_" + durationQuantile[10:-4] + "=\"" + row[durationQuantile] + "\""

    result += " duration_max=\"" + row['DurationMax[us]'] + "\""
    result += "/>"
    return [ start_dt , result + "\n"]


def build_pravega_xml(row, step_id, config):
    try:
        file_size = config["item"]["data"]["size"]
        segment_size = config["storage"]["driver"]["scaling"]["segments"]
        producers = config["storage"]["driver"]["threads"]
        dt_iso = row['DateTimeISO8601']

    except KeyError as e:
        print(f"config.yaml for {step_id} is not pravega-driver specific. Don't use the key '-p'")
        print(f"KeyError: {e}")
        exit(1)
    start_dt = datetime.strptime(dt_iso, '%Y-%m-%dT%H:%M:%S,%f')
    result = "<result id=\"" + step_id + "\""
    result += " operation=\"" + row['OpType'] + "\""
    result += " pods=\"" + row['NodeCount'] + "\""
    result += " segment_size=\"" + str(segment_size) + "\""
    result += " producers=\"" + str(producers) + "\""
    result += " RequestThreads=\"" + row['Concurrency'] + "\""
    result += " clients=\"" + row['NodeCount'] + "\""
    result += " filesize=\"" + str(file_size) + "\""
    result += " tps=\"" + row['TPAvg[op/s]'] + "\""
    result += " tps_unit=\"" + "records/s" + "\""
    result += " bw=\"" + row['BWAvg[MB/s]'] + "\""
    result += " bw_unit=\"" + "MB/s" + "\""
    result += " latency_unit=\"" + "us" + "\""
    result += " avglatency=\"" + row['LatencyAvg[us]'] + "\""
    result += " minavglatency=\"" + row['LatencyMin[us]'] + "\""
    #result += " avg75latency=\"" + row['LatencyLoQ[us]'] + "\""
    #result += " avg50latency=\"" + row['LatencyMed[us]'] + "\""
    #result += " avg95latency=\"" + row['LatencyHiQ[us]'] + "\""
    result += " maxavglatency=\"" + row['LatencyMax[us]'] + "\""
    result += "/>"
    return [ start_dt , result + "\n"]


def check_log_dir(path):
    if os.path.isdir(path):
        if path.split("/")[-1].startswith("none-"):
            return False
        if not os.path.exists(path + "/metrics.total.csv"):
            return False
        if not os.path.exists(path + "/config.yaml"):
            return False
        return True
    return False


def get_step_ids(logpath):
    return [d for d in os.listdir(logpath) if check_log_dir(os.path.join(logpath, d))]


if __name__ == "__main__":
    args = set_and_get_options()
    logpath = args.logpath
    disable_quantiles = args.disable_quantiles
    step_ids = get_step_ids(logpath)
    result_dict = {}

    for step_id in step_ids:
        path_to_metric = f"{logpath}/{step_id}/metrics.total.csv"
        path_to_config = f"{logpath}/{step_id}/config.yaml"
        config = yaml.load(open(path_to_config, 'r'), Loader=yaml.FullLoader)

        with open(path_to_metric) as csvfile:
            reader = csv.DictReader(csvfile, delimiter=',')
            for row in reader:
                if args.pravega:
                    result = build_pravega_xml(row, step_id, config)
                else:
                    result = build_xml(row, step_id, config, disable_quantiles)
                result_dict[result[0]] = result[1]
    sorted_list = [v for k, v in sorted(result_dict.items(), key=lambda p: p[0], reverse=False)]
    new_result = "<result>"
    for i in range(0,len(sorted_list)):
        new_result += sorted_list[i]
    print(new_result + "</result>")
