# -*- coding: iso-8859-15 -*-

"""
Fresh PDF writing library package. This package is based on ReportLab PDF
library, and specifically on platypus (see ReportLab documentation for
details).
"""

# The only class that have to be used for generating PDFs. Just instantiate
# the class:
#     wrt = PDFWriter(company_data)
# and then:
#     wrt.write(entity,output)

from cubicweb_expense.pdfgen.writers import PDFWriter  # noqa: F401
