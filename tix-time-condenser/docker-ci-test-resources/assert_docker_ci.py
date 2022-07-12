import json
import os

reports_volume_data_path = '/var/lib/docker/volumes/ReportsVolume/_data'

with open('docker-ci-test-resources/test-tix-report.json', 'r') as expected_report_file:
    expected_tix_report = json.load(expected_report_file)

users_dirs = os.listdir(reports_volume_data_path)
assert len(users_dirs) == 1
user_dir = users_dirs[0]
user_dir_path = os.path.join(reports_volume_data_path, user_dir)
installations_dirs = os.listdir(user_dir_path)
assert len(installations_dirs) == 1
installation_dir = installations_dirs[0]
installation_dir_path = os.path.join(user_dir_path, installation_dir)
reports = os.listdir(installation_dir_path)
assert len(reports) == 1
report = reports[0]
report_path = os.path.join(installation_dir_path, report)
with open(report_path, 'r') as report_file:
    tix_report = json.load(report_file)
assert tix_report == expected_tix_report
