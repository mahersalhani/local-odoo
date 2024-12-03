from odoo import models, fields

class LabTestResult(models.Model):
    _name = 'hospital.lab.test'
    _description = 'Laboratuvar Test Sonuçları'

    name = fields.Char(string='Test Adı', required=True)
    patient_id = fields.Many2one('hospital.patient', string='Hasta', required=True)
    test_date = fields.Datetime(string='Test Tarihi', required=True)
    result = fields.Text(string='Sonuçlar')
    doctor_id = fields.Many2one('hospital.doctor', string='Doktor')
    notes = fields.Text(string='Notlar')
