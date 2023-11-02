{
    'name':'Payroll Custom',
    'depends': [
        'om_hr_payroll',
        'report_xlsx'
    ],
    'data':[
        'security/ir.model.access.csv',

        'report/payslips_report_template.xml',
        'report/payslips_report.xml',

        'wizard/payslip_wizard.xml',

        'views/payroll_payslip_views.xml',

    ],
    'installable':True,
    'application': True
}