draft = add_state(_('draft'), 'Expense', initial=True)
submitted = rql('Any S WHERE S is State, S name "submitted", S state_of E, E name "Expense"')[0][0]
add_transition(_('submit'), 'Expense', (draft,), submitted)
