# -*- coding: iso-8859-15 -*-

"""
Library package containing the styles used in the PDF generation with
ReportLab platypus.
"""

from reportlab.lib.units import cm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT

STANDARD_FONT_SIZE = 9.0

# Defining paragraph styles used in PDF generation

style_metadata = ParagraphStyle("metadata")
style_metadata.fontSize = STANDARD_FONT_SIZE
style_metadata.leading = STANDARD_FONT_SIZE * 1.2
style_metadata.fontName = "Helvetica"
style_metadata.alignment = TA_LEFT
style_metadata.firstLineIndent = -0.5 * cm
style_metadata.leftIndent = 0.5 * cm

style_ids = ParagraphStyle("ids")
style_ids.fontSize = STANDARD_FONT_SIZE * 0.8
style_ids.leading = STANDARD_FONT_SIZE * 0.8 * 1.2
style_ids.fontName = "Helvetica"
style_ids.alignment = TA_LEFT

style_address = ParagraphStyle("address")
style_address.fontSize = STANDARD_FONT_SIZE * 1.2
style_address.leading = STANDARD_FONT_SIZE * 1.2 * 1.2
style_address.fontName = "Helvetica"
style_address.alignment = TA_LEFT
style_address.firstLineIndent = -0.5 * cm
style_address.leftIndent = 0.5 * cm

style_table_header = ParagraphStyle("table_header")
style_table_header.fontSize = STANDARD_FONT_SIZE
style_table_header.leading = STANDARD_FONT_SIZE * 1.1
style_table_header.fontName = "Helvetica"
style_table_header.alignment = TA_CENTER

style_table_data = ParagraphStyle("table_data")
style_table_data.fontSize = STANDARD_FONT_SIZE
style_table_data.leading = STANDARD_FONT_SIZE * 1.1
style_table_data.fontName = "Helvetica"
style_table_data.alignment = TA_LEFT
style_table_data.firstLineIndent = -0.2 * cm
style_table_data.leftIndent = 0.2 * cm

style_table_data_num = ParagraphStyle("table_data_num")
style_table_data_num.fontSize = STANDARD_FONT_SIZE
style_table_data_num.leading = STANDARD_FONT_SIZE * 1.1
style_table_data_num.fontName = "Helvetica"
style_table_data_num.alignment = TA_RIGHT
