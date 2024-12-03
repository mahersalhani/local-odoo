from odoo import models, fields

class TestPricing(models.Model):
    _name = 'hospital.test.pricing'
    _description = 'Test Fiyatlandırması'

    test_id = fields.Many2one('hospital.lab.test', string='Test', required=True)
    price = fields.Float(string='Fiyat', required=True)
    notes = fields.Text(string='Notlar')