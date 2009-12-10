"""base helper classes for eexpense's unittests"""

from datetime import date

from cubicweb.devtools.apptest import EnvBasedTC

class HelpersTC(EnvBasedTC):
    ## helpers ################################################################
    def add_relation(self, eidfrom, rtype, eidto):
        self.execute('SET X %s Y WHERE X eid %%(x)s, Y eid %%(y)s' % rtype,
                     {'x': eidfrom, 'y': eidto}, ('x', 'y'))


    def new_expense_line(self, paid_by_eid):
        line = self.add_entity('ExpenseLine', title=u'aline', diem=date.today(),
                               type=u'food', amount=1., taxes=0.)
        self.add_relation(line.eid, 'paid_by', paid_by_eid)
        self.add_relation(line.eid, 'paid_for', self.accountfor)
        return line

    def add_expense_line(self, expense, paid_by_eid):
        line = self.new_expense_line(paid_by_eid)
        self.add_relation(expense.eid, 'has_lines', line.eid)
        return line.eid

    def accept(self, expense):
        expense.change_state('accepted')
        self.commit() # to fire corresponding operations

    def new_account(self, login):
        user = self.create_user(login)
        self.execute('INSERT EmailAddress E: E address %(add)s, U use_email E, U primary_email E '
                     'WHERE U eid %(u)s', {'u': user.eid, 'add': login+'@test.org'})
        account = self.add_entity('PaidByAccount', label=u'%s account' % login)
        self.add_relation(account.eid, 'associated_to', user.eid)
        return user, account

    def refund_lines_count(self, account):
        return self.execute('Any COUNT(EL) WHERE R is Refund, R has_lines EL, R to_account A, '
                            'A eid %(a)s, R in_state S, S name "preparation"',
                            {'a': account})[0][0]

    def create_and_submit_expense(self):
        expense = self.add_entity('Expense', title=u'company expense')
        lineeid = self.add_expense_line(expense, self.account1)
        self.commit()
        expense.fire_transition('submit')
        return expense

    def setup_database(self):
        add = self.add_entity
        # users and accounts initialization
        user1, account1 = self.new_account(u'john')
        user2, account2 = self.new_account(u'bill')
        self.user1, self.user2 = user1.eid, user2.eid
        account_comp = add('PaidByAccount', label=u'company account')
        accountfor = add('PaidForAccount', label=u'whatever')
        self.account1, self.account2 = account1.eid, account2.eid
        self.account_comp, self.accountfor = account_comp.eid, accountfor.eid
        # expense creation
        self.expense = add('Expense', title=u'sprint')
        self.line1 = line1 = self.add_expense_line(self.expense, account1.eid)
        line_comp = self.add_expense_line(self.expense, account_comp.eid)
        self.commit()
        self.accept(self.expense)


