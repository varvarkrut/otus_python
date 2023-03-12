import os
from hw1.log_analyzer import make_report, save_report
import pytest


def test_report_making(create_log_file):
    log_file_path = 'log/nginx-access-ui.log-111111.log'
    report_size = 10
    report = make_report(log_file_path, report_size)
    assert len(report) == report_size
    assert report[0]['url'] == '/api/v2/banner/25020545'
    assert report[0]['count'] == 1
    assert report[0]['count_perc'] == 0.077
    assert report[0]['time_avg'] == 0.738
    assert report[0]['time_max'] == 0.738
    assert report[0]['time_sum'] == 0.738
    assert report[0]['time_perc'] == 18.313
    assert report[0]['time_med'] == 0.738


def test_report_making_with_empty_file(create_log_file):
    log_file_path = 'log/test.log'
    report_size = 10
    with open(log_file_path, 'w') as f:
        f.write('')
    report = make_report(log_file_path, report_size)
    assert len(report) == 0


def test_report_saving(create_log_file):
    report = [{'url': '/api/v2/banner/25020545', 'count': 1, 'count_perc': 0.077, 'time_avg': 0.738, 'time_max': 0.738,
               'time_sum': 0.738, 'time_perc': 18.313, 'time_med': 0.738}]
    report_path = 'report.html'
    save_report(report, report_path)
    file_path = os.path.join(os.getcwd(), report_path)
    assert os.path.exists(file_path)
    # delete report file
    os.remove(file_path)


@pytest.fixture
def create_log_file():

    with open('log/nginx-access-ui.log-111111.log', 'w') as f:
        f.write('1.196.116.32 -  - [29/Jun/2017:03:50:22 +0300] "GET /api/v2/banner/25019354 HTTP/1.1" 200 927 "-" "Lynx/2.8.8dev.9 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/2.10.5" "-" "1498697422-2190034393-4708-9752759" "dc7161be3" 0.390\n'
                '1.99.174.176 3b81f63526fa8  - [29/Jun/2017:03:50:22 +0300] "GET /api/1/photogenic_banners/list/?server_name=WIN7RB4 HTTP/1.1" 200 12 "-" "Python-urllib/2.7" "-" "1498697422-32900793-4708-9752770" "-" 0.133\n'
                '1.169.137.128 -  - [29/Jun/2017:03:50:22 +0300] "GET /api/v2/banner/16852664 HTTP/1.1" 200 19415 "-" "Slotovod" "-" "1498697422-2118016444-4708-9752769" "712e90144abee9" 0.199\n'
                '1.199.4.96 -  - [29/Jun/2017:03:50:22 +0300] "GET /api/v2/slot/4705/groups HTTP/1.1" 200 2613 "-" "Lynx/2.8.8dev.9 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/2.10.5" "-" "1498697422-3800516057-4708-9752745" "2a828197ae235b0b3cb" 0.704\n'
                '1.168.65.96 -  - [29/Jun/2017:03:50:22 +0300] "GET /api/v2/internal/banner/24294027/info HTTP/1.1" 200 407 "-" "-" "-" "1498697422-2539198130-4709-9928846" "89f7f1be37d" 0.146\n'
                '1.169.137.128 -  - [29/Jun/2017:03:50:22 +0300] "GET /api/v2/group/1769230/banners HTTP/1.1" 200 1020 "-" "Configovod" "-" "1498697422-2118016444-4708-9752747" "712e90144abee9" 0.628\n'
                '1.194.135.240 -  - [29/Jun/2017:03:50:22 +0300] "GET /api/v2/group/7786679/statistic/sites/?date_type=day&date_from=2017-06-28&date_to=2017-06-28 HTTP/1.1" 200 22 "-" "python-requests/2.13.0" "-" "1498697422-3979856266-4708-9752772" "8a7741a54297568b" 0.067\n'
                '1.169.137.128 -  - [29/Jun/2017:03:50:22 +0300] "GET /api/v2/banner/1717161 HTTP/1.1" 200 2116 "-" "Slotovod" "-" "1498697422-2118016444-4708-9752771" "712e90144abee9" 0.138\n'
                '1.166.85.48 -  - [29/Jun/2017:03:50:22 +0300] "GET /export/appinstall_raw/2017-06-29/ HTTP/1.0" 200 28358 "-" "Mozilla/5.0 (Windows; U; Windows NT 6.0; ru; rv:1.9.0.12) Gecko/2009070611 Firefox/3.0.12 (.NET CLR 3.5.30729)" "-" "-" "-" 0.003\n'
                '1.199.4.96 -  - [29/Jun/2017:03:50:22 +0300] "GET /api/v2/slot/4822/groups HTTP/1.1" 200 22 "-" "Lynx/2.8.8dev.9 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/2.10.5" "-" "1498697422-3800516057-4708-9752773" "2a828197ae235b0b3cb" 0.157\n'
                '1.196.116.32 -  - [29/Jun/2017:03:50:22 +0300] "GET /api/v2/banner/24987703 HTTP/1.1" 200 883 "-" "Lynx/2.8.8dev.9 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/2.10.5" "-" "1498697422-2190034393-4708-9752753" "dc7161be3" 0.726\n'
                '1.166.85.48 -  - [29/Jun/2017:03:50:22 +0300] "GET /export/appinstall_raw/2017-06-30/ HTTP/1.0" 404 162 "-" "Mozilla/5.0 (Windows; U; Windows NT 6.0; ru; rv:1.9.0.12) Gecko/2009070611 Firefox/3.0.12 (.NET CLR 3.5.30729)" "-" "-" "-" 0.001\n'
                '1.196.116.32 -  - [29/Jun/2017:03:50:22 +0300] "GET /api/v2/banner/25020545 HTTP/1.1" 200 969 "-" "Lynx/2.8.8dev.9 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/2.10.5" "-" "1498697422-2190034393-4708-9752761" "dc7161be3" 0.738\n'
                '1.169.137.128 -  - [29/Jun/2017:03:50:23 +0300] "GET /api/v2/banner/7763463 HTTP/1.1" 200 1018 "-" "Configovod" "-" "1498697422-2118016444-4708-9752774" "712e90144abee9" 0.181\n'
                '1.169.137.128 -  - [29/Jun/2017:03:50:23 +0300] "GET /api/v2/banner/16168711 HTTP/1.1" 200 16478 "-" "Slotovod" "-" "1498697422-2118016444-4708-9752775" "712e90144abee9" 0.190\n')