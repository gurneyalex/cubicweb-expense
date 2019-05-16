"""tests for expense's security"""

import unittest

from cubicweb import Unauthorized, ValidationError

from _helpers import HelpersTC


class SecurityTC(HelpersTC):

    def test_users_cannot_modify_accepted_expense(self):
        with self.new_access('john').repo_cnx() as cnx:
            rset = cnx.execute('Any E WHERE E is Expense, E has_lines EE, EE paid_by PA, '
                               'E in_state S, S name "accepted", PA associated_to U, U eid %(u)s',
                               {'u': self.user1})  # user1 is john
            self.assertEqual(len(rset), 1)
            expense = rset.get_entity(0, 0)
            self.add_expense_line(cnx, expense, self.account1)
            self.assertRaises(Unauthorized, cnx.commit)

    def test_users_cannot_accept_expense(self):
        with self.new_access('john').repo_cnx() as cnx:
            expense = self.create_and_submit_expense(cnx)
            cnx.commit()
            self.assertRaises(ValidationError, expense.cw_adapt_to('IWorkflowable').fire_transition, 'accept')

    def test_users_cannot_update_accepted_expense_line(self):
        with self.admin_access.repo_cnx() as cnx:
            expense = cnx.create_entity('Expense', title=u'company expense')
            lineeid = self.add_expense_line(cnx, expense, self.account1)
            cnx.commit()
            self.accept(cnx, expense)
        with self.new_access('john').repo_cnx() as cnx:
            cnx.execute('SET E amount %(a)s WHERE E eid %(e)s', {'e': lineeid, 'a': 12.3})
            self.assertRaises(Unauthorized, cnx.commit)

    def test_users_can_create_expenses(self):
        with self.new_access('john').repo_cnx() as cnx:
            self.create_and_submit_expense(cnx)
            cnx.commit()

    def test_users_cannot_create_refunds(self):
        with self.new_access('john').repo_cnx() as cnx:
            rset = cnx.execute('Any EE WHERE E is Expense, E has_lines EE, EE paid_by PA, '
                               'E in_state S, S name "accepted", PA associated_to U, U eid %(u)s',
                               {'u': self.user1})  # user1 is john
            self.assertEqual(len(rset), 1)
            lineeid = rset[0][0]
            rql = 'INSERT Refund R: R has_lines E, R to_account A WHERE E eid %(e)s, A eid %(a)s'
            cnx.execute(rql, {'e': lineeid, 'a': self.account1})
            self.assertRaises(Unauthorized, cnx.commit)

    def test_users_cannot_update_refunds(self):
        with self.new_access('john').repo_cnx() as cnx:
            rset = cnx.execute('Any R WHERE R is Refund, R has_lines EE, EE paid_by PA, '
                               'R to_account PA, PA associated_to U, U eid %(u)s',
                               {'u': self.user1})  # user1 is john
            self.assertEqual(len(rset), 1)
            line = self.new_expense_line(cnx, self.account1)
            rql = 'SET R has_lines E WHERE E eid %(e)s'
            cnx.execute(rql, {'e': line.eid})
            self.assertRaises(Unauthorized, cnx.commit)


if __name__ == '__main__':
    unittest.main()
