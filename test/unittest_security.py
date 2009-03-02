"""tests for expense's security"""

from logilab.common.testlib import unittest_main

from cubicweb.devtools.apptest import MAILBOX
from cubicweb import Unauthorized, ValidationError

from _helpers import HelpersTC

class SecurityTC(HelpersTC):

    
    def test_users_cannot_modify_accepted_expense(self):
        self.login('john')
        rset = self.execute('Any E WHERE E is Expense, E has_lines EE, EE paid_by PA, '
                            'E in_state S, S name "accepted", PA associated_to U, U eid %(u)s',
                            {'u': self.user1}) # user1 is john
        self.assertEquals(len(rset), 1)
        expense = rset.get_entity(0, 0)
        self.add_expense_line(expense, self.account1)
        self.assertRaises(Unauthorized, self.commit)

    def test_users_cannot_accept_expense(self):
        self.login('john')
        expense = self.create_and_submit_expense()
        self.assertRaises(ValidationError, self.execute, 'SET X in_state S WHERE X eid %(x)s, S name "accepted"',
                          {'x': expense.eid})

    def test_users_cannot_update_accepted_expense_line(self):
        expense = self.add_entity('Expense', title=u'company expense')
        lineeid = self.add_expense_line(expense, self.account1)
        self.accept(expense)
        self.login('john')
        self.execute('SET E amount %(a)s WHERE E eid %(e)s', {'e': lineeid, 'a': 12.3})
        self.assertRaises(Unauthorized, self.commit)

    def test_users_can_create_expenses(self):
        self.login('john')
        self.create_and_submit_expense()               
        self.commit()       
   
    def test_users_cannot_create_refunds(self):
        self.login('john')
        rset = self.execute('Any EE WHERE E is Expense, E has_lines EE, EE paid_by PA, '
                            'E in_state S, S name "accepted", PA associated_to U, U eid %(u)s',
                            {'u': self.user1}) # user1 is john
        self.assertEquals(len(rset), 1)
        lineeid = rset[0][0]
        rql = 'INSERT Refund R: R has_lines E, R to_account A WHERE E eid %(e)s, A eid %(a)s'
        self.execute(rql, {'e': lineeid, 'a': self.account1})
        self.assertRaises(Unauthorized, self.commit)

    def test_users_canot_update_refunds(self):
        self.login('john')
        rset = self.execute('Any R WHERE R is Refund, R has_lines EE, EE paid_by PA, '
                            'R to_account PA, PA associated_to U, U eid %(u)s',
                            {'u': self.user1}) # user1 is john
        self.assertEquals(len(rset), 1)
        line = self.new_expense_line(self.account1)
        rql = 'SET R has_lines E WHERE E eid %(e)s'
        self.execute(rql, {'e': line.eid})
        self.assertRaises(Unauthorized, self.commit)

           

if __name__ == '__main__':
    unittest_main()
