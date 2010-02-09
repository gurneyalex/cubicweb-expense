from logilab.common.testlib import unittest_main

from _helpers import HelpersTC

class EntitiesTC(HelpersTC):

    def test_totals_paid_by(self):
        expense = self.request().create_entity('Expense', title=u'expense 2')
        self.add_expense_line(expense, self.account1)
        self.add_expense_line(expense, self.account2)
        self.add_expense_line(expense, self.account1)
        paid_by = dict( (euser.eid, value)
                        for euser, value in expense.totals_paid_by().items())
        self.assertEquals(paid_by, {self.user1: 2, self.user2: 1})

if __name__ == '__main__':
    unittest_main()
