{
    'name': 'SalesCustom',
    'depends':['sale_management','product','account'],
    'data':[
        'views/product_template_views.xml',
        'views/sale_order_view.xml',
        'views/sale_report_view.xml',
        'views/account_move_view.xml'

    ],
    'installable': True,
    'application': True
}