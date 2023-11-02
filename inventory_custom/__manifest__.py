{
    'name': 'InventoryCustom',
    'depends': ['stock_account'],
    'data': [
        'wizard/stock_quantity_inherited.xml',
        'reports/valuation_report_template.xml',
        'reports/valuation_report.xml',
    ],

    'installable': True,
    'application': True
}