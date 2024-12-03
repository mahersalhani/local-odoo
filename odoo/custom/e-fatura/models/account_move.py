import logging
import requests
import json
from odoo import models, fields, api
from datetime import datetime
from odoo.exceptions import ValidationError, UserError

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'

    is_efatura = fields.Boolean('E-Fatura mı?', default=False)
    external_invoice_id = fields.Char(string="External Invoice ID", index=True)
    target_tckn_vkn = fields.Char(string="Alıcı TCKN/VKN")
    name_surname = fields.Char(string="Müşteri Adı Soyadı")
    supplier_name = fields.Char(string="Müşteri Adı Soyadı")
    supplier_lastname = fields.Char(string="Müşteri Adı Soyadı")
    target_title = fields.Char(string="Şirket Bilgisi")
    create_date_utc = fields.Datetime(string="Oluşturulma Tarihi")
    taxed_number = fields.Datetime(string="VKN")
    mersis_number = fields.Datetime(string="MERSISNO")
    account_number = fields.Datetime(string="TICARETSICILNO")
    execution_date = fields.Datetime(string="İcra Tarihi")
    tax_total = fields.Float(string="Toplam Vergi")
    amount_untaxed_signed = fields.Float(string="Vergisiz Tutar")
    amount_total_signed = fields.Float(string="Toplam Tutar")
    document_currency_code = fields.Many2one('res.currency', string="Para Birimi", required=True)
    country_id = fields.Many2one('res.country', string="Ülke")
    city = fields.Char(string="Şehir")
    room = fields.Char(string="Oda No")
    district = fields.Char(string="Mahalle/İlçe")
    town = fields.Char(string="Kasaba/Köy")
    postal_code = fields.Char(string="Posta Kodu")
    building_name = fields.Char(string="Bina Adı")
    building_no = fields.Char(string="Bina Kapı No")
    street = fields.Char(string="Cadde/Sokak")
    customer_country_id = fields.Many2one('res.country', string="Ülke")
    customer_city = fields.Char(string="Şehir")
    customer_room = fields.Char(string="Oda No")
    customer_district = fields.Char(string="Mahalle/İlçe")
    customer_town = fields.Char(string="Kasaba/Köy")
    customer_postal_code = fields.Char(string="Posta Kodu")
    customer_building_name = fields.Char(string="Bina Adı")
    customer_building_no = fields.Char(string="Bina Kapı No")
    customer_street = fields.Char(string="Cadde/Sokak")
    customer_tckn_vkn = fields.Char(string="Cadde/Sokak")
    phone = fields.Char(string="Telefon")
    fax = fields.Char(string="Fax")
    email = fields.Char(string="E-Posta")
    trade_registry_no = fields.Char(string="Ticari Sicil No")
    efatura_data = fields.Text(string="E-Fatura JSON", readonly=True)
    invoice_type = fields.Selection([
        ('SATIS', 'Satış'),
        ('ALIS', 'Alış')
    ], string="Fatura Tipi", required=True, default="SATIS")
    tax_total = fields.Monetary(string="Toplam Vergi", compute='_compute_tax_total')
    amount_untaxed_signed = fields.Monetary(string="Vergisiz Toplam", compute='_compute_untaxed_total')
    amount_total_signed = fields.Monetary(string="Toplam Tutar", compute='_compute_total')
    product_line_ids = fields.One2many('account.move.line.product', 'move_id', string="Ürün Bilgileri")
    amount_total_signed = fields.Monetary(string="Toplam Tutar", compute="_compute_total", readonly=False)
    issue_date = fields.Date(string="Fatura Tarihi")
    customer_tax_adress = fields.Char(string="Vergi Dairesi Adı")

    @api.depends('product_line_ids')
    def _compute_tax_total(self):
        for record in self:
            # Vergi toplamını hesapla
            record.tax_total = sum(line.tax_total for line in record.product_line_ids)
            
    @api.depends('product_line_ids')
    def _compute_untaxed_total(self):
        for record in self:
            # Vergisiz toplamı hesapla
            record.amount_untaxed_signed = sum(line.subtotal for line in record.product_line_ids)
            
    @api.depends('amount_untaxed_signed', 'tax_total')
    def _compute_total(self):
        for record in self:
            # Toplam tutarı hesapla
            record.amount_total_signed = record.amount_untaxed_signed + record.tax_total

    def open_address_form(self):
        """
        Adres ve Fatura Bilgileri formunu açan işlem.
        """
        return {
            'type': 'ir.actions.act_window',
            'name': 'Adres ve Fatura Bilgileri',
            'view_mode': 'form',
            'res_model': 'account.move',
            'res_id': self.id,
            'target': 'new',
        }

    def open_product_form(self):
        """
        Ürün Bilgileri formunu açan işlem.
        """
        return {
            'type': 'ir.actions.act_window',
            'name': 'Ürün Bilgileri',
            'view_mode': 'form',
            'res_model': 'account.move.line.product',
            'target': 'new',
        }

    def check_required_fields(self):
        """
        Eksik zorunlu alanları kontrol eder ve liste halinde döner.
        """
        required_fields = {
            'country_id': _("Ülke"),  # Zorunlu
            'city': _("Şehir"),       # Zorunlu
            'district': _("Mahalle/İlçe"),  # Zorunlu
            'target_title': _("Alıcı Ünvanı"),
            'target_tckn_vkn': _("Alıcı TCKN/VKN"),
            'invoice_type': _("Fatura Tipi"),  # Zorunlu
            'document_currency_code': _("Para Birimi"),
            'create_date_utc': _("Oluşturulma Tarihi"),
            'external_invoice_id': _("Dış Fatura ID"),
            'name_surname': _("Müşteri Adı Soyadı"),
            'tax_total': _("Toplam Vergi"),  # Zorunlu
            'amount_untaxed_signed': _("Vergisiz Tutar"),  # Zorunlu
            'amount_total_signed': _("Toplam Tutar"),  # Zorunlu
        }

        missing_fields = []
        for field, label in required_fields.items():
            if not getattr(self, field):
                missing_fields.append(label)

        return missing_fields

    def action_post_efatura(self):
        current_datetime = datetime.now()
        print(current_datetime)
        
        for record in self:
            # missing_fields = record.check_required_fields()
            # if missing_fields:
            #     error_message = _("E-Fatura gönderimi için eksik alanlar: ") + ", ".join(missing_fields)
            #     record.message_post(body=error_message)
            #     continue

            # API anahtarını al
            apiKey = self.env['ir.config_parameter'].sudo().get_param('e_fatura.api_key')

            if not apiKey:
                _logger.error("API anahtarı bulunamadı.")
                raise Exception("API anahtarı bulunamadı.")

            headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + apiKey
            }

            try:
                issue_date = record.create_date_utc or datetime.now()

                data = {
                    "Action": "SendInvoice",
                    "parameters": {
                        "invoices": [
                            {
                                "Invoice": {
                                    "UblVersionId": {"value": "2.1"},
                                    "CustomizationId": {"value": "TR1.2"},
                                    "ProfileId": {"value": "TICARIFATURA"},
                                    "CopyIndicator": {"value": False},
                                    "IssueDate": {"value": issue_date.strftime('%Y-%m-%d')},
                                    "IssueTime": {"value": issue_date.strftime('%H:%M:%S.%f')},
                                    "InvoiceTypeCode": {"value": record.invoice_type},
                                    "Note": [{"value": f"Fatura Notu - {record.external_invoice_id}"}],
                                    "DocumentCurrencyCode": {"value": record.document_currency_code.name},
                                    "LineCountNumeric": {"value": len(record.product_line_ids)},
                                    "OrderReference": {
                                        "Id": {"value": record.external_invoice_id},
                                        "IssueDate": {"value": issue_date.strftime('%Y-%m-%d')},
                                        "IssueTime": {"value": issue_date.strftime('%H:%M:%S.%f')}
                                    },
                                    "AccountingSupplierParty": {
                                        "Party": {
                                            "PartyIdentification": [
                                                {"Id": {"schemeId": "VKN", "value": record.taxed_number}},
                                                {"Id": {"schemeId": "MERSISNO", "value": record.mersis_number}},
                                                {"Id": {"schemeId": "TICARETSICILNO", "value": record.account_number}}
                                            ],
                                            "PartyName": {"Name": {"value": record.target_title}},
                                            "PostalAddress": {
                                                "Room": {"value": record.room},
                                                "StreetName": {"value": record.street},
                                                "BuildingNumber": {"value": record.building_no},
                                                "CitySubdivisionName": {"value": record.district},
                                                "CityName": {"value": record.city},
                                                "Country": {"Name": {"value": record.country_id.name}},
                                            },
                                            "PartyTaxScheme": {
                                                "TaxScheme": {
                                                    "Name": {"value": "KDV"}
                                                }
                                            },
                                            "Person": {
                                                "FirstName": {"value": record.supplier_name},
                                                "FamilyName": {"value": record.supplier_lastname}
                                            }
                                        }
                                    },
                                    "AccountingCustomerParty": {
                                        "Party": {
                                            "PartyIdentification": [
                                                {"ID": {"schemeID": "VKN", "Value": record.customer_tckn_vkn}}
                                            ],
                                            "PartyName": {"Name": {"value": record.name_surname}},
                                            "PostalAddress": {
                                                "Room": {"value": record.customer_room},
                                                "StreetName": {"value": record.customer_street},
                                                "BuildingNumber": {"value": record.customer_building_no},
                                                "CitySubdivisionName": {"value": record.customer_district},
                                                "CityName": {"value": record.customer_city},
                                                "Country": {"Name": {"value": record.customer_country_id.name}},
                                            },
                                            "PartyTaxScheme": {
                                                "TaxScheme": {
                                                    "Name": {"value": record.customer_tckn_vkn}
                                                }
                                            },
                                            "Contact": {
                                                "Telephone": {"value": record.phone}
                                            }
                                        }
                                    },
                                    "TaxTotal": [
                                        {
                                            "TaxAmount": {
                                                "currencyId": record.document_currency_code.name,
                                                "value": record.tax_total
                                            },
                                            "TaxSubtotal": [
                                                {
                                                    "TaxableAmount": {
                                                        "currencyId": record.document_currency_code.name,
                                                        "value": record.amount_untaxed_signed
                                                    },
                                                    "TaxAmount": {
                                                        "currencyId": record.document_currency_code.name,
                                                        "value": record.tax_total
                                                    },
                                                    "Percent": {"value": 18},
                                                    "TaxCategory": {
                                                        "TaxScheme": {
                                                            "Name": {"value": "KDV"}
                                                        }
                                                    }
                                                }
                                            ]
                                        }
                                    ],
                                    "LegalMonetaryTotal": {
                                        "LineExtensionAmount": {
                                            "currencyId": record.document_currency_code.name,
                                            "value": record.amount_untaxed_signed
                                        },
                                        "TaxExclusiveAmount": {
                                            "currencyId": record.document_currency_code.name,
                                            "value": record.amount_untaxed_signed
                                        },
                                        "TaxInclusiveAmount": {
                                            "currencyId": record.document_currency_code.name,
                                            "value": record.amount_total_signed
                                        },
                                        "PayableAmount": {
                                            "currencyId": record.document_currency_code.name,
                                            "value": record.amount_total_signed
                                        }
                                    },
                                    "InvoiceLine": [
                                        {
                                            "Id": {"value": str(i+1)},
                                            "InvoicedQuantity": {"unitCode": "NIU", "value": str(line.quantity)},
                                            "LineExtensionAmount": {
                                                "currencyId": record.document_currency_code.name,
                                                "value": line.subtotal
                                            },
                                            "TaxTotal": {
                                                "TaxAmount": {
                                                    "currencyId": record.document_currency_code.name,
                                                    "value": line.tax_line_ids.amount
                                                }
                                            },
                                            "Item": {
                                                "Description": {"value": line.description or "Açıklama"},
                                                "Name": {"value": line.product_id.name}
                                            },
                                            "Price": {
                                                "PriceAmount": {
                                                    "currencyId": record.document_currency_code.name,
                                                    "value": line.price_unit
                                                }
                                            }
                                        }
                                        for i, line in enumerate(record.product_line_ids)
                                    ],
                                    "EArchiveInvoiceInfo": {
                                        "DeliveryType": "Electronic"
                                    },
                                    "Scenario": 0,
                                    "Notification": {
                                        "Mailing": [
                                            {
                                                "Subject": "Satın aldığınız ürüne ait faturanız.",
                                                "EnableNotification": True,
                                                "To": {"value": record.email},
                                                "Attachment": {
                                                    "Xml": True,
                                                    "Pdf": True
                                                }
                                            }
                                        ]
                                    },
                                    "LocalDocumentId": f"E-FATURA-{record.id:03d}"
                                }
                            }
                        ],
                        "userInfo": {
                            "Username": "Uyumsoft",
                            "Password": "Uyumsoft"
                        }
                    }
                }

                response = requests.post("http://104.247.173.87:8888/api/post/BasicIntegrationApi", json=data, headers=headers)
                response.raise_for_status()
                print(response)
                print(response.status_code)
                print(response.json())

                if response.status_code == 200:
                    record.is_efatura = True

                record.message_post(body="E-Fatura başarıyla gönderildi.")
            except requests.exceptions.RequestException as e:
                # detele the record if the request fails
                record.unlink()

                error_message = f"E-Fatura gönderimi başarısız: {str(e)}"
                record.message_post(body=error_message)
                _logger.error(error_message)

    def action_send_invoice(self):
        """
        Fatura gönderim işlemi: Zorunlu alan kontrolü ve API isteği.
        """
        missing_fields = self.check_required_fields()
        if missing_fields:
            missing_fields_str = ", ".join(missing_fields)
            raise UserError(_("Zorunlu alanları doldurunuz:\n%s") % missing_fields_str)

        # Zorunlu alanlar tamam ise devam et
        try:
            self.sync_invoices()  # Örneğin bir API isteği
        except Exception as e:
            _logger.error(f"Fatura gönderimi sırasında hata: {str(e)}")
            raise UserError(_("Fatura gönderimi sırasında hata oluştu:\n%s") % str(e))

    def action_download_efatura_pdf(self):
        return self.env.ref('account.account_invoices').report_action(self)

    def sync_invoices(self):
        try:
            data = self.fetch_external_invoices()
            if not data:
                _logger.warning("Hiçbir fatura verisi alınamadı.")
                return
            
            invoice_ids = [invoice['DocumentId'] for invoice in data]
            existing_invoices = self.env['account.move'].search([('external_invoice_id', 'in', invoice_ids)])
            existing_invoice_ids = set(existing_invoices.mapped('external_invoice_id'))

            for invoice in data:
                try:

                    # Fetch the currency record
                    currency = self.env['res.currency'].sudo().search([('name', '=', invoice['DocumentCurrencyCode'])], limit=1)
                    all_currencies = self.env['res.currency'].sudo().search([])
                    print(all_currencies[0].name)

                    if not currency:
                        # Create the currency record if it doesn't exist
                        currency = self.env['res.currency'].sudo().create({
                            'name': invoice['DocumentCurrencyCode'],
                            'symbol': invoice['DocumentCurrencyCode'],
                        })


                    create_date_utc = datetime.strptime(invoice['CreateDateUtc'], '%Y-%m-%dT%H:%M:%S.%f') if invoice['CreateDateUtc'] else False
                    execution_date = datetime.strptime(invoice['ExecutionDate'], '%Y-%m-%dT%H:%M:%S') if invoice['ExecutionDate'] else False

                    values = {
                        'is_efatura': True,
                        'amount_untaxed_signed': invoice['TaxExclusiveAmount'],
                        'amount_total_signed': invoice['PayableAmount'],
                        'tax_total': invoice['TaxTotal'],
                        'target_tckn_vkn': invoice['TargetTcknVkn'],
                        'target_title': invoice['TargetTitle'],
                        'create_date_utc': create_date_utc,
                        'execution_date': execution_date,
                        'document_currency_code': currency.id,  # Assign the ID of the currency record
                        'invoice_type': 'SATIS',
                    }

                    if invoice['DocumentId'] in existing_invoice_ids:
                        existing_invoice = existing_invoices.filtered(lambda i: i.external_invoice_id == invoice['DocumentId'])
                        existing_invoice.write(values)
                        _logger.info(f"Var olan fatura güncellendi, DocumentId: {invoice['DocumentId']}")
                    else:
                        self.create({
                            'name': invoice['InvoiceId'],
                            'external_invoice_id': invoice['DocumentId'],
                            **values,
                        })
                        _logger.info(f"Yeni fatura oluşturuldu, DocumentId: {invoice['DocumentId']}")
                except Exception as e:
                    _logger.error(f"Fatura işlenirken hata oluştu: {str(e)}")
                    raise e

            return True
        except Exception as e:
            return e

    def fetch_external_invoices(self):
        url = 'http://104.247.173.87:8888/api/post/BasicIntegrationApi'
        apiKey = self.env['ir.config_parameter'].sudo().get_param('e_fatura.api_key')

        if not apiKey:
            _logger.error("API anahtarı bulunamadı.")
            raise Exception("API anahtarı bulunamadı.")

        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + apiKey
        }
        all_invoices = []
        page_index = 0
        total_pages = 1

        while page_index < total_pages:
            body = {
                "Action": "GetInboxInvoiceList",
                "parameters": {
                    "userInfo": {
                        "Username": "Uyumsoft",
                        "Password": "Uyumsoft"
                    },
                    "query": {
                        "CreateStartDate": "2020-08-30T23:59:59.999",
                        "CreateEndDate": "2020-09-04T23:59:59.999",
                        "PageIndex": page_index
                    }
                }
            }

            try:
                response = requests.post(url, headers=headers, data=json.dumps(body))
                response.raise_for_status()  # HTTP hatalarını yakala
            except requests.RequestException as e:
                _logger.error(f"API bağlantı hatası: {str(e)}")
                raise Exception("API bağlantı hatası: API anahtarınızı ve URL'nizi kontrol edin")

            try:
                data = response.json()
            except json.JSONDecodeError:
                _logger.error(f"API'den dönen yanıt JSON değil: {response.text}")
                break

            if data.get('Data', {}).get('IsSucceded', False):
                invoices = data['Data']['Value']['Items']
                all_invoices.extend(invoices)
                total_pages = data['Data']['Value']['TotalPages']
                page_index += 1
            else:
                _logger.error("API'den veri alınamadı: " + data['Data'].get('Message', 'Bilinmeyen hata'))
                break

        return all_invoices

    @api.model
    def action_sync_invoices(self, context=None):
        try:
            self.sync_invoices()
            return {
                'type': 'ir.actions.client',
                'tag': 'reload',
            }
        except Exception as e:
            _logger.error(f"Fatura senkronizasyonu hatası: {str(e)}")
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Hata',
                    'message': f"Fatura senkronizasyonunda hata: {str(e)}",
                    'type': 'danger',
                }
            }

class AccountMoveLineProduct(models.Model):
    _name = 'account.move.line.product'
    _description = "Ürün Bilgileri"

    move_id = fields.Many2one('account.move', string="Fatura", ondelete='cascade')
    product_id = fields.Many2one('product.product', string="Ürün", required=True)
    description = fields.Char(string="Açıklama")
    quantity = fields.Float(string="Miktar", required=True, default=1.0)
    price_unit = fields.Float(string="Birim Fiyatı", required=True)
    subtotal = fields.Float(string="Ara Toplam", compute="_compute_subtotal", store=True)
    tax_total = fields.Float(string="Vergi Tutarı", store=True)

    @api.depends('quantity', 'price_unit')
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.quantity * line.price_unit


