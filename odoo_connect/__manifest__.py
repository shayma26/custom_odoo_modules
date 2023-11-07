# -*- coding: utf-8 -*-
{
    'name': 'Odoo connect',
    'summary': """
       Odoo Restful Api with JWT bearer token authentication.""",
    'depends': ['base','website','report_xlsx'],
    "maintainers": ["sbidoul"],
    "external_dependencies": {"python": ["pyjwt", "cryptography"]},
    "demo": [],
    'data': [
        'security/ir.model.access.csv',

        'data/jwt_data.xml',

        'views/auth_jwt_validator_views.xml',
        'views/odoo_connect_api_lines_views.xml',
        'views/odoo_connect_api_views.xml',
        'views/odoo_connect_api_menus.xml',
        'views/auth_body_example.xml',
        'views/auth_response_example.xml',
        'views/json_body_example.xml',
        'views/json_response_example.xml',
        'views/odoo_connect_api_documentation_view.xml',

        'reports/api_data_report.xml',

    ],
    'assets': {
        'web.assets_frontend':[
            'odoo_connect/static/src/css/prism.css',
            'odoo_connect/static/src/js/prism.js',
            'odoo_connect/static/src/js/odoo_connect.js',
            'odoo_connect/static/src/css/style.css'
        ]
    },
    'installable': True,
    'application': True,
}
