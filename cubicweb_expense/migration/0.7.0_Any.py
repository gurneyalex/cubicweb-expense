change_relation_props('Expense', 'title', 'String', fulltextindexed=True)
change_relation_props('ExpenseLine', 'title', 'String', fulltextindexed=True)

add_cube('file')
add_relation_definition('Expense', 'has_attachment', 'File')
add_relation_definition('ExpenseLine', 'has_attachment', 'File')
