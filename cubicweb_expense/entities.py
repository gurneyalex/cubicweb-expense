"""this contains the template-specific entities' classes"""

from cubicweb.entities import AnyEntity, fetch_config


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
    __regid__ = 'Expense'
    fetch_attrs, cw_fetch_order = fetch_config(['title'])

    def dc_long_title(self):
        users = self.paid_by()
        if users:
            return u'%s (%s)' % (self.title,
                                 ', '.join(euser.login for euser in self.paid_by()))
        return self.title

    def euro_taxes(self):
        return sum(line.euro_taxes() for line in self.has_lines)

    def euro_total(self):
        return sum(line.euro_amount() for line in self.has_lines)


class ExpenseLine(AnyEntity):
    __regid__ = 'ExpenseLine'
    fetch_attrs, cw_fetch_order = fetch_config(['diem', 'type', 'title', 'amount',
                                                'currency'])

    @property
    def parent_expense(self):
        expenses = [entity for entity in self.reverse_has_lines
                    if entity.e_schema == 'Expense']
        if expenses:
            return expenses[0]
        return None

    def dc_title(self):
        return u'%s - %s - %s - %s %s' % (self._cw.format_date(self.diem),
                                          self._cw._(self.type), self.title,
                                          self.amount, self.currency)

    def dc_long_title(self):
        expense = self.parent_expense
        if expense:
            return u'%s - %s' % (self.title, expense.dc_title())
        else:
            return self.dc_title()

    def euro_amount(self):
        if self.currency == 'EUR':
            return self.amount
        return self.exchange_rate * self.amount

    def euro_taxes(self):
        if self.taxes_currency == 'EUR':
            return self.taxes
        return self.taxes_exchange_rate * self.taxes


class PaidByAccount(AnyEntity):
    __regid__ = 'PaidByAccount'
    fetch_attrs, cw_fetch_order = fetch_config(['label', 'account'])

    def dc_title(self):
        return self.label

    def dc_long_title(self):
        return u'%s (%s)' % (self.label, self.account)


class PaidForAccount(PaidByAccount):
    __regid__ = 'PaidForAccount'


class Refund(LineContainerMixIn, AnyEntity):
    __regid__ = 'Refund'
    fetch_attrs = ('payment_date', 'payment_mode')

    def dc_title(self):
        _ = self._cw._
        return u'%s %s, %s: %s' % (_('refund for account'),
                                   self.paid_by_accounts()[0].view('textincontext'),
                                   _('amount'), self.total)

    def for_user(self):
        account = self.to_account[0]
        if account.associated_to:
            return account.associated_to[0]
        return None
