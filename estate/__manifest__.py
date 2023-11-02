{
    'name': 'Estate',
    'depends': [
        'base'
    ],
    'data': [
        'security/ir.model.access.csv',

        'views/estate_property_offer_views.xml',
        'views/estate_property_tag_views.xml',
        'views/estate_property_type_views.xml',

        'views/estate_property_views.xml',
        'report/res_users_template.xml',
        'report/estate_property_offer_template.xml',
        'report/estate_property_templates.xml',
        'report/res_users_reports.xml',
        #'report/estate_property_reports.xml',
        'views/estate_menus.xml',
        'views/res_users_views.xml'
    ],
    'installable': True,
    'application': True
}