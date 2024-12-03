from odoo import models, fields

class Doctor(models.Model):
    _name = 'hospital.doctor'
    _description = 'Doktor Bilgileri'
    email=fields.Char(string="E-posta")
    name = fields.Char(string='Doktor Adı', required=True)
    specialty = fields.Char(string='Uzmanlık Alanı')
    appointment_ids = fields.One2many('hospital.appointment', 'doctor_id', string='Randevular')

