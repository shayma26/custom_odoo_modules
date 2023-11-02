# -*- coding: utf-8 -*-
from odoo import models


class ApiDataXlsx(models.AbstractModel):
    _name = 'report.odoo_connect.api_data_report_xls_view'
    _inherit = 'report.report_xlsx.abstract'
    _description = 'Xlsx report generation'

    def generate_xlsx_report(self, workbook, data, api_line_id):
        sheet = workbook.add_worksheet(api_line_id.description)
        header_bold_style = workbook.add_format(
            {'bold': True, 'align': 'center', 'border': 2})
        body_style = workbook.add_format(
            {'text_wrap': True, 'border': 2})
        header = api_line_id.fields_ids.mapped('name')
        header.insert(0, 'id')
        result = self.env[api_line_id.model_id.model].search([]).read(header)
        sheet.set_column(0, len(header) - 1, 18)

        row = 0
        for i in range(len(header)):
            sheet.write(row, i, header[i], header_bold_style)

        for record in result:
            row += 1
            for i in range(len(header)):
                rec_field = self.env['ir.model.fields'].search(
                    [('name', '=', header[i]), ('model', '=', api_line_id.model_id.model)])
                value = record[header[i]]
                if rec_field.ttype == 'many2one':
                    value = record[header[i]][1] if record[header[i]] else ""
                elif rec_field.ttype == 'many2many' or rec_field.ttype == 'one2many':
                    value = ', '.join(self.env[rec_field.relation].browse(record[header[i]]).mapped('name'))
                sheet.write(row, i, value, body_style)
