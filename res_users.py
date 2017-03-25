# -*- coding: utf-8 -*-

from openerp.osv import fields, osv
from openerp.tools.translate import _

class res_users(osv.osv):
    _name = "res.users"
    _inherit = "res.users"

    _columns = {
        'is_adresse_ip': fields.char('Adresse IP', help='Adresse IP de cet utilisateur pour lui donner des accès spcécifiques', required=False),
    }


