from odoo import models


class PayslipXlsx(models.AbstractModel):
    _name = 'report.payroll_custom.payslips_report_xls_view'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, payslip):
        payslips = self.env['hr.payslip'].search(
            [('date_from', '<=', payslip.start_date), ('date_to', '>=', payslip.end_date),
             ('employee_id', 'in', payslip.employee_ids.ids), ('state', '=', 'done')])
        total_base = 0
        total_gross = 0
        total_net = 0
        total_alw = 0
        total_total = 0

        sheet = workbook.add_worksheet("Payslips")
        header_bold_style = workbook.add_format(
            {'bold': True, 'bg_color': '#c7307b', 'align': 'center', 'border': 2})
        body_style = workbook.add_format(
            {'text_wrap': True, 'bg_color': '#f3c4db', 'border': 2})
        header = ["Employee", "Base", "Net", "Gross", "Allowance", "Total"]
        sheet.set_column('A:F', 15)  # set the length of the columns A:F
        row = 0

        for i in range(1,7):
            sheet.write(row, i, header[i-1], header_bold_style)

        for employee in payslip.employee_ids:
            total = 0
            for p in payslips:
                if p.employee_id.id == employee.id:
                    base = sum(p.line_ids.filtered(lambda x: x.code == "BASIC").mapped('total'))
                    total_base += base
                    net = sum(p.line_ids.filtered(lambda x: x.code == "NET").mapped('total'))
                    total_net += net
                    gross = sum(p.line_ids.filtered(lambda x: x.code == "GROSS").mapped('total'))
                    total_gross += gross
                    allow = sum(p.line_ids.filtered(lambda x: x.code == "ALW").mapped('total'))
                    total_alw += allow

                    total += base + gross + net + allow
                    total_total += total
                    row += 1
                    sheet.write(row, 1, employee.name, body_style)
                    sheet.write(row, 2, base, body_style)
                    sheet.write(row, 3, net, body_style)
                    sheet.write(row, 4, gross, body_style)
                    sheet.write(row, 5, allow, body_style)
                    sheet.write(row, 6, total, body_style)

        row += 1
        sheet.write(row, 0, "Sub Total", header_bold_style)
        sheet.write(row, 1, row-1, body_style)
        sheet.write(row, 2, total_base, body_style)
        sheet.write(row, 3, total_net, body_style)
        sheet.write(row, 4, total_gross, body_style)
        sheet.write(row, 5, total_alw, body_style)
        sheet.write(row, 6, total_total, body_style)
