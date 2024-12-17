import logging
import requests
import json
from odoo import models, fields, api, _
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError, UserError
from collections import defaultdict

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = "account.move"

    is_efatura = fields.Boolean("E-Fatura mı?", default=False)
    is_giden_efatura = fields.Boolean("Giden E-Fatura mı?", default=False)
    external_invoice_id = fields.Char(string="External Invoice ID", index=True)
    target_tckn_vkn = fields.Char(string="Alıcı TCKN/VKN")
    name_surname = fields.Char(string="Müşteri Adı Soyadı")
    supplier_name = fields.Char(string="Müşteri Adı Soyadı")
    supplier_lastname = fields.Char(string="Müşteri Adı Soyadı")
    supplier_tax_schema = fields.Char(string="Vergi Dairesi Adı")
    target_title = fields.Char(string="Şirket Bilgisi")
    create_date_utc = fields.Datetime(string="Oluşturulma Tarihi")
    taxed_number = fields.Char(string="VKN")
    order_number = fields.Char(string="Sipariş No")
    invoice_note = fields.Char(string="Not")
    mersis_number = fields.Char(string="MERSISNO")
    account_number = fields.Char(string="TICARETSICILNO")
    execution_date = fields.Datetime(string="İcra Tarihi")
    tax_total = fields.Float(string="Toplam Vergi")
    amount_total_signed = fields.Float(string="Toplam Tutar")
    document_currency_code = fields.Many2one(
        "res.currency", string="Para Birimi", required=True
    )
    supplier_country_id = fields.Many2one("res.country", string="Ülke")
    city = fields.Char(string="Şehir")
    room = fields.Char(string="Oda No")
    district = fields.Char(string="Mahalle/İlçe")
    town = fields.Char(string="Kasaba/Köy")
    postal_code = fields.Char(string="Posta Kodu")
    building_name = fields.Char(string="Bina Adı")
    building_no = fields.Char(string="Bina Kapı No")
    street = fields.Char(string="Cadde/Sokak")

    customer_country_id = fields.Many2one("res.country", string="Ülke")
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
    efatura_type = fields.Selection(
        [("EARSIVFATURA", "E-Arşiv Fatura"), ("TEMELFATURA", "Temel Fatura")],
        string="Belge Türü",
        required=True,
        default="EARSIVFATURA",
    )
    invoice_type = fields.Selection(
        [
            ("SATIS", "Satış"),
            ("GENEL_IADE", "Genel İade"),
            ("TEVKIFAT", "Tevkifat"),
            ("TEVKIFAT_IADE", "Tevkifat İade"),
            ("ISTISNA", "İstisna"),
            ("OZEL_MATRAH", "Özel Matrah"),
            ("IHRAC_KAYITLI", "İhrac Kayıtlı"),
            ("KONAKLAMA_VERGISI", "Konaklama Vergisi"),
        ],
        string="Fatura Tipi",
        required=True,
        default="SATIS",
    )
    tax_total = fields.Monetary(
        string="Toplam Vergi", compute="_compute_tax_total")
    amount_untaxed_signed = fields.Monetary(
        string="Vergisiz Toplam", compute="_compute_untaxed_total"
    )
    amount_total_signed = fields.Monetary(
        string="Toplam Tutar", compute="_compute_total"
    )
    product_line_ids = fields.One2many(
        "account.move.line.product", "move_id", string="Ürün Bilgileri"
    )
    amount_total_signed = fields.Monetary(
        string="Toplam Tutar", compute="_compute_total", readonly=False
    )
    issue_date = fields.Date(string="Fatura Tarihi")
    customer_tax_adress = fields.Char(string="Vergi Dairesi Adı")

    e_fatura_present = fields.Selection(
        [
            ("1", "1"),
            ("8", "8"),
            ("10", "10"),
            ("18", "18"),
            ("20", "20"),
        ],
        string="KDV Oranı",
        default="20",
    )

    customer_api_selection = fields.Selection(
        selection=lambda self: self._get_customer_selection(),
        string="Customer (API)",
        required=False
    )

    def _fetch_api_customers(self):
        """Fetch customer data from the API."""
        try:
            customers = [
                {
                    "id": 1,
                    "name": "Ahmet Yılmaz",
                    "country_id": 223,
                    "city": "İstanbul",
                    "street": "Beşiktaş Mah.",
                    "phone": "+90 212 555 5555",
                    "zip": "34353",
                    "property_account_position_id": {"name": "Beşiktaş Vergi Dairesi"}
                },
                {
                    "id": 2,
                    "name": "Ayşe Demir",
                    "country_id": 223,
                    "city": "Ankara",
                    "street": "Kızılay Cad.",
                    "phone": "+90 312 444 4444",
                    "zip": "06000",
                    "property_account_position_id": {"name": "Çankaya Vergi Dairesi"}
                },
                {
                    "id": 3,
                    "name": "Mehmet Kaya",
                    "country_id": 223,
                    "city": "İzmir",
                    "street": "Alsancak Mah.",
                    "phone": "+90 232 222 2222",
                    "zip": "35220",
                    "property_account_position_id": {"name": "Alsancak Vergi Dairesi"}
                }
            ]
            return customers
        except Exception:
            return []

    @api.model
    def _get_customer_selection(self):
        """Return the selection list dynamically."""
        customers = self._fetch_api_customers()
        return [(str(c['id']), c['name']) for c in customers]

    @api.onchange('customer_api_selection')
    def _onchange_customer_api_selection(self):
        """Handle onchange event for selection."""
        if self.customer_api_selection:
            selected_customer = next(
                (c for c in self._fetch_api_customers() if str(
                    c['id']) == self.customer_api_selection),
                None
            )
            if selected_customer:
                # Set other fields based on selected customer if needed
                self.partner_id = self.env['res.partner'].search(
                    [('name', '=', selected_customer['name'])], limit=1
                )

                # set the customer values
                self.customer_city = selected_customer.get('city', '')
                self.customer_street = selected_customer.get('street', '')
                self.name_surname = selected_customer.get('name', '')

    @api.model
    def fields_get(self, allfields=None, attributes=None):
        """Override fields_get to populate selection dynamically."""
        res = super().fields_get(allfields, attributes)

        if 'customer_api_selection' in res:
            res['customer_api_selection']['selection'] = self._get_customer_selection()

        return res

    # @api.onchange('name_surname')
    # def _onchange_name_surname(self):
    #     """
    #     Müşteri bilgilerini name_surname seçildiğinde otomatik olarak doldurur.
    #     """
    #     if self.name_surname:
    #         partner = self.env['res.partner'].search([('name', '=', self.name_surname)], limit=1)
    #         if partner:
    #             self.customer_country_id = partner.country_id.id
    #             self.customer_city = partner.city
    #             self.customer_district = partner.street
    #             self.phone = partner.phone
    #             self.customer_tax_adress = partner.property_account_position_id.name
    #             self.customer_postal_code = partner.zip

    # @api.onchange('supplier_name')
    # def _onchange_supplier_name(self):
    #     """
    #     Tedarikçi bilgilerini supplier_name seçildiğinde API'den çekip doldurur.
    #     """
    #     if self.supplier_name:
    #         supplier_data = self._fetch_supplier_data(self.supplier_name)
    #         if supplier_data:
    #             self.supplier_lastname = supplier_data.get("lastname")
    #             self.mersis_number = supplier_data.get("mersis_number")
    #             self.account_number = supplier_data.get("account_number")
    #             self.target_title = supplier_data.get("company_name")
    #             self.supplier_country_id = self.env['res.country'].search([('name', '=', supplier_data.get("country"))], limit=1).id
    #             self.city = supplier_data.get("city")
    #             self.district = supplier_data.get("district")
    #             self.street = supplier_data.get("street")
    #             self.building_no = supplier_data.get("building_no")
    #             self.supplier_tax_schema = supplier_data.get("tax_schema")

    def _fetch_supplier_data(self, supplier_name):
        """
        Tedarikçi bilgilerini API'den getirir.
        """
        api_url = "http://api.example.com/suppliers"
        api_key = self.env['ir.config_parameter'].sudo(
        ).get_param('e_fatura.api_key')

        headers = {"Authorization": f"Bearer {api_key}"}
        try:
            response = requests.get(
                f"{api_url}?name={supplier_name}", headers=headers)
            response.raise_for_status()
            return response.json()  # API JSON formatına göre düzenlenmelidir
        except requests.RequestException as e:
            _logger.error(f"Tedarikçi bilgisi getirilemedi: {str(e)}")
            return {}

    @api.depends("product_line_ids")
    def _compute_tax_total(self):
        for record in self:
            # Vergi toplamını hesapla
            record.tax_total = sum(
                line.tax_total for line in record.product_line_ids)

    @api.depends("product_line_ids")
    def _compute_untaxed_total(self):
        for record in self:
            # Vergisiz toplamı hesapla
            record.amount_untaxed_signed = sum(
                line.price_unit * line.quantity for line in record.product_line_ids
            )

    @api.depends("amount_untaxed_signed", "tax_total")
    def _compute_total(self):
        for record in self:
            # Toplam tutarı hesapla
            record.amount_total_signed = record.amount_untaxed_signed + record.tax_total

    def open_address_form(self):
        """
        Adres ve Fatura Bilgileri formunu açan işlem.
        """
        return {
            "type": "ir.actions.act_window",
            "name": "Adres ve Fatura Bilgileri",
            "view_mode": "form",
            "res_model": "account.move",
            "res_id": self.id,
            "target": "new",
        }

    def open_product_form(self):
        """
        Ürün Bilgileri formunu açan işlem.
        """
        return {
            "type": "ir.actions.act_window",
            "name": "Ürün Bilgileri",
            "view_mode": "form",
            "res_model": "account.move.line.product",
            "target": "new",
        }

    def check_required_fields(self):
        """
        Eksik zorunlu alanları kontrol eder ve liste halinde döner.
        """
        required_fields = {
            "country_id": _("Ülke"),  # Zorunlu
            "city": _("Şehir"),  # Zorunlu
            "district": _("Mahalle/İlçe"),  # Zorunlu
            "target_title": _("Alıcı Ünvanı"),
            "target_tckn_vkn": _("Alıcı TCKN/VKN"),
            "invoice_type": _("Fatura Tipi"),  # Zorunlu
            "document_currency_code": _("Para Birimi"),
            "create_date_utc": _("Oluşturulma Tarihi"),
            "external_invoice_id": _("Dış Fatura ID"),
            "name_surname": _("Müşteri Adı Soyadı"),
            "tax_total": _("Toplam Vergi"),  # Zorunlu
            "amount_untaxed_signed": _("Vergisiz Tutar"),  # Zorunlu
            "amount_total_signed": _("Toplam Tutar"),  # Zorunlu
        }

        missing_fields = []
        for field, label in required_fields.items():
            if not getattr(self, field):
                missing_fields.append(label)

        return missing_fields

    def action_post_efatura(self):
        for record in self:
            apiKey = (
                self.env["ir.config_parameter"].sudo(
                ).get_param("e_fatura.api_key")
            )

            if not apiKey:
                _logger.error("API anahtarı bulunamadı.")
                raise UserError(
                    _(
                        "API anahtarı bulunamadı. Lütfen sistem yöneticinizle iletişime geçin."
                    )
                )

            headers = {
                "Content-Type": "application/json",
                "Authorization": "Bearer " + apiKey,
            }

            try:
                issue_date = record.create_date_utc or datetime.utcnow()
                issue_date_trt = issue_date + timedelta(hours=3)
                formatted_date = issue_date_trt.strftime("%Y-%m-%d")
                formatted_time = issue_date_trt.strftime("%H:%M:%S.%f")

                tax_totals = defaultdict(
                    lambda: {"TaxableAmount": 0.0, "TaxAmount": 0.0}
                )

                for line in record.product_line_ids:
                    if line.tax_present:
                        key = float(line.tax_present)
                        tax_totals[key]["TaxableAmount"] += (
                            line.quantity * line.price_unit
                        )
                        tax_totals[key]["TaxAmount"] += line.tax_total

                tax_total = {
                    "TaxAmount": {
                        "currencyId": record.currency_id.name,
                        "value": sum(tax["TaxAmount"] for tax in tax_totals.values()),
                    },
                    "TaxSubtotal": [
                        {
                            "TaxableAmount": {
                                "currencyId": record.currency_id.name,
                                "value": tax["TaxableAmount"],
                            },
                            "TaxAmount": {
                                "currencyId": record.currency_id.name,
                                "value": tax["TaxAmount"],
                            },
                            "Percent": {
                                "value": percent,
                            },
                            "TaxCategory": {
                                "TaxScheme": {
                                    "Name": {
                                        "value": "KDV",
                                    },
                                    "TaxTypeCode": {
                                        "value": "0015",
                                    },
                                },
                            },
                        }
                        for percent, tax in tax_totals.items()
                    ],
                }

                # Fatura verisini oluştur
                data = {
                    "Action": "SendInvoice",
                    "parameters": {
                        "invoices": [
                            {
                                "Invoice": {
                                    "UblVersionId": {"value": "2.1"},
                                    "CustomizationId": {"value": "TR1.2"},
                                    "ProfileId": {"value": record.efatura_type},
                                    "CopyIndicator": {"value": False},
                                    "IssueDate": {"value": formatted_date},
                                    "IssueTime": {"value": formatted_time},
                                    "InvoiceTypeCode": {"value": record.invoice_type},
                                    "Note": [
                                        {
                                            "value": f"Fatura Notu - {record.invoice_note}"
                                        }
                                    ],
                                    "DocumentCurrencyCode": {
                                        "value": record.document_currency_code.name
                                    },
                                    "LineCountNumeric": {
                                        "value": len(record.product_line_ids)
                                    },
                                    "OrderReference": {
                                        "Id": {"value": record.order_number},
                                        "IssueDate": {"value": formatted_date},
                                        "IssueTime": {"value": formatted_time},
                                    },
                                    "AccountingSupplierParty": {
                                        "Party": {
                                            "PartyIdentification": [
                                                {
                                                    "Id": {
                                                        "schemeId": "VKN",
                                                        "value": "9000068418",
                                                    }
                                                },
                                                {
                                                    "Id": {
                                                        "schemeId": "MERSISNO",
                                                        "value": record.mersis_number,
                                                    }
                                                },
                                                {
                                                    "Id": {
                                                        "schemeId": "TICARETSICILNO",
                                                        "value": record.account_number,
                                                    }
                                                },
                                            ],
                                            "PartyName": {
                                                "Name": {"value": record.target_title}
                                            },
                                            "PostalAddress": {
                                                "Room": {"value": record.room},
                                                "StreetName": {"value": record.street},
                                                "BuildingNumber": {
                                                    "value": record.building_no
                                                },
                                                "CitySubdivisionName": {
                                                    "value": record.district
                                                },
                                                "CityName": {"value": record.city},
                                                "Country": {
                                                    "Name": {
                                                        "value": record.supplier_country_id.name
                                                    }
                                                },
                                            },
                                            "PartyTaxScheme": {
                                                "TaxScheme": {
                                                    "Name": {
                                                        "value": record.supplier_tax_schema
                                                    }
                                                }
                                            },
                                            "Person": {
                                                "FirstName": {
                                                    "value": record.supplier_name
                                                },
                                                "FamilyName": {
                                                    "value": record.supplier_lastname
                                                },
                                            },
                                        }
                                    },
                                    "AccountingCustomerParty": {
                                        "Party": {
                                            "PartyIdentification": [
                                                {
                                                    "ID": {
                                                        "schemeID": "VKN",
                                                        "Value": "9000068420",
                                                    }
                                                }
                                            ],
                                            "PartyName": {
                                                "Name": {"value": record.name_surname}
                                            },
                                            "PostalAddress": {
                                                "Room": {"value": record.customer_room},
                                                "StreetName": {
                                                    "value": record.customer_street
                                                },
                                                "BuildingNumber": {
                                                    "value": record.customer_building_no
                                                },
                                                "CitySubdivisionName": {
                                                    "value": record.customer_district
                                                },
                                                "CityName": {
                                                    "value": record.customer_city
                                                },
                                                "Country": {
                                                    "Name": {
                                                        "value": record.customer_country_id.name
                                                    }
                                                },
                                            },
                                            "PartyTaxScheme": {
                                                "TaxScheme": {
                                                    "Name": {
                                                        "value": record.customer_tax_adress
                                                    }
                                                }
                                            },
                                            "Contact": {
                                                "Telephone": {"value": record.phone}
                                            },
                                        }
                                    },
                                    "TaxTotal": [tax_total],
                                    "LegalMonetaryTotal": {
                                        "LineExtensionAmount": {
                                            "currencyId": record.document_currency_code.name,
                                            "value": record.amount_untaxed_signed,
                                        },
                                        "TaxExclusiveAmount": {
                                            "currencyId": record.document_currency_code.name,
                                            "value": record.amount_untaxed_signed,
                                        },
                                        "TaxInclusiveAmount": {
                                            "currencyId": record.document_currency_code.name,
                                            "value": record.amount_total_signed,
                                        },
                                        "PayableAmount": {
                                            "currencyId": record.document_currency_code.name,
                                            "value": record.amount_total_signed,
                                        },
                                    },
                                    "InvoiceLine": [
                                        {
                                            "Id": {"value": str(i + 1)},
                                            "InvoicedQuantity": {
                                                "unitCode": line.get_unit_code(),
                                                "value": str(line.quantity),
                                            },
                                            "LineExtensionAmount": {
                                                "currencyId": record.document_currency_code.name,
                                                "value": line.quantity
                                                * line.price_unit,
                                            },
                                            "TaxTotal": {
                                                "TaxAmount": {
                                                    "currencyId": record.document_currency_code.name,
                                                    "value": line.tax_total,
                                                },
                                                "TaxSubtotal": [
                                                    {
                                                        "TaxableAmount": {
                                                            "currencyId": record.document_currency_code.name,
                                                            "value": line.quantity
                                                            * line.price_unit,
                                                        },
                                                        "TaxAmount": {
                                                            "currencyId": record.document_currency_code.name,
                                                            "value": line.tax_total,
                                                        },
                                                        "Percent": {
                                                            "value": (
                                                                int(line.tax_present)
                                                                if line.tax_present
                                                                else 0
                                                            )
                                                        },
                                                        "TaxCategory": {
                                                            "TaxScheme": {
                                                                "Name": {
                                                                    "value": "KDV"
                                                                },
                                                                "TaxTypeCode": {
                                                                    "value": "0015"
                                                                },
                                                            }
                                                        },
                                                    }
                                                ],
                                            },
                                            "Item": {
                                                "Description": {
                                                    "value": line.description
                                                    or "Açıklama"
                                                },
                                                "Name": {"value": line.product_id.name},
                                            },
                                            "Price": {
                                                "PriceAmount": {
                                                    "currencyId": record.document_currency_code.name,
                                                    "value": line.price_unit,
                                                }
                                            },
                                        }
                                        for i, line in enumerate(
                                            record.product_line_ids
                                        )
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
                                                    "Pdf": True,
                                                },
                                            }
                                        ]
                                    },
                                }
                            }
                        ],
                        "userInfo": {"Username": "Uyumsoft", "Password": "Uyumsoft"},
                    },
                }

                _logger.info(f"REQUEST DATA: {data}")
                response = requests.post(
                    "https://e-ran-test.ranvals.com/api/post/BasicIntegrationApi",
                    json=data,
                    headers=headers,
                )

                # Yanıt kontrolü
                if response.status_code == 200 and response.text.strip() == "OK":
                    _logger.info("Fatura gönderimi başarılı.")

                    self.is_efatura = True
                    self.is_giden_efatura = True
                    self.message_post(body=_("E-Fatura başarıyla gönderildi."))

                    return True
                else:
                    _logger.error(f"Fatura gönderimi başarısız oldu: {
                                  response.text}")
                    raise UserError(
                        _("Fatura gönderimi başarısız oldu: %s") % response.text
                    )

            except requests.exceptions.RequestException as e:
                _logger.error(f"API bağlantı hatası: {str(e)}")
                raise UserError(_("API bağlantı hatası: %s") % str(e))

    def action_send_invoice(self):
        """
        Fatura gönderim işlemi: Zorunlu alan kontrolü ve API isteği.
        """
        missing_fields = self.check_required_fields()
        if missing_fields:
            missing_fields_str = ", ".join(missing_fields)
            raise UserError(_("Zorunlu alanları doldurunuz:\n%s") %
                            missing_fields_str)

        # Zorunlu alanlar tamam ise devam et
        try:
            self.sync_invoices()  # Örneğin bir API isteği
        except Exception as e:
            _logger.error(f"Fatura gönderimi sırasında hata: {str(e)}")
            raise UserError(
                _("Fatura gönderimi sırasında hata oluştu:\n%s") % str(e))

    def action_download_efatura_pdf(self):
        return self.env.ref("account.account_invoices").report_action(self)

    def sync_invoices(self):
        try:
            data = self.fetch_external_invoices()
            if not data:
                _logger.warning("Hiçbir fatura verisi alınamadı.")
                return

            invoice_ids = [invoice["DocumentId"] for invoice in data]
            existing_invoices = self.env["account.move"].search(
                [("external_invoice_id", "in", invoice_ids)]
            )
            existing_invoice_ids = set(
                existing_invoices.mapped("external_invoice_id"))

            for invoice in data:
                try:

                    # Fetch the currency record
                    currency = (
                        self.env["res.currency"]
                        .sudo()
                        .search(
                            [("name", "=", invoice["DocumentCurrencyCode"])], limit=1
                        )
                    )
                    all_currencies = self.env["res.currency"].sudo().search([])
                    print(all_currencies[0].name)

                    if not currency:
                        # Create the currency record if it doesn't exist
                        currency = (
                            self.env["res.currency"]
                            .sudo()
                            .create(
                                {
                                    "name": invoice["DocumentCurrencyCode"],
                                    "symbol": invoice["DocumentCurrencyCode"],
                                }
                            )
                        )

                    create_date_utc = (
                        datetime.strptime(
                            invoice["CreateDateUtc"], "%Y-%m-%dT%H:%M:%S.%f"
                        )
                        if invoice["CreateDateUtc"]
                        else False
                    )
                    execution_date = (
                        datetime.strptime(
                            invoice["ExecutionDate"], "%Y-%m-%dT%H:%M:%S")
                        if invoice["ExecutionDate"]
                        else False
                    )

                    values = {
                        "is_efatura": True,
                        "amount_untaxed_signed": invoice["TaxExclusiveAmount"],
                        "amount_total_signed": invoice["PayableAmount"],
                        "tax_total": invoice["TaxTotal"],
                        "target_tckn_vkn": invoice["TargetTcknVkn"],
                        "target_title": invoice["TargetTitle"],
                        "create_date_utc": create_date_utc,
                        "execution_date": execution_date,
                        "document_currency_code": currency.id,  # Assign the ID of the currency record
                        "invoice_type": "SATIS",
                    }

                    if invoice["DocumentId"] in existing_invoice_ids:
                        existing_invoice = existing_invoices.filtered(
                            lambda i: i.external_invoice_id == invoice["DocumentId"]
                        )
                        existing_invoice.write(values)
                        _logger.info(
                            f"Var olan fatura güncellendi, DocumentId: {
                                invoice['DocumentId']}"
                        )
                    else:
                        self.create(
                            {
                                "name": invoice["InvoiceId"],
                                "external_invoice_id": invoice["DocumentId"],
                                **values,
                            }
                        )
                        _logger.info(
                            f"Yeni fatura oluşturuldu, DocumentId: {
                                invoice['DocumentId']}"
                        )
                except Exception as e:
                    _logger.error(f"Fatura işlenirken hata oluştu: {str(e)}")
                    raise e

            return True
        except Exception as e:
            return e

    def fetch_external_invoices(self):
        url = "https://e-ran-test.ranvals.com/api/post/BasicIntegrationApi"
        apiKey = self.env["ir.config_parameter"].sudo(
        ).get_param("e_fatura.api_key")

        if not apiKey:
            _logger.error("API anahtarı bulunamadı.")
            raise Exception("API anahtarı bulunamadı.")

        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + apiKey,
        }
        all_invoices = []
        page_index = 0
        total_pages = 1

        while page_index < total_pages:
            body = {
                "Action": "GetInboxInvoiceList",
                "parameters": {
                    "userInfo": {"Username": "Uyumsoft", "Password": "Uyumsoft"},
                    "query": {
                        "CreateStartDate": "2020-08-30T23:59:59.999",
                        "CreateEndDate": "2020-09-04T23:59:59.999",
                        "PageIndex": page_index,
                    },
                },
            }

            try:
                response = requests.post(
                    url, headers=headers, data=json.dumps(body))
                response.raise_for_status()  # HTTP hatalarını yakala
            except requests.RequestException as e:
                _logger.error(f"API bağlantı hatası: {str(e)}")
                raise Exception(
                    "API bağlantı hatası: API anahtarınızı ve URL'nizi kontrol edin"
                )

            try:
                data = response.json()
            except json.JSONDecodeError:
                _logger.error(
                    f"API'den dönen yanıt JSON değil: {response.text}"
                )
                break

            if data.get("Data", {}).get("IsSucceded", False):
                invoices = data["Data"]["Value"]["Items"]
                all_invoices.extend(invoices)
                total_pages = data["Data"]["Value"]["TotalPages"]
                page_index += 1
            else:
                _logger.error(
                    "API'den veri alınamadı: "
                    + data["Data"].get("Message", "Bilinmeyen hata")
                )
                break

        return all_invoices

    @api.model
    def action_sync_invoices(self, context=None):
        try:
            self.sync_invoices()
            return {
                "type": "ir.actions.client",
                "tag": "reload",
            }
        except Exception as e:
            _logger.error(f"Fatura senkronizasyonu hatası: {str(e)}")
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": "Hata",
                    "message": f"Fatura senkronizasyonunda hata: {str(e)}",
                    "type": "danger",
                },
            }


class AccountMoveLineProduct(models.Model):
    _name = "account.move.line.product"
    _description = "Ürün Bilgileri"

    move_id = fields.Many2one(
        "account.move", string="Fatura", ondelete="cascade")
    product_id = fields.Many2one(
        "product.product", string="Ürün", required=True)
    description = fields.Char(string="Açıklama")
    quantity = fields.Float(string="Miktar", required=True, default=1.0)
    price_unit = fields.Float(string="Birim Fiyatı", required=True)
    subtotal = fields.Float(
        string="Ara Toplam", compute="_compute_subtotal", store=True
    )
    tax_total = fields.Float(
        string="Vergi Tutarı", store=True, compute="_compute_tax_total"
    )
    tax_present = fields.Selection(
        [
            ("1", "1"),
            ("8", "8"),
            ("10", "10"),
            ("18", "18"),
            ("20", "20"),
        ],
        string="KDV Oranı",
        default="20",
    )
    unit_code = fields.Selection(
        [
            ("adet", "Adet"),
            ("paket", "Paket"),
            ("kutu", "Kutu"),
            ("kg", "Kilogram"),
            ("mg", "Miligram"),
            ("ton", "Ton"),
            ("net_ton", "Net Ton"),
            ("gross_ton", "Gross Ton"),
            ("mm", "Milimetre"),
            ("cm", "Santimetre"),
            ("m", "Metre"),
            ("km", "Kilometre"),
            ("ml", "Mililitre"),
            ("mm3", "Milimetreküp"),
            ("cm2", "Santimetrekare"),
            ("cm3", "Santimetreküp"),
            ("m2", "Metrekare"),
            ("m3", "Metreküp"),
            ("kJ", "Kilojoule"),
            ("cl", "Centilitre"),
            ("karat", "Karat"),
            ("kwh", "Kilowatt-saat"),
            ("mwh", "Megawatt-saat"),
            ("1000_it", "1000 Litre"),
            ("saf_alkol_it", "Saf Alkol Litre"),
            ("kg_m2", "Kilogram Metrekare"),
            ("hücre_adet", "Hücre Adet"),
            ("set", "Set"),
            ("1000_adet", "1000 Adet"),
            ("scm", "SCM"),
            ("ncm", "NCM"),
            ("mmBTU", "mmBTU"),
            ("cm3", "CM3"),
            ("düzine", "Düzine"),
            ("dm2", "Desimetrekare"),
            ("dm", "Desimetre"),
            ("ha", "Hektar"),
            ("metretul", "Metretül (LM)"),
        ],
        string="Miktar Cinsi",
        required=True,
        default="adet",
    )

    @api.depends("quantity", "price_unit", "tax_present")
    def _compute_tax_total(self):
        for line in self:
            line.tax_total = (
                line.quantity * line.price_unit *
                (float(line.tax_present) / 100)
            )

    @api.depends("quantity", "price_unit")
    def _compute_subtotal(self):
        for line in self:
            tax_present = float(line.tax_present) if line.tax_present else 0.0
            line.subtotal = line.quantity * \
                line.price_unit * (1 + tax_present / 100)

    def get_unit_code(self):
        """
        Bu fonksiyon, unit_code alanındaki seçime göre evrensel birim kodlarını döndürür.
        """
        unit_codes = {
            "adet": "NIU",
            "paket": "C62",
            "kutu": "BX",
            "kg": "KGM",
            "mg": "GRM",
            "ton": "TNE",
            "net_ton": "TNE",
            "gross_ton": "GT",
            "mm": "MTR",
            "cm": "CMT",
            "m": "MTR",
            "km": "KMT",
            "ml": "LTR",
            "mm3": "M3",
            "cm2": "M2",
            "cm3": "M3",
            "m2": "M2",
            "m3": "M3",
            "kJ": "KGM",
            "cl": "LTR",
            "karat": "KGM",
            "kwh": "KWH",
            "mwh": "MWH",
            "1000_it": "LTR",
            "saf_alkol_it": "LTR",
            "kg_m2": "KGM",
            "hücre_adet": "NCL",
            "set": "SET",
            "1000_adet": "NIU",
            "scm": "M3",
            "ncm": "KGM",
            "mmBTU": "KGM",
            "cm3": "M3",
            "düzine": "DOZ",
            "dm2": "DM2",
            "dm": "DM",
            "ha": "M2",
            "metretul": "MTR",
        }

        # Default to "NIU" if unit code not found
        return unit_codes.get(self.unit_code, "NIU")
