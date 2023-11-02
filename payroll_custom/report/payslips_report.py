from odoo import models, fields, api


class PayslipsReport(models.AbstractModel):
    #  _name = Use prefix `report.` along with `module_name.report_name`
    _name = 'report.payroll_custom.payslips_report_view'

    @api.model
    def _get_report_values(self, docids, data=None):

        start_date = data['form']['start_date']
        end_date = data['form']['end_date']
        employees = data['form']['employee_ids']
        payslips = data['payslips']
        docs = []
        for employee in employees:
            base = 0
            gross = 0
            net = 0
            allow = 0
            emp = self.env['hr.employee'].search([('id', '=', employee)])
            for p in payslips:

                if p['employee_id'][0] == employee:
                    for line in p['line_ids']:
                        l = self.env['hr.payslip.line'].search([('id', '=', line)])
                        if l.code == "BASIC":
                            base += l.total
                        if l.code == "NET":
                            net += l.total
                        if l.code == "GROSS":
                            gross += l.total
                        if l.code == "ALW":
                            allow += l.total
            docs.append({
                'employee_name': emp.name,
                'basic': base,
                'net': net,
                'gross': gross,
                'allow': allow
            })
        print("docs", docs)

        return {
            'start_date': start_date,
            'end_date': end_date,
            'employees': len(employees),
            'docs': docs,
        }
