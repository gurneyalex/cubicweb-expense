from yams.buildobjs import (EntityType, RelationType, SubjectRelation,
                            ObjectRelation, Float, Date, String, RichString)
from cubicweb.schema import (WorkflowableEntityType, RQLConstraint,
                             RRQLExpression, ERQLExpression)

from cubicweb.schemas.base import CWUser

CWUser.add_relation(String(maxsize=32, description=_('social security number')), name='ssnum')
CWUser.add_relation(SubjectRelation('PostalAddress', cardinality='?1', composite='subject'), name='lives_at')


class Expense(WorkflowableEntityType):
    permissions = {'read': ('users', 'managers'),
                   'add': ('users', 'managers'),
                   'update': ('managers', ERQLExpression('X in_state S, NOT S name "accepted"')),
                   'delete': ('managers', ERQLExpression('X in_state S, NOT S name "accepted"')),
                   }
    title = String(maxsize=128, required=True)
    description = RichString(fulltextindexed=True)

    has_lines = SubjectRelation('ExpenseLine', cardinality='+1', composite='subject')
    # workflow : submitted, accepted


class ExpenseLine(EntityType):
    permissions = {'read': ('users', 'managers'),
                   'add': ('users', 'managers'),
                   'update': ('managers', ERQLExpression('E is Expense, E has_lines X, E in_state S, NOT S name "accepted"')),
                   'delete': ('managers', ERQLExpression('E is Expense, E has_lines X, E in_state S, NOT S name "accepted"')),
                   }
    title = String(maxsize=256, required=True)
    diem = Date(required=True)
    type = String(required=True, internationalizable=True,
                  vocabulary=(_('transport'), _('accomodation'), _('food'),
                              _('communication'), _('others')))
    amount = Float(required=True, description=_('total amount including taxes'))
    taxes = Float(required=True, description=_('total tax'))
    taxes_currency = String(required=True, maxsize=10, default=u'EUR')
    taxes_exchange_rate = Float(required=True, default=1.0)

    paid_by = SubjectRelation('PaidByAccount', cardinality='1*')
    paid_for = SubjectRelation('PaidForAccount', cardinality='+*')

    currency = String(required=True, maxsize=30, default=u'EUR')
    exchange_rate = Float(required=True, default=1.0)

class PaidByAccount(EntityType):
    permissions = {'read': ('users', 'managers'),
                   'add': ('managers', ),
                   'update': ('managers',),
                   'delete': ('managers',),
                   }
    label = String(required=True, maxsize=128)
    account = String(maxsize=16)

    associated_to = SubjectRelation('CWUser', cardinality='??')


class PaidForAccount(EntityType):
    permissions = {'read': ('users', 'managers'),
                   'add': ('managers', ),
                   'update': ('managers',),
                   'delete': ('managers',),
                   }
    label = String(required=True, maxsize=128)
    account = String(maxsize=16)


class Refund(WorkflowableEntityType):
    permissions = {'read': ('users', 'managers'),
                   'add': ('managers', ),
                   'update': ('managers',),
                   'delete': ('managers',),
                   }
    payment_date = Date(description=_('payment date'))
    payment_mode = String(maxsize=64, description=_('payment mode'))

    has_lines = SubjectRelation('ExpenseLine', cardinality='+*')
    to_account = SubjectRelation('PaidByAccount', cardinality='1*')
    # workflow : preparation / paid


class has_lines(RelationType):
    # note: The RRQLExpression used will only work when adding ExpenseLines on
    # Expense, and not on refund. ExpenseLines are supposed to be added to
    # Refund automatically via a hook through an unsafe_execute
    permissions = {
        'read' : ('managers', 'users'),
        'add': ('managers', RRQLExpression('S is Expense, S in_state ST, NOT ST name "accepted"')),
        'delete': ('managers', RRQLExpression('S is Expense, S in_state ST, NOT ST name "accepted"')),
        }
