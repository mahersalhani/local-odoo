from odoo import models, fields, api

class Appointment(models.Model):
    _name = 'hospital.appointment'
    _description = 'Randevu Bilgileri'

    name = fields.Char(string='Randevu Referansı', required=True)
    patient_id = fields.Many2one('hospital.patient', string='Hasta', required=True)
    doctor_id = fields.Many2one('hospital.doctor', string='Doktor', required=True)
    doctor_email = fields.Char(related='doctor_id.email', string='Doktor E-postası', store=True)  # İlgili alan
    appointment_date = fields.Datetime(string='Randevu Tarihi', required=True)
    notes = fields.Text(string='Notlar')
    status = fields.Selection([
        ('scheduled', 'Planlandı'),
        ('completed', 'Tamamlandı'),
        ('canceled', 'İptal Edildi')
    ], default='scheduled', string='Durum')


    @api.model
    def create(self, vals):
        record = super(Appointment, self).create(vals)
        self.send_appointment_confirmation(record)
        return record

    def send_appointment_confirmation(self, appointment):
        template = self.env.ref('hospital_management.email_template_appointment_confirmation')
        self.env['mail.template'].browse(template.id).send_mail(appointment.id, force_send=True)
