import json
from odoo import http
from odoo.http import request

class CarRentalController(http.Controller):
    # @http.route(['/vehicles/rental'], type='http', auth="public", website=True)
    # def list_car_rental_contracts(self, **kwargs):
    #     print('list_car_rental_contracts')

    #     vehicle_ids = (
    #         request.env["fleet.vehicle"]
    #         .sudo()
    #         .search([('rental_check_availability','=',True),('state_id.name','!=','Inactive')])
    #     )

    #     return request.render('fleet_rental.template_vehicle_rental_list', {
    #         'vehicles': vehicle_ids
    #     })

    @http.route('/vehicle/rental/submit', type='http', auth='public', methods=['POST'])
    def create_car_rental_contract(self, customer_name, customer_email, customer_phone, vehicle_id, rent_start_date, rent_end_date, **kwargs):
        print('create_car_rental_contract')

        # Validate required fields
        if not customer_name or not customer_email or not vehicle_id or not rent_start_date or not rent_end_date:
            return {'error': 'Missing required parameters'}
        
        try:
            # Step 1: Create or find the customer
            customer = request.env['res.partner'].sudo().search([('email', '=', customer_email)], limit=1)

            if not customer:
                # Create the customer if it doesn't exist
                customer = request.env['res.partner'].sudo().create({
                    'name': customer_name,
                    'email': customer_email,
                    'phone': customer_phone,
                })
            
            # Step 2: Create the car rental contract with the customer
            contract = request.env['car.rental.contract'].sudo().create({
                'customer_id': customer.id,
                'vehicle_id': vehicle_id,
                'rent_start_date': rent_start_date,
                'rent_end_date': rent_end_date,
                'state': 'draft',
                'cost_frequency': 'no',
                'cost': 0.00,
                'first_payment': 0.00,
            })
            
            return request.redirect('/vehicle/rental/confirmation')
        
        except Exception as e:
            return {'error': str(e)}

    @http.route('/vehicle/rental/<int:vehicle_id>', type='http', auth="public", website=True, methods=['GET'])
    def list_car_rental(self, vehicle_id, **kwargs):
        vehicle = (
            request.env["fleet.vehicle"]
            .sudo()
            .search([('rental_check_availability','=',True),('state_id.name','!=','Inactive'), ('id','=',vehicle_id)])
        )


        return request.render('fleet_rental.template_vehicle_rental_form', {
            'vehicle': vehicle
        })

    @http.route(['/vehicle/rental/confirmation'], type='http', auth="public", website=True)
    def vehicle_booking_confirmation(self, **kwargs):
        return request.render('fleet_rental.vehicle_booking_confirmation')

    @http.route(['/rental'], type='http', auth="public", website=True)
    def vehicle_booking_confirmation2(self, model_id=None, **kwargs):
        vehicle_ids = (
            request.env["fleet.vehicle"]
            .sudo()
            .search(
                    [
                        ('rental_check_availability','=',True),
                        ('state_id.name','!=','Inactive'), 
                        model_id and ('model_id.id', '=', model_id) or (True, '=', True)
                    ]
                )
        )

        # fleet.vehicle.model
        vehicle_model_ids = (
            request.env["fleet.vehicle.model"]
            .sudo()
            .search([('vehicle_type', '=', 'car')])
        )

        return request.render('fleet_rental.template_vehicle_rental_list', {
            'model_id': model_id,
            'vehicles': vehicle_ids,
            'vehicle_models': vehicle_model_ids
        })
