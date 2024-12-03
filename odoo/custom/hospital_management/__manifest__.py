{
    'name': 'Hospital Management',
    'version': '1.0',
    'icon': '/hospital_management/static/description/hospital.png',
    'depends': ['base', 'mail','web'],
    'data': [
        'security/ir.model.access.csv',
        'views/homepage_views.xml',
        'views/hospital_menus.xml',
        'views/appointment_views.xml',
        'views/patient_views.xml',
        'views/health_history_views.xml',
        'views/lab_views.xml',
        'views/access_rights.xml',
        'views/payment_views.xml',
        'views/invoice_views.xml',
        'data/appointment_email_templates.xml',
        'views/menu_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'hospital_management/static/src/css/homepage_style.css',
        ],
    },
    'installable': True,
    'application': True,
}
