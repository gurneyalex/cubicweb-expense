# -*- coding: utf-8 -*-
"""cubicweb-expense specific hooks and notification views

:organization: Logilab
:copyright: 2008-2009 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""

from itertools import groupby

from logilab.common.textutils import normalize_text

from cubicweb.selectors import implements
from cubicweb.server.pool import PreCommitOperation
from cubicweb.server.hooksmanager import Hook
from cubicweb.sobjects.notification import (RecipientsFinder, StatusChangeMixIn,
                                         NotificationView)

class UpdateRefundStateOperation(PreCommitOperation):
    """adds the new expense line automatically to the corresponding
    refund entity. If no refund entity is associated to the account
    who paid the expense, the operation will create one.
    """

    def precommit_event(self):
        session = self.session
        execute = session.execute
        unsafe_execute = session.unsafe_execute
        rql = 'Any A,U,EL ORDERBY A WHERE X has_lines EL, EL paid_by A, ' \
              'A associated_to U?, X eid %(x)s'
        acc_rset = execute(rql, {'x' : self.expense})
        for account, lines in groupby(acc_rset, lambda row: row[0]):
            # reset refund to None for this new account
            ref = None
            for _, euser, line in lines:
                if euser is None: # this is a company account, no refund needed
                    break
                ref = ref or self.get_or_create_refund_for(account)
                # users don't have permissions to add lines to refunds
                unsafe_execute('SET R has_lines EL WHERE R is Refund, R eid %(r)s, EL eid %(el)s, NOT EXISTS(R has_lines EL)',
                               {'r' : ref, 'el': line})


    def get_or_create_refund_for(self, account):
        rql = 'Any R WHERE R is Refund, R to_account A, A eid %(a)s, ' \
              'R in_state S, S name "preparation"'
        rset = self.session.execute(rql, {'a': account})
        if rset:
            return rset[0][0]
        rql = 'INSERT Refund R: R to_account A WHERE A eid %(a)s'
        # users don't have permission to add refunds
        return self.session.unsafe_execute(rql, {'a': account})[0][0]



class OnExpenseAcceptedHook(Hook):
    """
    * when an expense is going from "submitted" to "accepted", create
      (or update) refund entities accordingly
    """
    events = ('after_add_relation',)
    accepts = ('in_state',)

    def call(self, session, fromeid, rtype, toeid):
        etype = session.describe(fromeid)[0]
        if etype != 'Expense':
            return
        newstate = session.entity(toeid).name
        if newstate == 'accepted':
            UpdateRefundStateOperation(session, expense=fromeid)



class ExpenseLinesRecipientsFinder(RecipientsFinder):
    __select__ = implements('Expense', 'Refund')
    users_rql = ('Any X,E,A WHERE EE has_lines EL, EL paid_by AC, AC associated_to X, '
                 'X primary_email E, E address A, EE eid %(ee)s')

    def recipients(self):
        expense = self.entity(0)
        rset = self.req.execute(self.users_rql, {'ee': expense.eid})
        return sorted(set((u.get_email(), u.property_value('ui.language'))
                          for u in rset.entities()))


class ExpenseAcceptedView(StatusChangeMixIn, NotificationView):
    __select__ = implements('Expense')
    content = _("""
The expense ``%(title)s`` has been accepted :

Description
-----------
%(description)s

Detail
-----
%(detail)s

URL
---
%(url)s
""")

    def subject(self):
        return u'%s %s' % (self.req._('expense accepted: '), self.entity(0).title)

    def context(self, **kwargs):
        context = super(ExpenseAcceptedView, self).context(**kwargs)
        entity = self.complete_entity(0, 0)
        description = entity.printable_value('description', format='text/plain')
        description = normalize_text(description, 80)
        detail = u'\n'.join(line.view('textoutofcontext') for line in entity.has_lines)
        context.update({'description': description,
                        'title': entity.title,
                        'url': entity.absolute_url(),
                        'detail': detail,})
        return context



class RefundActedView(StatusChangeMixIn, NotificationView):
    __select__ = implements('Refund')
    content = _("""
Your expenses have been refuned (amount=%(amount)s euros.)

Detail
------
%(detail)s

URL
---
%(url)s
""")

    def subject(self):
        return self.req._('your expense will be refunded on your next payroll')

    def context(self, **kwargs):
        context = super(RefundActedView, self).context(**kwargs)
        entity = self.complete_entity(0, 0)
        detail = u'\n'.join(line.view('textoutofcontext') for line in entity.has_lines)
        context.update({'amount': entity.total,
                        'url': entity.absolute_url(),
                        'detail': detail,})
        return context

