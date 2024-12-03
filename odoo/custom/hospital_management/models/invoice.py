from odoo import models, fields ,api

class Invoice(models.Model):
    _name = 'hospital.invoice'
    _description = 'Fatura Bilgileri'

    patient_id = fields.Many2one('hospital.patient', string='Hasta', required=True)
    appointment_id = fields.Many2one('hospital.appointment', string='Randevu')
    total_amount = fields.Float(string='Toplam Tutar', compute='_compute_total_amount')
    payment_id = fields.Many2one('hospital.payment', string='Ödeme Bilgisi')
    invoice_date = fields.Date(string='Fatura Tarihi')

    @api.depends('appointment_id', 'payment_id')
    def _compute_total_amount(self):
        for invoice in self:
            total = 0
            # Randevudaki hizmetleri ve testleri alarak toplamı hesapla
            if invoice.appointment_id:
                # Test fiyatlarını ekle
                for test in invoice.appointment_id.test_ids:
                    total += test.test_id.price
            invoice.total_amount = total
