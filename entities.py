"""this contains the template-specific entities' classes"""

from cubicweb.entities import AnyEntity, fetch_config
from cubicweb.entities.authobjs import EUser as BaseEUser


class EUser(BaseEUser):
    __rtags__ = {'lives_at': 'inlineview'}

class LineContainerMixIn(object):
    """mixin class used by all entities containing expense lines"""
    def paid_by(self):
        """returns the list of eusers who paid something
        in this container
        """
        accounts = self.paid_by_accounts()
        return [acc.associated_to[0] for acc in accounts if acc.associated_to]

    def paid_by_accounts(self):
        """returns the list of accounts used in this container
        """
        accounts = []
        eids = set()
        for line in self.has_lines:
            account = line.paid_by[0]
            if account.eid not in eids:
                accounts.append(account)
                eids.add(account.eid)
        return accounts

    def totals_paid_by(self):
        """returns a dictionnary containing the total paid by each euser who
        paid something
        """
        tot = {}
        for line in self.has_lines:
            account = line.paid_by[0]
            if account.associated_to:
                euser = account.associated_to[0]
                tot.setdefault(euser, 0.0)
                tot[euser] += line.euro_amount()
        return tot
            
    @property
    def start(self):
        return min(line.diem for line in self.has_lines)

    @property
    def stop(self):
        return max(line.diem for line in self.has_lines)

    @property
    def total(self):
        return sum(line.amount for line in self.has_lines)

    @property
    def taxes(self):
        return sum(line.taxes for line in self.has_lines)

    

class Expense(LineContainerMixIn, AnyEntity):
    id = 'Expense'
    fetch_attrs, fetch_order = fetch_config(['title'])
    __rtags__ = {'has_lines' : ('inlineview', 'add_on_new')}

    def dc_long_title(self):
        users = self.paid_by()
        if users:
            return u'%s (%s)' % (self.title,
                                 ', '.join(euser.login for euser in self.paid_by()))
        return self.title


class ExpenseLine(AnyEntity):
    id = 'ExpenseLine'
    fetch_attrs, fetch_order = fetch_config(['diem', 'type', 'title', 'amount', 'currency'],
                                            'diem')
    
    @property
    def parent_expense(self):
        expenses = [entity for entity in self.reverse_has_lines
                        if entity.e_schema == 'Expense']
        if expenses:
            return expenses[0]
        return None

    def parent(self):
        return self.parent_expense

    def dc_title(self):
        return u'%s - %s - %s - %s %s' % (self.format_date(self.diem),
                                          self.req._(self.type), self.title,
                                          self.amount, self.currency) 


    def dc_long_title(self):
        expense = self.parent_expense
        if expense :
            return u'%s - %s' % (self.title, expense.dc_title())
        else:
            return self.dc_title()


    def euro_amount(self):
        return self.exchange_rate * self.amount

    def euro_taxes(self):
        if self.currency == self.taxe_currency:
            if self.currency == 'EUR':
                real_taxes = self.taxes
            else:
                real_taxes = self.taxes * self.exchange_rate
        return real_taxes
                

class PaidByAccount(AnyEntity):
    id = 'PaidByAccount'
    fetch_attrs, fetch_order = fetch_config(['label', 'account'])

    def dc_title(self):
        return self.label

    def dc_long_title(self):
        return u'%s (%s)' % (self.label, self.account)


class PaidForAccount(PaidByAccount):
    id = 'PaidForAccount'


class Refund(LineContainerMixIn, AnyEntity):
    id = 'Refund'

    fetch_attrs = ('payment_date', 'payment_mode')
    
    def dc_title(self):
        _ = self.req._
        return u'%s %s, %s: %s' % (_('refund for account'),
                                   self.paid_by_accounts()[0].view('textincontext'),
                                   _('amount'), self.total)

    def for_user(self):
        account = self.to_account[0]
        if account.associated_to:
            return account.associated_to[0]
        return None
