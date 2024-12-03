from odoo import fields, models, tools

class Vehicle(models.Model):
    _name = 'vehicle.vehicle'
    _description = 'Vehicle'

    name = fields.Char(string='Vehicle Name', required=True)
    vehicle_model = fields.Char(string='Model', required=True)
    vehicle_image = fields.Image(string='Image', max_width=1920, max_height=1920, help='Image of the vehicle')
    show_in_website = fields.Boolean(string='Show in Website', default=False)