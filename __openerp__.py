# -*- coding: utf-8 -*-

{
    'name': 'InfoSaône - Module Odoo CPI-Raspberry pour Plastigray',
    'version': '1.0',
    'category': 'InfoSaône\Plastigray',

    'description': """
InfoSaône - Module Odoo CPI-Raspberry pour Plastigray
===================================================

""",
    'author': 'InfoSaône',
    'maintainer': 'InfoSaône',
    'website': 'http://www.infosaone.com',
    'depends': [],
    'data': [
        "security/is_security.xml",
        "security/ir.model.access.csv",
        "assets.xml",
        "is_cpi_raspberry_view.xml",
        "is_capteur_view.xml",
        "res_users_view.xml",
        "res_company_view.xml",
        "report/is_report_rebuts.xml",
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'images': [],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
