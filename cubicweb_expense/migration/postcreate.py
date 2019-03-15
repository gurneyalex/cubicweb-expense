# expense workflow

from cubicweb import _

wf = add_workflow(_('expense workflow'), 'Expense')
draft = wf.add_state(_('draft'), initial=True)
submitted = wf.add_state(_('submitted'))
accepted = wf.add_state(_('accepted'))
wf.add_transition(_('accept'), submitted, accepted,
                  requiredgroups=('managers',))
wf.add_transition(_('submit'), draft, submitted)

# refund workflow
wf = add_workflow(_('refund workflow'), 'Refund')
preparation = wf.add_state(_('preparation'), initial=True)
paid = wf.add_state(_('paid'))
pay = wf.add_transition(_('pay'), preparation, paid)
