from odoo import models, fields, api

class HospitalHomepage(models.Model):
    _name = 'hospital.homepage'
    _description = 'Hospital Homepage'

    def action_view_appointments(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Randevular',
            'res_model': 'hospital.appointment',
            'view_mode': 'tree,form',
            'target': 'current',
        }

    def action_view_patients(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Hastalar',
            'res_model': 'hospital.patient',
            'view_mode': 'tree,form',
            'target': 'current',
        }

    def action_view_doctors(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Doktorlar',
            'res_model': 'hospital.doctor',
            'view_mode': 'tree,form',
            'target': 'current',
        }

    def action_view_payments(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Muhasebe',
            'res_model': 'hospital.payment',
            'view_mode': 'tree,form',
            'target': 'current',
        }
