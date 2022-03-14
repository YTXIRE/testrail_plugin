from testrail_api import TestRailAPI
from logging import error, basicConfig

basicConfig(format='TESTRAIL: %(levelname)s - %(message)s')


def get_status(testrail: TestRailAPI, case_id: int, test_run_id: int) -> int:
    """
    Getting the status ID by the request ID and test run

    :param testrail: Instance of the testrail api class
    :param case_id: ID test case in TestRail
    :param test_run_id: ID test run in TestRail
    :return: Status ID
    """
    try:
        if case_id <= 0 or test_run_id <= 0:
            raise error('The test case ID or test run ID is not valid')
        case = testrail.results.get_results_for_case(
            run_id=int(test_run_id),
            case_id=int(case_id),
            limit=1
        )
        if len(case) == 0:
            return 0
        return case[0]['status_id']
    except Exception:
        pass
