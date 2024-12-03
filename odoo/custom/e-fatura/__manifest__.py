# __manifest__.py
{
    'name': 'E-Fatura Entegrasyonu',
    'version': '1.0',
    'summary': 'E-Fatura Modülü API Tetikleyici',
    'icon': '/e-fatura/static/description/invoice.png',
    'author': 'Your Name',
    'category': 'Accounting',
    'depends': ['account', 'web'],
    'data': [
        'security/ir.model.access.csv',

        'views/account_move_view.xml',
        'views/invoice_template_view.xml',
        'views/invoice_menu_view.xml',
        'views/invoice.xml',
        'views/gelen_account_move_view.xml',
        'views/res_config_settings_views.xml',

        'wizard/account_move_wizard.xml',
    ],
    'installable': True,
    'application': True,
    'assets': {
        'web.assets_backend': [
            'e-fatura/static/src/components/*/*.js',
            'e-fatura/static/src/components/*/*.xml',
            'e-fatura/static/src/components/*/*.scss',
        ],
    }
}
