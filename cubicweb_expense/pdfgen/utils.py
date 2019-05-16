# -*- coding: iso-8859-15 -*-

"""
Library package containing the definition of useful text formatting
functions.
"""


def format_number(number, digits=2):
    """
    Function that formats a number to be written in the PDF document. It uses
    the separating characters for numbers defined in the localized
    dictionnary

    number: float or int. number to be formatted.
    digits: int. number of digits to be displayed ('number' is rounded if it
            has more digits).
    Returns: unicode string.
    """
    str_mask = u"%%.%df" % digits
    # str_num contains the string representation of 'number' rounded with
    # 'digits' digits.
    str_num = str_mask % number

    # gets the integer string
    str_int = str_num.split('.')[0]

    # passes through the integer string (in reverse order) and adds thousands
    # separator when needed
    result_int = u""
    count = 0
    for char in str_int[::-1]:
        if char in '0123456789':
            if count != 0 and count % 3 == 0:
                # result_int = _(u"thousands sep") + result_int
                result_int = u'\u00a0%s' % result_int
            result_int = char + result_int
            count += 1
        elif char in '+-':
            result_int = u'%s\u00a0%s' % (char, result_int)

    result_int = u" ".join(result_int.split())

    if digits == 0:
        formatted_num = result_int
    else:
        formatted_num = u'%s,%s' % (result_int, str_num.split('.')[1])
    return formatted_num
