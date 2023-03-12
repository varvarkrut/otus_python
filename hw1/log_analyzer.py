import collections
import argparse
import gzip
import glob
import json
import math
import os
import re
import logging
from datetime import datetime

import pytest

CONFIG = {
    "REPORT_SIZE": 1000,
    "REPORT_DIR": "./reports",
    "LOG_DIR": "./log"
}
PATS = (r''
        r'^\S+\s\S+\s{2}\S+\s\[.*?\]\s'
        r'\"\S+\s(\S+)\s\S+\"\s'  # request_url
        r'\S+\s\S+\s.+?\s\".+?\"\s\S+\s\S+\s\S+\s'
        r'(\S+)'  # request_time
        )

PAT = re.compile(PATS)



def parse_args():
    parser = argparse.ArgumentParser(description='Log analyzer')
    parser.add_argument('--config', type=str, help='Path to config file')
    parser.add_argument('--log_path', type=str, help='Path to log file')
    return parser.parse_args()



def get_config(config_path=None):
    logging.info(f'Start getting config {config_path}')
    if config_path is None or (not os.path.exists(config_path)):
        return CONFIG
    with open(config_path) as f:
        config = json.load(f)
        resulted_config = CONFIG.copy()
        resulted_config.update(config)
    return config


def open_log_file(log_file):
    logging.info(f'Start opening log file {log_file}')
    if log_file.endswith('.gz'):
        return gzip.open(log_file, 'rt')
    return open(log_file, 'r')

def make_report(log_path, report_size):
    logging.info('Start making report')
    url_frequency = dict()
    counter = 0
    request_time_counter = 0
    url_characteristics = collections.defaultdict(list)
    median_dict = collections.defaultdict(list)
    parsing_error_counter = 0
    log_file = open_log_file(log_path)
    with log_file as f:
        logging.info('Start parsing log file')
        for line in f:
            try:
                parsed_line = parse_line(line)

                if parsed_line:
                    counter += 1
                    request_time_counter += parsed_line['request_time']

                    url_characteristic = url_characteristics.get(parsed_line['request_url'], {})
                    url_characteristic['count_perc'] = round_to_the_third(url_characteristic.get('count_perc', 0) + 1 / counter)
                    url_characteristic['count'] = url_characteristic.get('count', 0) + 1
                    url_characteristic['time_avg'] = round_to_the_third(url_characteristic.get('time_avg', 0) + parsed_line['request_time'])
                    url_characteristic['time_max'] = round_to_the_third(url_characteristic.get('time_max', 0))
                    url_characteristic['time_max'] = round_to_the_third(parsed_line['request_time'] if parsed_line['request_time'] > \
                                                                                    url_characteristic['time_max'] else \
                    url_characteristic['time_max'])
                    url_characteristic['time_sum'] = round_to_the_third(url_characteristic.get('time_sum', 0) + parsed_line['request_time'])
                    url_characteristic['total_time'] = round_to_the_third(url_characteristic.get('total_time', 0) + parsed_line[
                        'request_time'])
                    url_characteristic['time_characteristic'] = url_characteristic.get('time_characteristic', {})
                    url_characteristic['time_characteristic']['request_time'] = url_characteristic[
                                                                                    'time_characteristic'].get(
                        'request_time', 0) + parsed_line['request_time']
                    url_characteristic['time_perc'] = round_to_the_third((url_characteristic['time_sum'] / request_time_counter) * 100)
                    median_dict[parsed_line['request_url']].append(parsed_line['request_time'])
                    url_characteristic['time_med'] = median_dict[parsed_line['request_url']][
                        math.floor(len(median_dict[parsed_line['request_url']]) / 2)]

                    url_characteristics[parsed_line['request_url']] = url_characteristic
            except Exception as e:
                parsing_error_counter += 1
                print(f'Parsing error: {e}')
                continue

    if parsing_error_counter > counter/3:
        logging.error('Too many parsing errors')
        raise Exception('Too many parsing errors')


    logging.info('Start sorting report')
    report = []
    for url, url_characteristic in url_characteristics.items():
        url_characteristic['time_avg'] = round_to_the_third(url_characteristic['time_avg'] / url_characteristic['count'])
        report.append({'url': url, 'count': url_characteristic['count'], 'count_perc': url_characteristic['count_perc'],
                       'time_avg': url_characteristic['time_avg'], 'time_max': url_characteristic['time_max'],
                       'time_sum': url_characteristic['time_sum'], 'time_perc': url_characteristic['time_perc'],
                       'time_med': url_characteristic['time_med']})

    sorted_report = sorted(report, key=lambda x: x['time_sum'], reverse=True)
    return sorted_report[:report_size]


def round_to_the_third(number):
    return round(number, 3)


def get_latest_file(file_dir):
    files = glob.glob(file_dir + '/nginx-access-ui.log-*')
    if files:
        latest_file = max(files, key=get_file_date)
        return latest_file
    return None


def get_file_date(file_path):
    file_date = re.match(r'^.*-(\d+)\.?\w*$', file_path)
    if file_date:
        return datetime.strptime(file_date.group(1), '%Y%m%d')
    raise RuntimeError('Unexpected log file format')



def parse_line(line):
    g = PAT.match(line)
    if g:
        col_names = ('request_url', 'request_time')
        parsed_line = (dict(zip(col_names, g.groups())))
        parsed_line['request_time'] = float(parsed_line['request_time']) if parsed_line['request_time'] != '-' else 0
        return parsed_line
    return None


def save_report(report, file_path):
    logging.info(f'Start saving report to file {file_path}')
    with open('./reports/report.html', 'r') as f:
        file_data = f.read()
    file_data = file_data.replace('$table_json', json.dumps(report))
    with open(file_path, 'w') as f:
        f.write(file_data)


def main():
    config_path = None
    try:
        args = parse_args()
        config_path = args.config_path
        log_path = args.log_path
    except AttributeError as err:
        print ("there was no config passed or it was empty, so we will use the default one")

    log_path = "STDOUT"
    if log_path == "STDOUT":
        logging.basicConfig(level=logging.INFO, datefmt='%Y.%m.%d %H:%M:%S')
    else:
        logging.basicConfig(filename=log_path, level=logging.INFO, datefmt='%Y.%m.%d %H:%M:%S')
    logging.info("Starting the script")
    config = get_config(config_path)


    latest_log_file = get_latest_file(config['LOG_DIR'])
    if not latest_log_file:
        print('No log files found')
        exit(0)

    report_date = datetime.strftime(get_file_date(latest_log_file), '%Y.%m.%d')
    report_path = os.path.join(config['REPORT_DIR'], f'report-{report_date}.html')
    if os.path.exists(report_path):
        print('Report already exists, exiting ...')
        exit(0)

    report = make_report(latest_log_file, config['REPORT_SIZE'])

    if not report:
        print('No report data')
        exit(0)

    save_report(report, report_path)

    print('Report saved to', report_path)

if __name__ == '__main__':
    main()