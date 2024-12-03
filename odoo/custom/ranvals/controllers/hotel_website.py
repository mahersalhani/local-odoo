from odoo import http
from odoo.http import request
from datetime import datetime

class HotelWebsite(http.Controller):

    @http.route(['/hotel/rooms', '/hotel/rooms/page/<int:page>' ], type='http', auth="public", website=True)
    def hotel_rooms(self, room_type=None, check_in=None, page=1, check_out=None, error=None, **kwargs):
        HotelRoom = request.env['hotel.room']
        rooms = HotelRoom.sudo().search([])
        website = request.website
        pager = None
        ProductTemplate = request.env['product.template']
        room_types = ProductTemplate.sudo().search([('is_room', '=', True)])
        
        if error:
            pager = website.pager(
                url='/hotel/rooms',
                total=0,
                page=page,
                step=9,
                scope=5,
                url_args={}
            )
            if error == 'invalid_dates':
                error = 'Invalid dates. Check-out date must be greater than check-in date.'
                return request.render('ranvals.template_hotel_rooms_1', {
                    'rooms': [],
                    'error': error,
                    'check_in': check_in,
                    'check_out': check_out,
                    'pager': pager,
                    'room_types': room_types,
                    'room_type': room_type
                })
            elif error == 'invalid_check_in':
                error = 'Invalid check-in date. Check-in date must be greater than or equal to current date.'
                return request.render('ranvals.template_hotel_rooms_1', {
                    'rooms': [],
                    'error': error,
                    'check_in': check_in,
                    'check_out': check_out,
                    'pager': pager,
                    'room_types': room_types,
                    'room_type': room_type
                })

        if check_in and check_out:
            if check_in > check_out:
                return request.redirect('/hotel/rooms?error=invalid_dates&check_in=%s&check_out=%s' % (check_in, check_out))
            elif  check_in < datetime.now().strftime('%Y-%m-%d'):
                return request.redirect('/hotel/rooms?error=invalid_check_in&check_in=%s&check_out=%s' % (check_in, check_out))
            
            rooms, total = self._get_available_rooms(check_in, check_out, rooms, page, room_type)
            available_rooms = rooms
            pager = website.pager(
                url='/hotel/rooms',
                total=total,
                page=page,
                step=9,
                scope=5,
                url_args={'check_in': check_in, 'check_out': check_out, 'room_type': room_type},
            )
        else:
            available_rooms = []
            pager = website.pager(
                url='/hotel/rooms',
                total=0,
                page=page,
                step=9,
                scope=5,
                url_args={},
            )


        values = {
            'rooms': available_rooms,
            'check_in': check_in,
            'check_out': check_out,
            'pager': pager,
            'room_types': room_types,
            'room_type': room_type
        }
        return request.render('ranvals.template_hotel_rooms_1', values)

    def _get_available_rooms(self, check_in, check_out, rooms, page=1, room_type=None):
        available_room_ids = []
        for room in rooms:
            bookings = request.env['hotel.book.history'].sudo().search([
                ('room_ids', '=', room.id),
                ('check_in', '<=', check_out),
                ('check_out', '>=', check_in),
                ('state', 'in', ['booked', 'checked_in']),
            ])
            if not bookings:
                available_room_ids.append(room.id)

        if room_type:
            room_type_id = int(room_type)
            # check if room_type_id is valid in available_room_ids if not remove from the list
            available_room_ids = [room_id for room_id in available_room_ids if rooms.sudo().browse(room_id).room_type.id == room_type_id]

        start = (page - 1) * 9
        end = start + 9
        
        # return request.env['hotel.room'].browse(available_room_ids[start:end])
        rooms = request.env['hotel.room'].sudo().browse(available_room_ids[start:end])
        total = len(available_room_ids)

        return rooms, total

    @http.route('/hotel/room/<int:room_id>', type='http', auth="public", website=True)
    def hotel_room_detail(self, room_id, **kwargs):
        room = request.env['hotel.room'].sudo().browse(room_id)
        if not room.exists():
            return request.not_found()
        return request.render('ranvals.template_hotel_room_detail', {
            'room': room
        })


    @http.route(['/hotel/booking'], type='http', auth="public", website=True)
    def hotel_booking_form(self, **kwargs):
        rooms = request.env['hotel.room'].sudo().search([('state', '=', 'available')])
        return request.render('ranvals.hotel_booking_form', {
            'rooms': rooms,
        })

    @http.route(['/hotel/booking/submit'], type='http', auth="public", methods=['POST'], website=True)
    def hotel_booking_submit(self, **post):
        partner = request.env.user.partner_id
        check_in = post.get('check_in')
        check_out = post.get('check_out')
        room_id = int(post.get('room_id'))

        # Create a new booking
        booking = request.env['hotel.book.history'].sudo().create({
            'partner_id': partner.id,
            'check_in': check_in,
            'check_out': check_out,
            'room_ids': [(6, 0, [room_id])],
        })

        return request.redirect('/hotel/booking/confirmation')
    
    @http.route(['/hotel/booking/confirmation'], type='http', auth="public", website=True)
    def hotel_booking_confirmation(self, **kwargs):
        return request.render('ranvals.hotel_booking_confirmation')
