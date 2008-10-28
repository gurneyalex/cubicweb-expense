# expense workflow
draft = add_state(_('draft'), 'Expense', initial=True)
submitted = add_state(_('submitted'), 'Expense')
accepted = add_state(_('accepted'),  'Expense')
add_transition(_('accept'), 'Expense', (submitted,), accepted,
               requiredgroups=('managers',))
add_transition(_('submit'), 'Expense', (draft,), submitted)

# refund workflow
preparation = add_state(_('preparation'), 'Refund', initial=True)
paid = add_state(_('paid'),  'Refund')
pay = add_transition(_('pay'), 'Refund', (preparation,), paid)
