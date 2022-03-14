from testrail_api import TestRailAPI
from logging import error, basicConfig

basicConfig(format='TESTRAIL: %(levelname)s - %(message)s')


def get_section(testrail: TestRailAPI, name: str, project_id: int) -> dict:
    """
    Getting a section with test cases

    :param testrail: Instance of the testrail api class
    :param name: Test run name
    :param project_id: Project ID
    :return: Dictionary with section ID and suite ID
    """
    try:
        if project_id <= 0:
            raise error('The project ID is not valid')
        if name == '':
            raise error('The name is not be empty')
        for section in testrail.sections.get_sections(project_id=project_id):
            if str(section['name']).lower() == name.lower():
                return {
                    'id': section['id'],
                    'suite_id': section['suite_id'],
                }
        section = testrail.sections.add_section(project_id=project_id, name=name)
        return {
            'id': section['id'],
            'suite_id': section['suite_id'],
        }
    except Exception:
        pass
