from odoo import models, fields

class Patient(models.Model):
    _name = 'hospital.patient'
    _description = 'Hasta Bilgileri'

    name = fields.Char(string='Hasta Adı', required=True)
    date_of_birth = fields.Date(string='Doğum Tarihi')
    contact_number = fields.Char(string='İletişim Numarası')
    email = fields.Char(string='E-posta Adresi')
    appointment_ids = fields.One2many('hospital.appointment', 'patient_id', string='Randevular')
