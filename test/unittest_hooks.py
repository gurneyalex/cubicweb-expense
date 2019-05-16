"""unittests for cubicweb-expense hooks"""

import unittest

from cubicweb.devtools.testlib import MAILBOX

from _helpers import HelpersTC


class HooksTC(HelpersTC):
    def test_refund_is_created(self):
        with self.admin_access.repo_cnx() as cnx:
            rset = cnx.execute('Any R,PA,COUNT(L) WHERE R has_lines L, R to_account PA')
            # only one refund should have been created (because no refund
            # is needed for company expenses)
            self.assertEqual(len(rset), 1)
            self.assertEqual(rset[0][1], self.account1)
            self.assertEqual(rset[0][2], 1)

    def test_refunds_gets_updated_on_new_lines(self):
        with self.admin_access.repo_cnx() as cnx:
            rset = cnx.execute('Any R,PA WHERE R has_lines L, R to_account PA')
            refund = rset[0][0]
            expense = cnx.create_entity('Expense', title=u'expense 2')
            self.add_expense_line(cnx, expense, self.account1)
            cnx.commit()
            self.accept(cnx, expense)
            rset = cnx.execute('Any COUNT(L) WHERE R has_lines L, R eid %(r)s', {'r': refund})
            self.assertEqual(rset[0][0], 2)

    def test_no_refund_is_created_for_company_account(self):
        with self.admin_access.repo_cnx() as cnx:
            count = cnx.execute('Any COUNT(R) WHERE R is Refund, R in_state S, S name "preparation"')[0][0]
            expense = cnx.create_entity('Expense', title=u'company expense')
            self.add_expense_line(cnx, expense, self.account_comp)
            cnx.commit()
            self.accept(cnx, expense)
            newcount = cnx.execute('Any COUNT(R) WHERE R is Refund, R in_state S, S name "preparation"')[0][0]
            self.assertEqual(newcount, count)

    def test_no_refund_is_created_while_not_accepted(self):
        """make sure no refund is created until expense was accepted"""
        with self.admin_access.repo_cnx() as cnx:
            count = self.refund_lines_count(cnx, self.account1)
            expense = cnx.create_entity('Expense', title=u'expense 1')
            self.add_expense_line(cnx, expense, self.account1)
            cnx.commit()  # to fire corresponding operations
            newcount = self.refund_lines_count(cnx, self.account1)
            self.assertEqual(newcount, count)
            self.accept(cnx, expense)
            newcount = self.refund_lines_count(cnx, self.account1)
            self.assertEqual(newcount, count + 1)

    def test_expense_accepted_notification(self):
        with self.admin_access.repo_cnx() as cnx:
            expense = cnx.create_entity('Expense', title=u'expense 2')
            self.add_expense_line(cnx, expense, self.account1)
            # force expense to its initial state, otherwise StatusChangeHook won't be called
            cnx.commit()
            self.assertEqual(len(MAILBOX), 0, MAILBOX)
            self.accept(cnx, expense)  # to fire corresponding operations
            self.assertEqual(len(MAILBOX), 1, MAILBOX)
            self.assertCountEqual(MAILBOX[0].recipients, ['john@test.org'])

    def test_refund_acted_notification(self):
        with self.admin_access.repo_cnx() as cnx:
            expense1 = cnx.create_entity('Expense', title=u'expense 2')
            self.add_expense_line(cnx, expense1, self.account1)
            cnx.commit()
            self.accept(cnx, expense1)
            MAILBOX[:] = []
            account1 = cnx.execute('Any X WHERE X eid %(x)s', {'x': self.account1}).get_entity(0, 0)
            account1.reverse_to_account[0].cw_adapt_to('IWorkflowable').fire_transition('pay')
            self.assertEqual(len(MAILBOX), 0, MAILBOX)
            cnx.commit()  # to fire corresponding operations
            self.assertEqual(len(MAILBOX), 1, MAILBOX)
            email1 = MAILBOX[0]
            self.assertCountEqual(email1.recipients, ['john@test.org'])
            MAILBOX[:] = []
            expense2 = cnx.create_entity('Expense', title=u'expense 3')
            self.add_expense_line(cnx, expense2, self.account1)
            cnx.commit()
            self.accept(cnx, expense2)
            account1.cw_clear_all_caches()
            account1.reverse_to_account[0].cw_adapt_to('IWorkflowable').fire_transition('pay')
            cnx.commit()  # to fire corresponding operations
            email2 = MAILBOX[0]
            self.assertCountEqual(email2.recipients, ['john@test.org'])
            self.assertNotEqual(email2.message.get('Message-id'), email1.message.get('Message-id'))

    def test_automatic_refund_with_existing_line(self):
        with self.admin_access.repo_cnx() as cnx:
            refund = cnx.create_entity('Refund')
            # NOTE: use account2 which doesn't have a refund yet
            self.add_relation(cnx, refund.eid, 'to_account', self.account2)
            expense = cnx.create_entity('Expense', title=u'expense 2')
            line1eid = self.add_expense_line(cnx, expense, self.account2)
            line2eid = self.add_expense_line(cnx, expense, self.account2)
            self.add_expense_line(cnx, expense, self.account2)
            self.add_relation(cnx, refund.eid, 'has_lines', line1eid)
            self.add_relation(cnx, refund.eid, 'has_lines', line2eid)
            cnx.commit()
            rset = cnx.execute('Any R,COUNT(L) WHERE R has_lines L, R eid %s' % refund.eid)
            self.assertEqual(len(rset), 1)
            self.assertEqual(rset[0][1], 2)
            self.accept(cnx, expense)
            rset = cnx.execute('Any L WHERE R has_lines L, R eid %(r)s', {'r': refund.eid})
            self.assertEqual(len(rset), 3)


if __name__ == '__main__':
    unittest.main()
