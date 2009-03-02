"""specific views for expense component

:organization: Logilab
:copyright: 2008 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

import os
from mx.DateTime import today

from logilab.mtconverter import html_escape

from cubicweb.common.selectors import onelinerset_selector, accept_selector
from cubicweb.common.view import EntityView
from cubicweb.web.action import EntityAction
from cubicweb.web.views.baseviews import PrimaryView
from cubicweb.web.views.baseforms import ChangeStateForm
from cubicweb.web.views.urlrewrite import SimpleReqRewriter

## actions ####################################################################

class PDFAction(EntityAction):
    accepts = ('Expense','Refund')
    id = 'pdfaction'
    title = _('generate pdf document')
    category = 'mainactions'
    
    def url(self):
        entity = self.entity(0, 0)
        return entity.absolute_url(vid='pdfexport')


class ExpensePrimaryView(PrimaryView):
    accepts = ('Expense',)
    
    def cell_call(self, row, col):
        _ = self.req._
        expense = self.complete_entity(row, col)
        title = html_escape(u'%s - %s' % (expense.dc_title(), _(expense.state)))
        self.w(u'<h1>%s</h1>' % title)
        self.w(u'%s: %s %s %s' % (_('total'), expense.total,
                                  _('including taxes'), expense.taxes))
        rset = self.req.execute('Any EID,T,ET,EA,EC,C,GROUP_CONCAT(CCL),CL GROUPBY EID,T,ET,EC,EA,C,CL '
                                'WHERE X has_lines E, X eid %(x)s, E eid EID, E type T, '
                                'E title ET, E currency EC, E amount EA, E paid_by C?, '
                                'C label CL, E paid_for CC, CC label CCL' , {'x': expense.eid})
        
        headers = [_('id'), _('type'), _('title'), _('amount'), _('currency'),
                   _('payed_by'), _('payed_for') ]
        self.wview('table', rset, headers=headers, displaycols=range(7), displayfilter=True)
        
class RefundPrimaryView(PrimaryView):
    accepts = ('Refund',)

    def cell_call(self, row, col):
        _ = self.req._
        refund = self.complete_entity(row, col)
        title = html_escape(u'%s - %s' % (refund.dc_title(), _(refund.state)))
        self.w(u'<h1>%s</h1>' % title)
        self.w(u'%s: %s' % (_('account to refund'), refund.paid_by_accounts()[0].view('oneline')))
        self.w(u'<br/>')
        self.w(u'%s: %s' % (_('total'), refund.total))
        self.w(u'<br/>')
        if refund.payment_date:
            self.w(u'%s: %s' % (_('payment date'), self.format_date(refund.payment_date)))
            self.w(u'<br/>')
        if refund.payment_mode:
            self.w(u'%s: %s' % (_('payment mode'), refund.payment_mode))
            self.w(u'<br/>')
        rset = self.req.execute('Any E,ET,EC,EA WHERE X has_lines E, X eid %(x)s, '
                                'E title ET, E currency EC, E amount EA',
                                {'x': refund.eid})
        self.wview('table', rset, displayfilter=True)


class RefundChangeStateForm(ChangeStateForm):
    accepts = ('Refund',)
    def fill_form(self, entity, state, dest):
        super(RefundChangeStateForm, self).fill_form(entity, state, dest)
        if dest.name == 'paid':
            for attr in ('payment_date', 'payment_mode'):
                wdg = entity.get_widget(attr, 'subject')
                self.w(wdg.render_label(entity))
                self.w(wdg.edit_render(entity))
                self.w(wdg.render_help(entity))
                self.w(u'<br />')


class PdfExportView(EntityView):
    id = 'pdfexport'
    accepts = ('Refund', 'Expense')
    title = _('pdf export')
    content_type = 'application/pdf'
    __selectors__ = (onelinerset_selector, accept_selector)
    
    templatable = False
    binary = True

    def call(self):
        _ = self.req._
        from cubes.expense.pdfgen.writers import PDFWriter
        
        writer = PDFWriter(self.config)
        entity = self.rset.get_entity(0, 0)
        entity.complete()
        # XXX reportlab needs HOME and getcwd to find fonts
        home_backup = os.environ.get('HOME')
        getcwd_backup = os.getcwd
        try:
            os.environ['HOME'] = 'wtf'
            os.getcwd = lambda: 'wtf'
            writer.write(entity, self._stream)
        finally:
            if home_backup:
                os.environ['HOME'] = home_backup
            os.getcwd = getcwd_backup
            

## urls #######################################################################
class ExpenseURLRewriter(SimpleReqRewriter):
    rules = [
        ('/todo', dict(rql='Any E WHERE E is Expense, E in_state S, S name "submitted"')),
        ]

