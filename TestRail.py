from pytest import mark


class TestRail:
    @staticmethod
    def id(*ids: str) -> mark:
        """
        Assigning an id to a label in pytest
        :param ids: ID of the test case in the testrail
        :return: The pytest label
        """
        return mark.testrail_ids(ids=ids)

    @staticmethod
    def suite(*name: str) -> mark:
        """
        Assigning an suite to a label in pytest
        :param name: Suite of the test case in the testrail
        :return: The pytest label
        """
        return mark.testrail_suite(name=name)
