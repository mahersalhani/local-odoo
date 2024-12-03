{
  'name': 'Ranvals',
  'version': '1.0.2',
  'summary': 'Ranvals custom module',
  'description': '',
  'category': 'Sales',
  'author': 'Ranvals',
  'website': 'https://odoo.ranvals.com',
  'license': 'LGPL-3',
  'depends': [
    "base",
    "mail", 
    "sale_management",
    "purchase", 
    "account",
    "website",
  ],
  'sequence': 0,
  'data': [
    'data/sequence.xml',
    'data/hotel_room_data.xml',
    
    'security/ir.model.access.csv',
    
    'views/room_views.xml',
    'views/product_views.xml',
    'views/amenity_views.xml',
    'views/book_history_views.xml',
    'views/dashboard_views.xml',
    'views/sale_order_views.xml',
    'views/account_move_views.xml',
    'views/form_template.xml',
    'views/template_hotel_rooms.xml',
    'views/vehicle_views.xml',
  
    'views/snippets/explore_vehicle.xml',
    'views/snippets/snippets.xml',

    'report/ir_actions_report_templates.xml',
    
    'views/menu_views.xml',
  ],
  'assets': {
    'web.assets_frontend': [
      "ranvals/static/src/js/explore-vehicle.js",
    ],
    'website.assets_wysiwyg': [
      "ranvals/static/src/js/explore-vehicle-options.js",
    ]
  },
  'installable': True,
  'auto_install': False,
  'application': True,
  'images': [
      'static/description/banner.png',
  ],
}
