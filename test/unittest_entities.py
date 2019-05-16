import unittest

from _helpers import HelpersTC


class EntitiesTC(HelpersTC):

    def test_totals_paid_by(self):
        with self.admin_access.repo_cnx() as cnx:
            expense = cnx.create_entity('Expense', title=u'expense 2')
            self.add_expense_line(cnx, expense, self.account1)
            self.add_expense_line(cnx, expense, self.account2)
            self.add_expense_line(cnx, expense, self.account1)
            paid_by = dict((euser.eid, value)
                           for euser, value in expense.totals_paid_by().items())
            self.assertEqual(paid_by, {self.user1: 2, self.user2: 1})


if __name__ == '__main__':
    unittest.main()
