from odoo import models, fields

class HealthHistory(models.Model):
    _name = 'hospital.health.history'
    _description = 'Hasta Sağlık Geçmişi'

    patient_id = fields.Many2one('hospital.patient', string='Hasta', required=True)
    visit_date = fields.Date(string='Ziyaret Tarihi')
    reason_for_visit = fields.Text(string='Ziyaret Nedeni')
    notes = fields.Text(string='Notlar')
