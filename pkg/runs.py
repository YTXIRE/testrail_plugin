from datetime import datetime

from testrail_api import TestRailAPI
from logging import error, basicConfig

basicConfig(format='TESTRAIL: %(levelname)s - %(message)s')


def get_test_runs(testrail: TestRailAPI, name: str, project_id: int) -> int or None:
    """
    Getting test run ID in TestRail

    :param testrail: Instance of the testrail api class
    :param name: Test run name
    :param project_id: Project ID
    :return: Test run ID
    """
    try:
        if project_id <= 0:
            raise error('The project ID is not valid')
        if name == '':
            raise error('The name is not be empty')
        for run in testrail.runs.get_runs(project_id=project_id, is_completed=False):
            if name in run['name']:
                return run['id']
        return None
    except Exception:
        pass


def create_test_run(testrail: TestRailAPI, milestone_id: int, testrail_ids: list, title_run_name: str, project_id) -> dict:
    try:
        if testrail_ids is None:
            testrail_ids = []
        case_ids = []
        date = datetime.today().strftime('%d.%m.%Y')
        time = datetime.today().strftime('%H:%M:%S')
        name = f"{title_run_name} {date} {time}"
        if milestone_id <= 0:
            raise error('Milestone with the specified ID was not found')
        lasted_test_run = get_test_runs(
            testrail=testrail,
            name=f"{title_run_name} {date}",
            project_id=project_id
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
    except Exception:
        pass
