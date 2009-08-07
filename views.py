"""specific views for expense component

:organization: Logilab
:copyright: 2008-2009 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

import os
from cStringIO import StringIO

from logilab.mtconverter import html_escape

from cubicweb.selectors import one_line_rset, implements
from cubicweb.view import EntityView
from cubicweb.web import uicfg, action
from cubicweb.web.views import primary, autoform, workflow, urlrewrite


uicfg.autoform_is_inlined.tag_subject_of(('CWUser', 'lives_at', '*'), True)
uicfg.autoform_section.tag_subject_of(('CWUser', 'lives_at', '*'), 'generated')
uicfg.autoform_is_inlined.tag_subject_of(('Expense', 'has_lines', '*'), True)
uicfg.autoform_section.tag_subject_of(('Expense', 'has_lines', '*'), 'generated')
uicfg.autoform_section.tag_subject_of(('ExpenseLine', 'paid_by', '*'), 'primary')
uicfg.autoform_field_kwargs.tag_subject_of(('ExpenseLine', 'paid_by', '*'), {'sort': True})
uicfg.autoform_section.tag_subject_of(('ExpenseLine', 'paid_for', '*'), 'secondary')
uicfg.autoform_field_kwargs.tag_subject_of(('ExpenseLine', 'paid_for', '*'), {'sort': True})

uicfg.autoform_permissions_overrides.tag_subject_of(('Expense', 'has_lines', '*'),
                                            'add_on_new')

uicfg.primaryview_section.tag_subject_of(('Expense', 'has_lines', '*'), 'hidden')
uicfg.primaryview_section.tag_subject_of(('Refund', 'has_lines', '*'), 'hidden')
uicfg.primaryview_section.tag_subject_of(('Refund', 'paid_by_accounts', '*'), 'hidden')


class PDFAction(action.Action):
    id = 'pdfaction'
    __select__ = one_line_rset() & implements('Expense','Refund')

    title = _('generate pdf document')
    category = 'mainactions'

    def url(self):
        return self.entity(self.row or 0, self.col or 0).absolute_url(vid='pdfexport')


class ExpenseURLRewriter(urlrewrite.SimpleReqRewriter):
    rules = [
        ('/todo', dict(rql='Any E,S WHERE E is Expense, '
                       'E in_state S, S name "submitted"')),
        ]

## views and forms ############################################################

class ExpensePrimaryView(primary.PrimaryView):
    __select__ = implements('Expense',)

    def render_entity_title(self, entity):
        title = html_escape(u'%s - %s' % (entity.dc_title(),
                                          self.req._(entity.state)))
        self.w(u'<h1><span class="etype">%s</span> %s</h1>'
               % (entity.dc_type().capitalize(), title))

    def render_entity_attributes(self, entity):
        _ = self.req._
        self.w(u'%s: %s %s %s' % (_('total'), entity.euro_total(),
                                  _('including taxes'), entity.euro_taxes()))
        rset = self.req.execute('Any EID,T,ET,EA,EC,C,GROUP_CONCAT(CCL),CL '
                                'GROUPBY EID,T,ET,EC,EA,C,CL '
                                'WHERE X has_lines E, X eid %(x)s, E eid EID, '
                                'E type T, E title ET, E currency EC, '
                                'E amount EA, E paid_by C?, C label CL, '
                                'E paid_for CC, CC label CCL' ,
                                {'x': entity.eid})
        headers = [_('eid'), _('type'), _('title'), _('amount'), _('currency'),
                   _('paid_by'), _('paid_for') ]
        self.wview('table', rset, headers=headers,
                   displaycols=range(len(headers)), displayfilter=True)


class RefundPrimaryView(primary.PrimaryView):
    __select__ = implements('Refund',)

    def render_entity_title(self, entity):
        title = html_escape(u'%s - %s' % (entity.dc_title(), _(entity.state)))
        self.w(u'<h1><span class="etype">%s</span> %s</h1>'
               % (entity.dc_type().capitalize(), title))

    def render_entity_attributes(self, entity):
        _ = self.req._
        self.field(_('account to refund'),
                   entity.paid_by_accounts()[0].view('oneline'), tr=False)
        self.field(_('total'), entity.total, tr=False)
        if entity.payment_date:
            self.field(_('payment date'), self.format_date(entity.payment_date),
                       tr=False)
        if entity.payment_mode:
            self.field(_('payment mode'), entity.payment_mode, tr=False)
        rset = self.req.execute('Any E,ET,EC,EA WHERE X has_lines E, X eid %(x)s, '
                                'E title ET, E currency EC, E amount EA',
                                {'x': entity.eid})
        self.wview('table', rset, displayfilter=True)


class PdfExportView(EntityView):
    id = 'pdfexport'
    __select__ = one_line_rset() & implements('Refund', 'Expense')

    title = _('pdf export')
    content_type = 'application/pdf'
    templatable = False
    binary = True

    def cell_call(self, row, col):
        # import error to avoid import error if reportlab isn't available
        from cubes.expense.pdfgen.writers import PDFWriter
        _ = self.req._
        writer = PDFWriter(self.config)
        entity = self.rset.get_entity(row, col)
        entity.complete()
        # XXX reportlab needs HOME and getcwd to find fonts
        home_backup = os.environ.get('HOME')
        getcwd_backup = os.getcwd
        try:
            os.environ['HOME'] = 'wtf'
            os.getcwd = lambda: 'wtf'
            # NOTE: we could use self.w.__self__ directly
            stream = StringIO()
            writer.write(entity, stream)
            self.w(stream.getvalue())
        finally:
            if home_backup:
                os.environ['HOME'] = home_backup
            os.getcwd = getcwd_backup


class RefundChangeStateForm(workflow.ChangeStateForm):
    __select__ = implements('Refund')
    payment_date = autoform.etype_relation_field('Refund', 'payment_date')
    payment_mode = autoform.etype_relation_field('Refund', 'payment_mode')

