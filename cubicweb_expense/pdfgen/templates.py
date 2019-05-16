# -*- coding: iso-8859-15 -*-

"""
Library package containing the definition of template classes (page template
and document template) used in the PDF generation with ReportLab platypus.
These classes are derived from platypus standard classes but are specific to
the Fresh application. The page template draw the static content in the
PDF documents.
"""

from reportlab import Version as reportlab_version

from reportlab.lib.units import cm

from reportlab.lib.utils import ImageReader
from reportlab.platypus import PageTemplate, BaseDocTemplate, Frame

from logilab.mtconverter import xml_escape

_ = unicode


class FreshPageTemplate(PageTemplate):
    """
    Class defining the page template used to draw the pages of the PDF documents
    generated by Fresh (Expense and Refund). This page template has a main frame
    that will be filled with the entities data, and draws various other elements
    as the logo and the header that are displayed identically on each page
    (static content).
    """

    def __init__(self, doc_type, company_data, template_id="", _=unicode):
        """
        Instanciates a FreshPageTemplate.

        doc_type: string. type of the document. Can be "refund"
                  (Refund) or "expense" (Expense).
        company_data: {'':u"", }. dictionnary containing data about the
                      company (logo filename, company address, etc.)
        template_id: string. id of the page template.
        """
        # Defines the main frame in which the expenses data will be displayed
        main_f = Frame(1*cm, 1*cm, 19*cm, 23.9*cm,
                       leftPadding=0*cm, bottomPadding=0*cm,
                       rightPadding=0*cm, topPadding=0*cm)

        self.company_data = company_data
        self.doc_type = doc_type
        self._ = _

        PageTemplate.__init__(self, id=template_id, frames=[main_f])


    def beforeDrawPage(self, canvas, document) :
        """
        Overrides the method called before drawing on a new page of the PDF
        document. This method draws various static data on the page
        (logo, company address, header, page number).

        canvas: Canvas. Reportlab canvas that the PDF objects are drawn in.
        document: BaseDocTemplate. Reportlab document template.
        """
        # saves canvas state
        canvas.saveState()

        self.draw_static_content(canvas, document)

        # Puts back the canvas in its previous state
        canvas.restoreState()


    def draw_static_content(self, canvas, document) :
        """
        Draws on the PDF page the static content that is displayed on all
        pages, i.e. logo, company address, header, page number.

        canvas: Canvas. Reportlab canvas that the PDF objects are drawn in.
        document: BaseDocTemplate. Reportlab document template.
        """
        _ = self._
        # Here we don't use a Frame and the platypus machinery because we want
        # to draw various elements that are absolutely positioned. Moreover,
        # with platypus, we can't draw an image (logo) that is left-aligned.

        # rectangle around the header
        canvas.setLineWidth(0.05*cm)
        canvas.rect(1*cm,28.7*cm,19*cm,-3.3*cm,stroke=1,fill=0)

        # company logo
        try:
            logo = ImageReader(self.company_data["logo-filename"])
            if reportlab_version >= "2.1" and reportlab_version <= "2.3":
                canvas.drawImage(logo, 1.2*cm, 28.5*cm, 5*cm, 2.5*cm,
                               preserveAspectRatio=True, anchor="nw")
            else:
                # Old version of reportlab. must compute the height and width
                # of the image. draws the image from the southwest corner.
                # 2.4 Version has the same problem!
                img_width,img_height = logo.getSize()
                ratio = img_width / img_height
                if ratio >= 5/2.5:
                    width = 5*cm
                    height = 5*cm / ratio
                else:
                    width = ratio * 2.5*cm
                    heigth = 2.5*cm
                canvas.drawImage(logo, 1.2*cm, 28.5*cm-height, width, height)
        except IOError:
            # Unable to read logo filename
            canvas.setFont("Helvetica",12)
            str_data = xml_escape( self.company_data["company-name"] )
            canvas.drawString(1.2*cm,28*cm,str_data)

        canvas.setFont("Helvetica",8)

        # page number
        str_data = _(u"Page") + _(u": ") + u"%d" %document.page
        canvas.drawRightString(19.8*cm,28.2*cm,str_data)

        # company address
        str_data = _(u"Est.") + _(u": ") \
        + self.company_data["company-address"]
        self.draw_string_in_width(canvas,str_data,1.2*cm,25.6*cm,9.5*cm)

        # company official ID number
        str_data = _(u"Official ID num") + _(u": ") \
        + self.company_data["company-offnum"]
        self.draw_string_in_width(canvas,str_data,11.2*cm,25.6*cm,5*cm)

        # company activity number
        str_data = _(u"Activity num") + _(u": ") \
        + self.company_data["company-actnum"]
        self.draw_string_in_width(canvas,str_data,16.7*cm,25.6*cm,3.5*cm)

        # title depending on document type
        title = u""
        if self.doc_type == "refund":
            title = _(u"Refund Document").upper()
        elif self.doc_type == "expense":
            title = _(u"Expense Document").upper()
        canvas.setFont("Helvetica-Bold",14)
        canvas.drawCentredString(14.2*cm,27.2*cm,title)

        # preamble remark
        canvas.setFont("Helvetica-Oblique",9)
        canvas.drawCentredString(14.2*cm,26.7*cm,
              _(u"All the amounts are displayed in Euros, except if specified"))


    def draw_string_in_width(self,canvas,string,x,y,width):
        """
        In a canvas, draws a string from the x,y position and within the
        specified width. If the value is too large, the string
        is truncated in order to keep it into the specified width. Therefore,
        the string is drawned between the positions (x,y) and (x+width,y).
        This method gently adds "..." at the end of the truncated string.

        canvas: Canvas. Reportalb canvas that the strings are drawn in
        string: unicode string. string to be drawn in the canvas
        x: float. horizontal position that the string is drawn from
        y: float. vertical position that the string is drawn on
        width: float. maximum width of the string.
        """
        if reportlab_version >= "2.1":
            str_width = canvas.stringWidth(string)
        else:
            # Old version of reportlab library. must provide font informations
            str_width = canvas.stringWidth(string,canvas._fontname,
                                           canvas._fontsize)
        if str_width > width :
            string = string+u"..."
            str_width = canvas.stringWidth(string)
            while str_width > width :
                string = string[:-4]+u"..."
                str_width = canvas.stringWidth(string)
        canvas.drawString(x,y,string)



class FreshDocTemplate(BaseDocTemplate) :
    """
    The Fresh document template is a class explaining how to create a PDF
    document for the Fresh application (Expense or Refund). It uses
    the FreshPageTemplate.
    """

    def __init__(self, output, doc_type, company_data, _=unicode):
        """
        Instanciates a FreshDocTemplate.
        output: string or output flow. name of the PDF output file or
                writable flow where to write the PDF output

        doc_type: string. type of the document that can be "refund"
                  (Refund) or or "expense" (Expense).
        company_data: {'':u"", }. dictionnary containing various data about
                      the company.
        """
        # Initializes the document template with the correct page templates
        templates = [ FreshPageTemplate(doc_type, company_data,
                                        template_id="Pages", _=_) ]
        BaseDocTemplate.__init__(self, output, pageTemplates=templates,
                                 allowSplitting=1)

        if doc_type == "refund":
            self.title = _(u"Refund Document")
        elif doc_type == "expense":
            self.title = _(u"Expense Document")
        else:
            self.title = u""
        self.author = company_data['company-name']
