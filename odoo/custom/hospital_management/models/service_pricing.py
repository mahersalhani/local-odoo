from odoo import models, fields

class ServicePricing(models.Model):
    _name = 'hospital.service.pricing'
    _description = 'Hizmet Fiyatlandırması'

    service_name = fields.Char(string='Hizmet Adı', required=True)
    price = fields.Float(string='Fiyat', required=True)
    notes = fields.Text(string='Notlar')