add_attribute('ExpenseLine', 'taxes_exchange_rate')
rql('SET E taxes_exchange_rate TR WHERE E is ExpenseLine, E exchange_rate TR')

checkpoint()
