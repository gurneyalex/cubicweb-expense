"""cubicweb-expense application package

yo
"""

try:
    from cubicweb import server
    # server part not installed
    server.ON_COMMIT_ADD_RELATIONS.add('has_lines')
except ImportError:
    pass
