from odoo import models, fields

class Payment(models.Model):
    _name = 'hospital.payment'
    _description = 'Ödeme Bilgileri'

    patient_id = fields.Many2one('hospital.patient', string='Hasta', required=True)
    appointment_id = fields.Many2one('hospital.appointment', string='Randevu')
    amount_due = fields.Float(string='Ödenecek Tutar', required=True)
    payment_date = fields.Date(string='Ödeme Tarihi')
    payment_status = fields.Selection([
        ('unpaid', 'Ödenmedi'),
        ('paid', 'Ödendi')
    ], default='unpaid', string='Durum')
    notes = fields.Text(string='Notlar')