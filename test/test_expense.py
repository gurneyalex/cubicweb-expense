"""template automatic tests"""
from logilab.common.testlib import unittest_main
from cubicweb.devtools.testlib import AutomaticWebTest

class AutomaticWebTest(AutomaticWebTest):

    def to_test_etypes(self):
        return set(('Expense', 'ExpenseLine', 'Refund',
                    'PaidByAccount', 'PaidForAccount'))

    def list_startup_views(self):
        return ()


if __name__ == '__main__':
    unittest_main()
