# -*- coding: iso-8859-15 -*-

"""
Library package containing the definition of the class that can write a PDF
file for Fresh documents (Refund or Expense). The PDF generation uses
ReportLab platypus and is based on specific flow generators and
templates.
"""

from cubicweb_expense.pdfgen.templates import FreshDocTemplate
from cubicweb_expense.pdfgen.flowgenerators import ExpenseFlowGenerator
from cubicweb_expense.pdfgen.flowgenerators import RefundFlowGenerator


class PDFWriter(object):
    """
    Class writing the PDF for the Fresh documents (Refund or Expense). This
    class instanciates a flow generator specific to the kind of document
    (Expense or Refund) that must be written.
    """

    def __init__(self, company_data):
        """
        Instanciates a PDF writer.

        company_data: {'':u"", }. dictionnary containing various data about
                      the company.
        """
        self.company_data = company_data

        # flow generator that can create the PDF content flow of the document.
        self._flow_generator = None  # AbstractFlowGenerator
        # type of document to be generated
        self._doc_type = None  # string "expense" or "refund"

    def __init_flow_generator(self, entity):
        """
        Instanciates the flow generator that will create the PDF flow content
        of the document. The real class of flow generator
        (ExpenseFlowGenerator or RefundFlowGenerator) depends on the class
        of the entity object.

        entity: Entity. Any object of class Refund or Expense.
        """
        if entity.e_schema == 'Refund':
            if self._doc_type != "refund":
                self._doc_type = "refund"
                self._flow_generator = RefundFlowGenerator()
        elif entity.e_schema == 'Expense':
            if self._doc_type != "expense":
                self._doc_type = "expense"
                self._flow_generator = ExpenseFlowGenerator()
        else:
            self._doc_type = None
            self._flow_generator = None

    def write(self, entity, output):
        """
        Writes a PDF document representing the entity object.

        entity: Entity. Any object of class Refund or Expense.
        output: string or output flow. File name or IO flow that the PDF will
                be written in.
        """
        # Initializes a flow generator (whose class depends on the entity type)
        self.__init_flow_generator(entity)

        if self._doc_type is None:
            err_msg = "Entity #%d can not be displayed as a PDF file. "\
                      + "Should be of type \"Refund\" or \"Expense\"." \
                      % entity.eid
            raise Exception(err_msg)

        # Opens the PDF document
        pdf_doc = FreshDocTemplate(output, self._doc_type, self.company_data, entity._cw._)

        # Builds it with the content flow returned by the flow generator
        pdf_doc.build(self._flow_generator.generate_flow(entity))
