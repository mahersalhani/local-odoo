from odoo import http
from odoo.http import request


class Snippets(http.Controller):
    # @http.route('/vehicle_cart/', type='http', auth='public', csrf=False, website=False)
    # @http.route('/explore_vehicle/', type='http', auth='public', website=True, csrf=False)
    # @http.route('/explore_vehicle/', type='json', auth='public', csrf=False)
    @http.route('/vehicle_cart/', type='json', auth='public', website=True)
    def all_vehicles(self):
        vehicles = http.request.env['vehicle.vehicle'].sudo().search([('show_in_website', '=', True)])

        data = []
        
        for vehicle in vehicles:
            data.append({
                'id': vehicle.id,
                'name': vehicle.name,
                'vehicle_model': vehicle.vehicle_model,
                'vehicle_image': vehicle.vehicle_image,
            })

        return data
