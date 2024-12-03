from odoo import models, fields

class Website(models.Model):
    _inherit = 'website'
    
    mobile_number = fields.Char(string="Mobile Number")
