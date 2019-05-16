"""base helper classes for eexpense's unittests"""

from datetime import date

from cubicweb.devtools.testlib import CubicWebTC


class HelpersTC(CubicWebTC):
    # helpers
    def add_relation(self, cnx, eidfrom, rtype, eidto):
        cnx.execute('SET X %s Y WHERE X eid %%(x)s, Y eid %%(y)s' % rtype,
                    {'x': eidfrom, 'y': eidto})

    def new_expense_line(self, cnx, paid_by_eid):
        line = cnx.create_entity('ExpenseLine', title=u'aline', diem=date.today(),
                                 type=u'food', amount=1., taxes=0.)
        self.add_relation(cnx, line.eid, 'paid_by', paid_by_eid)
        self.add_relation(cnx, line.eid, 'paid_for', self.accountfor)
        return line

    def add_expense_line(self, cnx, expense, paid_by_eid):
        line = self.new_expense_line(cnx, paid_by_eid)
        self.add_relation(cnx, expense.eid, 'has_lines', line.eid)
        return line.eid

    def accept(self, cnx, expense):
        expense.cw_adapt_to('IWorkflowable').change_state('accepted')
        cnx.commit()  # to fire corresponding operations

    def new_account(self, cnx, login):
        user = self.create_user(cnx, login)
        cnx.execute('INSERT EmailAddress E: E address %(add)s, U use_email E, U primary_email E '
                    'WHERE U eid %(u)s', {'u': user.eid, 'add': login + '@test.org'})
        account = cnx.create_entity('PaidByAccount', label=u'%s account' % login)
        self.add_relation(cnx, account.eid, 'associated_to', user.eid)
        return user, account

    def refund_lines_count(self, cnx, account):
        return cnx.execute('Any COUNT(EL) WHERE R is Refund, R has_lines EL, R to_account A, '
                           'A eid %(a)s, R in_state S, S name "preparation"',
                           {'a': account})[0][0]

    def create_and_submit_expense(self, cnx):
        expense = cnx.create_entity('Expense', title=u'company expense')
        self.add_expense_line(cnx, expense, self.account1)
        cnx.commit()
        expense.cw_adapt_to('IWorkflowable').fire_transition('submit')
        return expense

    def setup_database(self):
        with self.admin_access.repo_cnx() as cnx:
            add = cnx.create_entity
            # users and accounts initialization
            user1, account1 = self.new_account(cnx, u'john')
            user2, account2 = self.new_account(cnx, u'bill')
            self.user1, self.user2 = user1.eid, user2.eid
            account_comp = add('PaidByAccount', label=u'company account')
            accountfor = add('PaidForAccount', label=u'whatever')
            self.account1, self.account2 = account1.eid, account2.eid
            self.account_comp, self.accountfor = account_comp.eid, accountfor.eid
            # expense creation
            self.expense = add('Expense', title=u'sprint')
            self.add_expense_line(cnx, self.expense, account1.eid)
            self.add_expense_line(cnx, self.expense, account_comp.eid)
            cnx.commit()
            self.accept(cnx, self.expense)
