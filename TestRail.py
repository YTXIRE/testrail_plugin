import os
import shutil
from os import getenv
from json import loads
from uuid import uuid4
from pytest import mark
from os.path import join
from pathlib import Path
from platform import system
from datetime import datetime
from typing import Optional, Any
from testrail_api import TestRailAPI
from dotenv import load_dotenv

from pkg import get_status, get_test_runs, create_comment, get_section, formatted_time

load_dotenv()


class TestRail:
    @staticmethod
    def id(*ids: str or list) -> mark:
        """
        Assigning an id to a label in pytest

        :param ids: ID of the test case in the testrail
        :return: The pytest label
        """
        return mark.testrail_ids(ids=ids)

    @staticmethod
    def suite(name: str) -> mark:
        """
        Assigning an suite to a label in pytest

        :param name: Suite of the test case in the testrail
        :return: The pytest label
        """
        return mark.testrail_suite(name=name)

    def _get_test_case_ids(self):
        test_case_ids = []
        tests = self._get_path({'is_tests': True, 'nested_path': 'tests'})
        for root, dirs, files in os.walk(tests, topdown=False):
            for name in files:
                if name.split('.')[-1] == 'pyc':
                    continue
                file = open(os.path.join(root, name), 'r', encoding='UTF-8')
                text = str(file.read())
                while text.find("@TestRail.id('") != -1:
                    start_with = text.find("@TestRail.id('") + 15
                    id = text[start_with::].split("')")[0]
                    if id != '' and len(id) > 2:
                        test_case_ids.append(int(id))
                    text = text[start_with::]
        return test_case_ids

    def _copy_files(self, source_folder, destination_folder):
        for file_name in os.listdir(source_folder):
            source = join(source_folder, file_name)
            destination = join(destination_folder, file_name)
            if os.path.isfile(source):
                shutil.copy(source, destination)

    def _get_allure_result(self):
        results = []
        testrail_ids = []
        folder_name = str(uuid4())
        os.mkdir(path=self._get_path({'is_tests': True, 'nested_path': folder_name}))
        self._copy_files(
            source_folder=self._get_path({'is_nested_path': False}),
            destination_folder=self._get_path({'is_tests': True, 'nested_path': folder_name})
        )
        files = self._get_path({'is_nested_path': False})
        for root, _, files in os.walk(files, topdown=False):
            for file in files:
                if 'result.json' in file:
                    with open(os.path.join(root, file), 'r', encoding='UTF-8') as f:
                        results.append(loads(f.read()))
        start = "testrail_ids(ids=('C"
        end = "',))"
        for value in results:
            if 'labels' in value.keys():
                for label in value['labels']:
                    if str(label['value']).startswith(start):
                        testrail_ids.append(label['value'][len(start):-len(end)])
        return {
            'results': results,
            'testrail_ids': testrail_ids,
            'temp_folder_name': folder_name,
            'temp_folder': self._get_path({'is_tests': True, 'nested_path': folder_name})
        }

    def _get_path(self, data):
        is_tests = data.get('is_tests', False)
        is_nested_path = data.get('is_nested_path', False)
        nested_path = data.get('nested_path', '/')
        files = join(Path(__file__).parent.parent.parent.parent, nested_path)
        if is_tests:
            return files
        else:
            if is_nested_path:
                return f'{join(Path(__file__).parent.parent.parent.parent, getenv("ALLURE_DIR"))}/{nested_path}'
            else:
                return f'{join(Path(__file__).parent.parent.parent.parent, getenv("ALLURE_DIR"))}'

    def _add_steps_in_file_test(self, steps: list, full_name: str):
        test_name = full_name.split('#')[-1]
        class_name = full_name.split('#')[0].split('.')[-1]
        file_name = full_name.split('#')[0].split('.')[-2]
        folder_path = full_name.split('#')[0].split('.')[-3]
        tests = self._get_path({'is_tests': True, 'nested_path': 'tests'})
        readed_files = []
        for root, dirs, files in os.walk(tests, topdown=False):
            for name in files:
                if name.split('.')[-1] == 'pyc':
                    continue
                file = open(os.path.join(root, name), 'r', encoding='UTF-8')
                text = str(file.read())
                file.close()
                if class_name in text and test_name in text:
                    readed_name = f'{folder_path}/{file_name}/{class_name}/{test_name}'
                    if readed_name in readed_files:
                        continue
                    readed_files.append(readed_name)
                    with open(f'{tests}/{folder_path}/{file_name}.py', 'r+', encoding='UTF-8') as file:
                        src = file.readlines()
                        file.seek(0)
                        for line in src:
                            test__name = str(line).split('def ')[1].split('(')[0] if test_name in line else ''
                            if line.find(test_name) != -1 and test_name == test__name:
                                file.write(f"{line}{''.join(steps)}")
                            else:
                                file.write(line)

    def _add_testrail_id_in_file_before_test(self, id: int, full_name: str):
        test_name = full_name.split('#')[-1]
        class_name = full_name.split('#')[0].split('.')[-1]
        file_name = full_name.split('#')[0].split('.')[-2]
        folder_path = full_name.split('#')[0].split('.')[-3]
        tests = self._get_path({'is_tests': True, 'nested_path': 'tests'})
        readed_files = []
        for root, dirs, files in os.walk(tests, topdown=False):
            for name in files:
                if name.split('.')[-1] == 'pyc':
                    continue
                file = open(os.path.join(root, name), 'r', encoding='UTF-8')
                text = str(file.read())
                file.close()
                if class_name in text and test_name in text:
                    readed_name = f'{folder_path}/{file_name}/{class_name}/{test_name}'
                    if readed_name in readed_files:
                        continue
                    readed_files.append(readed_name)
                    with open(f'{tests}/{folder_path}/{file_name}.py', 'r+', encoding='UTF-8') as file:
                        src = file.readlines()
                        file.seek(0)
                        for line in src:
                            test__name = str(line).split('def ')[1].split('(')[0] if test_name in line else ''
                            if line.find(test_name) != -1 and test_name == test__name:
                                file.write(f"    @TestRail.id('C{id}')\n{line}")
                            else:
                                file.write(line)

    def _get_test_cases_by_suite(self, tr: TestRailAPI, suite_id: int, section_id: int, case_name: str) -> dict:
        cases = tr.cases.get_cases(
            project_id=int(getenv('TESTRAIL_PROJECT_ID')),
            suite_id=suite_id,
            section_id=section_id
        )
        data = {
            'result': False,
            'data': {}
        }
        for case in cases:
            if 'title' not in case:
                return data
            if str(case['title']).lower() == case_name.lower():
                return {
                    'result': True,
                    'data': case
                }
        return data

    def _get_custom_result_field(self, tr: TestRailAPI) -> dict:
        fields_list = {}
        fields = tr.result_fields.get_result_fields()
        for field in fields:
            if str(field['system_name']).startswith('custom_'):
                fields_list[field['system_name']] = field['configs'][0]['options'][
                    'default_value'] if 'default_value' in field['configs'][0]['options'].keys() else ""
        return fields_list

    def _get_custom_case_field(self, tr: TestRailAPI) -> dict:
        fields_list = {}
        fields = tr.case_fields.get_case_fields()
        for field in fields:
            if str(field['system_name']).startswith('custom_'):
                fields_list[field['system_name']] = field['configs'][0]['options'][
                    'default_value'] if 'default_value' in field['configs'][0]['options'].keys() else ""
        return fields_list

    def _update_test_case_preconds(self, tr: TestRailAPI, case: dict, case_params: list):
        custom_steps = []
        if 'custom_preconds' not in dict(case).keys():
            return
        params = str(case['custom_preconds']).split('\n\n\n')[0]
        params_header = str(params).split('\n|||')[0]
        params_data = str(params).split('\n|||')[-1]
        custom_steps.append(params_header)
        custom_steps.append('\n|||')
        custom_steps.append(params_data)
        custom_steps.append(''.join(case_params[2::]))
        tr.cases.update_case(case_id=case['id'], custom_preconds=''.join(custom_steps))

    def _update_test_case_expected_result(self, tr: TestRailAPI, case_id: int, expected: list):
        case_info = tr.cases.get_case(case_id=case_id)
        for step in case_info['custom_steps_separated']:
            links_list = []
            for result in expected:
                if result['step_name'].lower() == step['content'].lower():
                    links_list.append(result['name'])
            if 'валидация ответа api' not in step['content'].lower():
                step['expected'] = ''.join(links_list)
        tr.cases.update_case(case_id=case_id, custom_steps_separated=case_info['custom_steps_separated'])

    def _create_test(self, tr: TestRailAPI, case_id: int, full_name: str):
        case_info = tr.cases.get_case(case_id=case_id)
        steps = []
        for item in case_info['custom_steps_separated']:
            steps.append(f'#\t\twith step("{item["content"]}"):\n#\t\t\tassert "{item["expected"]}"\n')
        self._add_steps_in_file_test(steps=steps, full_name=full_name)

    def _get_attachments_for_case(self, tr: TestRailAPI, case_id: int) -> dict:
        return tr.attachments.get_attachments_for_case(case_id=case_id)

    def _convert_attachments_list(self, attachments_list: list, upload_list: list):
        remastered_files_list = []
        for item in upload_list:
            for file in item:
                for attachment in attachments_list:
                    if file['name'].lower() == attachment['name'].lower():
                        remastered_files_list.append({
                            'name': f'[{attachment["name"]}](index.php?/attachments/get/{attachment["id"]})\n',
                            'step_name': file['top_step']
                        })
        return remastered_files_list

    def _create_test_case(self, tr: TestRailAPI, case_info: list, custom_fields: dict, folder: str):
        result = {
            'suite_name': None,
            'title': None,
            'description': None,
            'steps': [],
            'params': [],
            'precondition': [],
            'upload_files': [],
            'expected_files': [],
        }
        start = "testrail_suite(name=('"
        end = "',))"
        if 'labels' in dict(case_info).keys():
            for label in dict(case_info).get('labels'):
                if str(label['value']).startswith(start):
                    result['suite_name'] = label['value'][len(start):-len(end)]
        if result['suite_name'] is None:
            return
        suite_id = get_section(testrail=tr, name=result['suite_name'], project_id=int(getenv('TESTRAIL_PROJECT_ID')))
        if suite_id['id'] is None:
            return
        if 'name' not in dict(case_info).keys():
            return
        result['title'] = dict(case_info).get('name')
        if 'description' not in dict(case_info).keys():
            return
        result['description'] = dict(case_info).get('description')
        if 'parameters' in dict(case_info).keys():
            result['precondition'].append('**Параметры**:\n')
            result['precondition'].append('|||:Название|:Значение\n')
            for parametr in dict(case_info).get('parameters'):
                result['precondition'].append(f'|| {parametr["name"]} | {parametr["value"]}\n')
        if 'steps' not in dict(case_info).keys():
            return
        if len(dict(case_info).get('steps')) == 0:
            return
        # if 'steps' in dict(case_info).keys():
        #     result['steps'].append('\n\n**Шаги**:\n')
        for key, step in enumerate(dict(case_info).get('steps')):
            top_step = f'{step["name"]}\n'
            if 'steps' in dict(step).keys():
                internal_steps = []
                upload_files = []
                for k, s in enumerate(dict(step).get('steps')):
                    filename = f'{k + 1}. {str(s["name"]).replace("/", "_").replace("?", "_")}{uuid4()}.txt'
                    upload_files.append({
                        'top_step': top_step,
                        'name': filename,
                        'path': self._get_path({
                            'is_tests': True,
                            'nested_path': f'{folder}/{filename}'
                        })
                    })
                    if 'steps' in dict(s).keys():
                        for idx, value in enumerate(dict(s).get('steps')):
                            if 'attachments' in dict(value).keys():
                                for attachment in value["attachments"]:
                                    if 'request' == attachment['name']:
                                        with open(self._get_path({
                                            'is_tests': True,
                                            'nested_path': f'{folder}/{attachment["source"]}'
                                        })) as file:
                                            curl = file.read()
                                        internal_steps.append(
                                            f'{k + 1}. {s["name"]}\n - {value["name"]}\n\n\t{curl}\n\n'
                                        )
                                    if 'response' == attachment['name']:
                                        os.rename(
                                            self._get_path({
                                                'is_tests': True,
                                                'nested_path': f'{folder}/{attachment["source"]}'
                                            }),
                                            self._get_path({
                                                'is_tests': True,
                                                'nested_path': f'{folder}/{filename}'
                                            })
                                        )
                    else:
                        if 'attachments' in dict(s).keys():
                            for attachment in s["attachments"]:
                                if 'request' == attachment['name']:
                                    with open(self._get_path({
                                        'is_tests': True,
                                        'nested_path': f'{folder}/{attachment["source"]}'
                                    })) as file:
                                        curl = file.read()
                                    internal_steps.append(f'{k + 1}. {s["name"]}\n\n\t{curl}\n\n')
                                if 'response' == attachment['name']:
                                    os.rename(
                                        self._get_path({
                                            'is_tests': True,
                                            'nested_path': f'{folder}/{attachment["source"]}'
                                        }),
                                        self._get_path({
                                            'is_tests': True,
                                            'nested_path': f'{folder}/{filename}'
                                        })
                                    )
                result['steps'].append({
                    "content": top_step,
                    "additional_info": "".join(internal_steps),
                    "expected": "".join([f'{file["name"]}\n' for file in upload_files]),
                })
                result['upload_files'].append(upload_files)
            else:
                result['steps'].append({
                    "content": top_step,
                    "expected": 'Данный шаг только для автотестов' if 'валидация ответа api'
                                                                      in top_step.lower() else '',
                    "additional_info": ''
                })
        if 'fullName' not in dict(case_info).keys():
            return
        case = self._get_test_cases_by_suite(
            tr=tr,
            suite_id=suite_id['suite_id'],
            section_id=suite_id['id'],
            case_name=result['title']
        )
        if case['result']:
            self._update_test_case_preconds(tr=tr, case=case['data'], case_params=result['precondition'])
            return
        for field in dict(custom_fields).keys():
            if field == 'custom_description':
                custom_fields[field] = result['description']
            if field == 'custom_preconds':
                custom_fields[field] = ''.join(result['precondition'])
            if field == 'custom_steps_separated':
                custom_fields[field] = result['steps']
        created_case = tr.cases.add_case(
            section_id=suite_id['id'],
            title=result['title'],
            template_id=2,
            **custom_fields
        )
        for item in result['upload_files']:
            for file in item:
                tr.attachments.add_attachment_to_case(case_id=created_case["id"], path=file['path'])
        self._update_test_case_expected_result(
            tr=tr,
            case_id=created_case["id"],
            expected=self._convert_attachments_list(
                attachments_list=self._get_attachments_for_case(tr=tr, case_id=created_case["id"]),
                upload_list=result['upload_files']
            )
        )
        if 'fullName' in dict(case_info).keys():
            self.set_automation_status(
                tr=tr,
                case_id=created_case['id'],
                automated_type=int(getenv('TESTRAIL_AUTOMATED'))
            )
        self._add_testrail_id_in_file_before_test(id=created_case['id'], full_name=case_info['fullName'])

    def set_automation_status(self, tr: TestRailAPI, case_id: int, automated_type: int):
        if system().lower() in ['linux', 'darwin']:
            return
        case_info = tr.cases.get_case(case_id=case_id)
        if int(case_info['type_id']) != int(getenv('TESTRAIL_TYPE_AUTOMATED')):
            tr.cases.update_case(case_id=case_id, type_id=int(getenv('TESTRAIL_TYPE_AUTOMATED')))
        if case_info['custom_automated'] != int(getenv('TESTRAIL_AUTOMATED')) \
                and automated_type == int(getenv('TESTRAIL_AUTOMATED')):
            tr.cases.update_case(case_id=case_id, custom_automated=automated_type)

    def create_test_run(self, tr: TestRailAPI, testrail_ids=None) -> Optional[dict[int, Any]]:
        if testrail_ids is None:
            testrail_ids = []
        case_ids = []
        date = datetime.today().strftime('%d.%m.%Y')
        time = datetime.today().strftime('%H:%M:%S')
        name = f"{getenv('TESTRAIL_TITLE_RUN')} {date} {time}"
        ml = getenv('TESTRAIL_MILESTONE_ID')
        if not ml:
            raise ValueError('Milestone с указаным ID не найден')
        lasted_test_run = get_test_runs(
            testrail=tr,
            name=f"{getenv('TESTRAIL_TITLE_RUN')} {date}",
            project_id=int(getenv('TESTRAIL_PROJECT_ID'))
        )
        if lasted_test_run is not None:
            return lasted_test_run
        if int(getenv('ALLURE_FOR_TESTRAIL_ENABLED')) == 0:
            case_ids = self._get_test_case_ids()
        elif int(getenv('ALLURE_FOR_TESTRAIL_ENABLED')) == 1:
            case_ids = testrail_ids
        return tr.runs.add_run(
            project_id=int(getenv('TESTRAIL_PROJECT_ID')),
            name=name,
            milestone_id=ml,
            case_ids=case_ids,
            include_all=len(case_ids) == 0
        )['id']

    def close_test_run(self, tr: TestRailAPI, run_id: int):
        if tr.runs.get_run(run_id=run_id)['is_completed']:
            return
        tr.runs.close_run(run_id=run_id)

    def set_status(self, tr: TestRailAPI, data: dict):
        test_run_id = data['test_run_id']
        case_id = int(str(data['case_id'][1:]))
        if test_run_id is None:
            return
        if get_status(testrail=tr, case_id=case_id, test_run_id=test_run_id) == 5:
            print(f'Тест кейс с ID {data["case_id"]} уже находится в статусе Failed')
            return
        result = tr.results.add_result_for_case(
            run_id=int(test_run_id),
            case_id=int(case_id),
            status_id=int(data['status']),
            elapsed=data['elapsed'],
            comment=data['comment']
        )
        if data.get('screenshot') is not None:
            tr.attachments.add_attachment_to_result(result["id"], data['screenshot'])

    def set_statuses(self, tr, data):
        raw_data = self._get_allure_result()
        custom_case_fields = self._get_custom_case_field(tr=tr)
        custom_result_fields = self._get_custom_result_field(tr=tr)
        custom_browser = getenv('TESTRAIL_BROWSER')
        if custom_browser is not None:
            custom_browser = int(custom_browser)
        for field in custom_result_fields.keys():
            if field == 'custom_browser' and custom_browser is not None:
                custom_result_fields[field] = custom_browser
        if int(getenv("ALLURE_FOR_TESTRAIL_ENABLED")) == 1 and len(raw_data['testrail_ids']) > 0:
            data['test_run_id'] = self.create_test_run(tr=tr, testrail_ids=raw_data['testrail_ids'])
        for value in raw_data['results']:
            result = {
                'case_id': None,
                'case_name': '',
                'case_status': '',
                'case_description': '',
                'case_time': 0,
                'steps': [],
                'attachments': [],
                'upload_files': [],
                'params': [],
                'error': {
                    'message': '',
                    'trace': ''
                }
            }
            result['case_name'] = value['name'] if 'name' in value.keys() else ''
            result['case_status'] = value['status']
            result['case_description'] = value['description'] if 'description' in value.keys() else ''
            start = "testrail_ids(ids=('C"
            end = "',))"
            if result['case_status'].lower() == 'broken':
                continue
            step_data = {}
            if 'labels' in value.keys():
                for label in value['labels']:
                    if str(label['value']).startswith(start):
                        result['case_id'] = label['value'][len(start):-len(end)]
            if result['case_id'] is None:
                self._create_test_case(
                    tr=tr,
                    case_info=value,
                    custom_fields=custom_case_fields,
                    folder=raw_data["temp_folder_name"]
                )
                continue
            if 'steps' not in dict(value).keys() and 'description' not in dict(value).keys():
                self._create_test(tr=tr, case_id=result['case_id'], full_name=value['fullName'])
                continue
            if 'statusDetails' in value.keys():
                result['error']['message'] = value['statusDetails']['message']
                result['error']['trace'] = value['statusDetails']['trace']
            if 'parameters' in value.keys():
                result['params'].append('**Параметры**:\n')
                result['params'].append('|||:Название|:Значение\n')
                for parametr in value['parameters']:
                    result['params'].append(f'|| {parametr["name"]} | {parametr["value"]}\n')
            if 'steps' in value.keys():
                for step in value['steps']:
                    image = {
                        'img': None,
                        'name': ''
                    }
                    if 'parameters' in step.keys():
                        for param in step['parameters']:
                            if param['name'] == 'data' and param['value']:
                                step_data['data'] = param['value']
                            if param['name'] == 'expected_data' and param['value']:
                                step_data['expected_data'] = param['value']
                            if param['name'] == 'asserts_data' and param['value']:
                                step_data['asserts_data'] = param['value']
                    if 'attachments' in step.keys():
                        image['img'] = step["attachments"][0]["source"]
                    result['steps'].append({
                        'name': step['name'],
                        'status': step['status'],
                        'time': formatted_time((step['stop'] - step['start']) / 1000),
                        'data': step_data,
                        'image': image
                    })
                    result['case_time'] += (step['stop'] - step['start']) / 1000
            result['case_time'] = formatted_time(round(result['case_time'], 3))
            if 'attachments' in value.keys():
                for attachment in value['attachments']:
                    result['attachments'].append(attachment["source"])
            for key, val in enumerate(result['steps']):
                # if val['status'] == 'passed':
                #     continue
                if len(result['steps']) != key + 1:
                    continue
                if val['image']['img'] is None:
                    continue
                filename = f'Шаг_{key + 1}_{result["case_id"]}.png'
                os.rename(
                    self._get_path({
                        'is_tests': True,
                        'nested_path': f'{raw_data["temp_folder_name"]}/{val["image"]["img"]}'
                    }),
                    self._get_path({'is_tests': True, 'nested_path': f'{raw_data["temp_folder_name"]}/{filename}'})
                )
                result['steps'][key]['image']['name'] = filename
                result['upload_files'].append(
                    self._get_path({'is_tests': True, 'nested_path': f'{raw_data["temp_folder_name"]}/{filename}'}))
            with open(self._get_path({'is_nested_path': True, 'nested_path': 'mode.txt'}), 'r') as file:
                mode = file.read()
            case_status = True
            case_status_id_current = int(
                get_status(testrail=tr, case_id=int(result['case_id']), test_run_id=int(data['test_run_id'])))
            if case_status_id_current == int(getenv('TESTRAIL_FAILED_STATUS')) or result['case_status'] == 'failed':
                case_status = False
            result_case = tr.results.add_result_for_case(
                run_id=int(data['test_run_id']),
                case_id=int(result['case_id']),
                status_id=getenv('TESTRAIL_PASSED_STATUS') if case_status else getenv('TESTRAIL_FAILED_STATUS'),
                elapsed=result['case_time'],
                comment=create_comment(result, mode),
                **custom_result_fields
            )
            for file in result['upload_files']:
                tr.attachments.add_attachment_to_result(result_case["id"], file)
            if 'fullName' in value.keys():
                self.set_automation_status(
                    tr=tr,
                    case_id=result['case_id'],
                    automated_type=int(getenv('TESTRAIL_AUTOMATED'))
                )
        shutil.rmtree(raw_data['temp_folder'], ignore_errors=True)
        if int(getenv('TESTRAIL_AUTOCLOSE_TESTRUN')) == 1 and len(raw_data['testrail_ids']) > 0:
            self.close_test_run(tr=tr, run_id=data['test_run_id'])
