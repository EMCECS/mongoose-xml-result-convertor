import sys
import os
import csv
import json
import time
from datetime import datetime


def build_xml(row, step_id, file_size):
    result = "<result id=\"" + step_id + "\""
    dt_iso = row['DateTimeISO8601']
    start_dt = datetime.strptime(dt_iso, '%Y-%m-%dT%H:%M:%S,%f')
    start_timestamp = time.mktime(start_dt.timetuple())
    step_dur = float(row['StepDuration[s]'])
    end_timestamp = start_timestamp + step_dur
    end_dt = datetime.fromtimestamp(end_timestamp)
    result += " StartDate=\"" + str(start_dt.date()) + ' ' + str(start_dt.time()) + "\""
    result += " StartTimestamp=\"" + str(start_timestamp) + "\""
    result += " EndDate=\"" + str(end_dt.date()) + ' ' + str(end_dt.time()) + "\""
    result += " EndTimestamp=\"" + str(end_timestamp) + "\""
    result += " operation=\"" + row['OpType'] + "\""
    result += " threads=\"" + str(int(row['Concurrency']) * int(row['NodeCount'])) + "\""
    result += " RequestThreads=\"" + row['Concurrency'] + "\""
    result += " clients=\"" + row['NodeCount'] + "\""
    result += " error=\"" + row['CountFail'] + "\""
    result += " runtime=\"" + row['StepDuration[s]'] + "\""
    result += " filesize=\"" + file_size + "\""
    result += " tps=\"" + row['TPAvg[op/s]'] + "\""
    result += " tps_unit=\"" + "op/s" + "\""
    result += " bw=\"" + row['BWAvg[MB/s]'] + "\""
    result += " bw_unit=\"" + "MB/s" + "\""
    result += " latency=\"" + row['LatencyAvg[us]'] + "\""
    result += " latency_unit=\"" + "us" + "\""
    result += " latency_min=\"" + row['LatencyMin[us]'] + "\""
    result += " latency_loq=\"" + row['LatencyLoQ[us]'] + "\""
    result += " latency_med=\"" + row['LatencyMed[us]'] + "\""
    result += " latency_hiq=\"" + row['LatencyHiQ[us]'] + "\""
    result += " latency_max=\"" + row['LatencyMax[us]'] + "\""
    result += " duration=\"" + row['DurationAvg[us]'] + "\""
    result += " duration_unit=\"" + "us" + "\""
    result += " duration_min=\"" + row['DurationMin[us]'] + "\""
    result += " duration_loq=\"" + row['DurationLoQ[us]'] + "\""
    result += " duration_med=\"" + row['DurationMed[us]'] + "\""
    result += " duration_hiq=\"" + row['DurationHiQ[us]'] + "\""
    result += " duration_max=\"" + row['DurationMax[us]'] + "\""
    result += "/></result>"
    return result


if __name__ == "__main__":
    path = sys.argv[1]
    path_to_metric = path + "/metrics.total.csv"
    path_to_config = path + "/config.json"
    for p in [path, path_to_metric, path_to_config]:
        if not os.path.exists(p):
            print(path_to_metric + " doesn't exist")
            exit(1)
    step_id = path.split("/")[-1]
    config = json.load(open(path_to_config))
    file_size = config["item"]["data"]["size"]
    with open(path_to_metric) as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',')
        for row in reader:
            print build_xml(row, step_id, file_size)
