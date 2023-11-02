{
    'name': 'FleetCustom',
    'depends': [
        'fleet', 'account', 'base_address_extended', 'mail'
    ],
    'data': [
        'security/ir.model.access.csv',

        'data/book_sequence.xml',
        'data/rent_service.xml',

        'views/fleet_vehicle_book_views.xml',
        'views/fleet_vehicle_views.xml',



    ],
    'installable': True,
    'application': True
}