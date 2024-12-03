import logging
from odoo import http
from odoo.http import request
import requests

class EFaturaFetchController(http.Controller):

    @http.route(['/e_fatura/invoices', 
                '/e_fatura/invoices/page/<int:page>'],
                type='http', auth='user')
    def fetch_invoices(self, page=1, **kwargs):
        url = "http://efatura-test.uyumsoft.com.tr/api/BasicIntegrationApi"  # Harici API URL'si

        if page < 1:
            return request.redirect('/e_fatura/invoices/page/1')

        json = {
            "Action": "GetInboxInvoiceList",
            "parameters": {
                "userInfo": {
                    "Username": "Uyumsoft",
                    "Password": "Uyumsoft"
                },
                "query": {
                    "CreateStartDate": "2020-08-30T23:59:59.999",
                    "CreateEndDate": "2020-09-04T23:59:59.999",
                    "PageIndex": page - 1,
                }
            }
        }
        
        response = requests.post(url, json=json)
        data, total_count, total_pages = [], 0, 0

        if response.status_code == 200:
            response_data = response.json()
            if response_data.get('Data', {}).get('Value', {}).get('Items'):
                data = response_data['Data']['Value']['Items']
                total_count = response_data['Data']['Value']['TotalCount']
                total_pages = response_data['Data']['Value']['TotalPages'] + 1

            previous_page = str(max(1, page - 1))
            next_page = str(min(total_pages, page + 1))
            page_range = range(page - 1, min(total_pages, page + 1) + 1)
            
            if page == 1:
                page_range = range(page, min(total_pages, page + 2) + 1)
            if page == total_pages:
                page_range = range(max(1, page - 2), page + 1)

        return request.render('e-fatura.api_data_template', {
            'data': data,
            'page_index': page,
            'total_count': total_count,
            'total_pages': total_pages,
            'previous_page': previous_page,
            'next_page': next_page,
            'page_range': page_range,
        })

    def create_invoice(self, invoice_data):
        """
        API'den gelen fatura verilerini Odoo'da oluşturur.
        """
        invoice = request.env['account.move'].sudo().create({
            'name': invoice_data.get('InvoiceId'),
            'external_invoice_id': invoice_data.get('DocumentId'),
            'amount_untaxed_signed': invoice_data.get('TaxExclusiveAmount'),
            'amount_total_signed': invoice_data.get('PayableAmount'),
            'tax_total': invoice_data.get('TaxTotal'),
            'invoice_date': invoice_data.get('CreateDateUtc'),
            'is_efatura': True,
            'target_tckn_vkn': invoice_data.get('TargetTcknVkn'),
            'target_title': invoice_data.get('TargetTitle'),
            'create_date_utc': invoice_data.get('CreateDateUtc'),
            'execution_date': invoice_data.get('ExecutionDate'),
            'document_currency_code': invoice_data.get('DocumentCurrencyCode'),
        })
        return invoice
