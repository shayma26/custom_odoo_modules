from odoo import models, fields, api
from odoo.exceptions import ValidationError


class CreatePayslips(models.TransientModel):
    _name = 'create.payslips'

    employee_ids = fields.Many2many('hr.employee')
    start_date = fields.Date()
    end_date = fields.Date()

    @api.constrains('start_date', 'end_date')
    def _check_period(self):
        for record in self:
            if record.start_date > record.end_date:
                raise ValidationError("The start date cannot be greater than end date")

    def create_payslips_pdf(self):
        payslips = self.env['hr.payslip'].search_read(
            [('date_from', '<=', self.start_date), ('date_to', '>=', self.end_date),
             ('employee_id', 'in', self.employee_ids.ids), ('state','=','done')])
        data = {
            'form': self.read()[0],  # a list of only one item
            'payslips': payslips,
        }
        # ref `module_name.report_id` as reference.
        return self.env.ref('payroll_custom.payslips_report').report_action(self, data=data)

    def create_payslips_xls(self):

        return self.env.ref('payroll_custom.payslips_report_xls').report_action(self)
