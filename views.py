"""specific views for expense component

:organization: Logilab
:copyright: 2008-2011 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

import os
from cStringIO import StringIO

from logilab.mtconverter import xml_escape

from cubicweb.selectors import yes, one_line_rset, is_instance
from cubicweb.view import EntityView
from cubicweb.web import uicfg, action
from cubicweb.web.views import primary, autoform, workflow, urlrewrite, ibreadcrumbs

class ExpenseLineIBreadCrumbsAdapter(ibreadcrumbs.IBreadCrumbsAdapter):
    __select__ = is_instance('IBreadCrumbs')

    def parent_entity(self):
        return self.entity.parent_expense


class ExpenseURLRewriter(urlrewrite.SimpleReqRewriter):
    rules = [
        ('/todo', dict(rql='Any E,S WHERE E is Expense, '
                       'E in_state S, S name "submitted"')),
        ]

## forms #######################################################################

_afs = uicfg.autoform_section
_affk = uicfg.autoform_field_kwargs
_afs.tag_subject_of(('CWUser', 'lives_at', '*'), 'main', 'inlined')
_afs.tag_subject_of(('Expense', 'has_lines', '*'), 'main', 'inlined')

_afs.tag_subject_of(('ExpenseLine', 'paid_by', '*'), 'main', 'attributes')
_afs.tag_subject_of(('ExpenseLine', 'paid_by', '*'), 'muledit', 'attributes')
_affk.tag_subject_of(('ExpenseLine', 'paid_by', '*'), {'sort': True})
_afs.tag_subject_of(('ExpenseLine', 'paid_for', '*'), 'main', 'attributes')
_affk.tag_subject_of(('ExpenseLine', 'paid_for', '*'), {'sort': True})

# XXX still necessary?
uicfg.autoform_permissions_overrides.tag_subject_of(
    ('Expense', 'has_lines', '*'), 'add_on_new')


class RefundChangeStateForm(workflow.ChangeStateForm):
    __select__ = is_instance('Refund')
    payment_date = autoform.etype_relation_field('Refund', 'payment_date')
    payment_mode = autoform.etype_relation_field('Refund', 'payment_mode')


## views #######################################################################

_pvs = uicfg.primaryview_section
_pvs.tag_subject_of(('Expense', 'has_lines', '*'), 'hidden')
_pvs.tag_subject_of(('Refund', 'has_lines', '*'), 'hidden')
_pvs.tag_subject_of(('Refund', 'paid_by_accounts', '*'), 'hidden')

class ExpensePrimaryView(primary.PrimaryView):
    __select__ = is_instance('Expense',)

    def render_entity_title(self, entity):
        state = self._cw._(entity.cw_adapt_to('IWorkflowable').state)
        title = xml_escape(u'%s - %s' % (entity.dc_title(), state))
        self.w(u'<h1><span class="etype">%s</span> %s</h1>'
               % (entity.dc_type().capitalize(), title))

    def render_entity_attributes(self, entity):
        _ = self._cw._
        self.w(u'%s: %s %s %s' % (_('total'), entity.euro_total(),
                                  _('including taxes'), entity.euro_taxes()))
        rset = self._cw.execute('Any EID,T,ET,EA,EC,C,GROUP_CONCAT(CCL),CL '
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
    __select__ = is_instance('Refund',)

    def render_entity_title(self, entity):
        state = self._cw._(entity.cw_adapt_to('IWorkflowable').state)
        title = xml_escape(u'%s - %s' % (entity.dc_title(), state))
        self.w(u'<h1><span class="etype">%s</span> %s</h1>'
               % (entity.dc_type().capitalize(), title))

    def render_entity_attributes(self, entity):
        _ = self._cw._
        self.field(_('account to refund'),
                   entity.paid_by_accounts()[0].view('oneline'), tr=False)
        self.field(_('total'), entity.total, tr=False)
        if entity.payment_date:
            self.field('payment_date', entity.printable_value('payment_date'))
        if entity.payment_mode:
            self.field('payment_mode', xml_escape(entity.payment_mode))
        rset = self._cw.execute('Any E,ET,EC,EA WHERE X has_lines E, X eid %(x)s, '
                                'E title ET, E currency EC, E amount EA',
                                {'x': entity.eid})
        self.wview('table', rset, displayfilter=True)


try:
    from cubes.expense.pdfgen.writers import PDFWriter
    has_reportlab = yes()
except ImportError:
    has_reportlab = yes(0)

# use the has_reportlab selector trick to have them in the registry anyway
# and avoid for instance i18n messages removing due to missing reportlab

class PDFAction(action.Action):
    __regid__ = 'pdfaction'
    __select__ = has_reportlab & one_line_rset() & is_instance('Expense','Refund')

    title = _('generate pdf document')
    category = 'mainactions'

    def url(self):
        return self.cw_rset.get_entity(self.cw_row or 0, self.cw_col or 0).absolute_url(vid='pdfexport')


class PdfExportView(EntityView):
    __regid__ = 'pdfexport'
    __select__ = has_reportlab & one_line_rset() & is_instance('Refund', 'Expense')

    title = _('pdf export')
    content_type = 'application/pdf'
    templatable = False
    binary = True

    def cell_call(self, row, col):
        # import error to avoid import error if reportlab isn't available
        _ = self._cw._
        writer = PDFWriter(self._cw.vreg.config)
        entity = self.cw_rset.get_entity(row, col)
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

