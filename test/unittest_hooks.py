"""unittests for cubicweb-expense hooks"""

from logilab.common.testlib import unittest_main

from cubicweb.devtools.testlib import MAILBOX

from _helpers import HelpersTC

class HooksTC(HelpersTC):
    def test_refund_is_created(self):
        rset = self.execute('Any R,PA,COUNT(L) WHERE R has_lines L, R to_account PA')
        # only one refund should have been created (because no refund
        # is needed for company expenses)
        self.assertEquals(len(rset), 1)
        self.assertEquals(rset[0][1], self.account1)
        self.assertEquals(rset[0][2], 1)

    def test_refunds_gets_updated_on_new_lines(self):
        rset = self.execute('Any R,PA WHERE R has_lines L, R to_account PA')
        refund = rset[0][0]
        expense = self.add_entity('Expense', title=u'expense 2')
        self.add_expense_line(expense, self.account1)
        self.commit()
        self.accept(expense)
        rset = self.execute('Any COUNT(L) WHERE R has_lines L, R eid %(r)s', {'r': refund})
        self.assertEquals(rset[0][0], 2)

    def test_no_refund_is_created_for_company_account(self):
        count = self.execute('Any COUNT(R) WHERE R is Refund, R in_state S, S name "preparation"')[0][0]
        expense = self.add_entity('Expense', title=u'company expense')
        self.add_expense_line(expense, self.account_comp)
        self.commit()
        self.accept(expense)
        newcount = self.execute('Any COUNT(R) WHERE R is Refund, R in_state S, S name "preparation"')[0][0]
        self.assertEquals(newcount, count)

    def test_no_refund_is_created_while_not_accepted(self):
        """make sure no refund is created until expense was accepted"""
        count = self.refund_lines_count(self.account1)
        expense = self.add_entity('Expense', title=u'expense 1')
        self.add_expense_line(expense, self.account1)
        self.commit() # to fire corresponding operations
        newcount = self.refund_lines_count(self.account1)
        self.assertEquals(newcount, count)
        self.accept(expense)
        newcount = self.refund_lines_count(self.account1)
        self.assertEquals(newcount, count+1)


    def test_expense_accepted_notification(self):
        expense = self.add_entity('Expense', title=u'expense 2')
        self.add_expense_line(expense, self.account1)
        # force expense to its initial state, otherwise StatusChangeHook won't be called
        self.commit()
        self.assertEquals(len(MAILBOX), 0, MAILBOX)
        self.accept(expense) # to fire corresponding operations
        self.assertEquals(len(MAILBOX), 1, MAILBOX)
        self.assertUnorderedIterableEquals(MAILBOX[0].recipients, ['john@test.org'])

    def test_refund_acted_notification(self):
        expense1 = self.add_entity('Expense', title=u'expense 2')
        self.add_expense_line(expense1, self.account1)
        self.commit()
        self.accept(expense1)
        MAILBOX[:] = []
        rql = 'SET R in_state S WHERE R is Refund, R to_account A, A eid %(a)s, S name "paid"'
        account1 = self.execute('Any X WHERE X eid %(x)s', {'x': self.account1}, 'x').get_entity(0, 0)
        account1.reverse_to_account[0].fire_transition('pay')
        self.assertEquals(len(MAILBOX), 0, MAILBOX)
        self.commit() # to fire corresponding operations
        self.assertEquals(len(MAILBOX), 1, MAILBOX)
        email1 = MAILBOX[0]
        self.assertUnorderedIterableEquals(email1.recipients, ['john@test.org'])
        MAILBOX[:] = []
        expense2 = self.add_entity('Expense', title=u'expense 3')
        self.add_expense_line(expense2, self.account1)
        self.commit()
        self.accept(expense2)
        rql = 'SET R in_state S WHERE R is Refund, R to_account A, A eid %(a)s, S name "paid", NOT R in_state S'
        account1.clear_all_caches()
        account1.reverse_to_account[0].fire_transition('pay')
        self.commit() # to fire corresponding operations
        email2 = MAILBOX[0]
        self.assertUnorderedIterableEquals(email2.recipients, ['john@test.org'])
        self.failIfEqual(email2.message.get('Message-id'), email1.message.get('Message-id'))


    def test_automatic_refund_with_existing_line(self):
        refund = self.add_entity('Refund')
        # NOTE: use account2 which doesn't have a refund yet
        self.add_relation(refund.eid, 'to_account', self.account2)
        expense = self.add_entity('Expense', title=u'expense 2')
        line1eid = self.add_expense_line(expense, self.account2)
        line2eid = self.add_expense_line(expense, self.account2)
        line3eid = self.add_expense_line(expense, self.account2)
        self.add_relation(refund.eid, 'has_lines', line1eid)
        self.add_relation(refund.eid, 'has_lines', line2eid)
        self.commit()
        rset = self.execute('Any R,COUNT(L) WHERE R has_lines L, R eid %s' % refund.eid)
        self.assertEquals(len(rset), 1)
        self.assertEquals(rset[0][1], 2)
        self.accept(expense)
        rset = self.execute('Any L WHERE R has_lines L, R eid %(r)s', {'r': refund.eid})
        self.assertEquals(len(rset), 3)


if __name__ == '__main__':
    unittest_main()
