# controllers/efatura_controller.py

from odoo import http
from odoo.http import request
import requests

class EFaturaAPI(http.Controller):

    @staticmethod
    def send_invoice(invoice):
        url = "https://example.com/api/test"  # API URL'si
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer YOUR_TOKEN'  # Geçerli bir token kullanın
        }
        data = {
            'invoice_number': invoice.name,
            'amount': invoice.amount_total,
            'customer': invoice.partner_id.name,
            'date': invoice.invoice_date.strftime('%Y-%m-%d') if invoice.invoice_date else None,
        }

        # API isteğini yap
        response = requests.post(url, json=data, headers=headers)

        # API yanıtını kontrol et
        if response.status_code == 200:
            return {
                'status': 'success',
                'data': response.json()
            }
        else:
            return {
                'status': 'error',
                'message': 'API isteği başarısız: ' + str(response.status_code)
            }

    @http.route('/e_fatura/faturalar', type='http', auth='public')
    def list_invoices(self, **kwargs):
        invoices = request.env['account.move'].search([('is_efatura', '=', True)])  # E-faturaları getir
        return invoices

    @http.route('/call_kw/account.move/sync_invoices', type='json', auth='user', csrf=False)
    def sync_invoices(self, **kwargs):
        data = request.env['account.move'].sync_invoices()

        if data is not True:
            # Handle the case where data is not True
            return {
                'status': 'field',
                'message': data
            }

        res = {
            'status': 'success',
            'message': 'Faturalar senkronize edildi.'
        }

        return res
