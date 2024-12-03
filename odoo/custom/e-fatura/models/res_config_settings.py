from odoo import fields, models, api
import requests

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    active = fields.Boolean(string="Activate E-Fatura")
    api_key = fields.Char(string="API Key")
    remaining_credits = fields.Integer(string="Kalan Kredi", readonly=True)

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('e_fatura.active', self.active)
        self.env['ir.config_parameter'].sudo().set_param('e_fatura.api_key', self.api_key)

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            active=self.env['ir.config_parameter'].sudo().get_param('e_fatura.active', default=False),
            api_key=self.env['ir.config_parameter'].sudo().get_param('e_fatura.api_key', default=''),
            remaining_credits=self._get_remaining_credits() 
        )
        return res

    def _get_remaining_credits(self):
        """Kalan kredi sayısını API çağrısı ile getirir."""
        api_key = self.env['ir.config_parameter'].sudo().get_param('e_fatura.api_key')

        if not api_key:
            return 0  

        try:
            response = requests.get("http://104.247.173.87:8888/api/get/get-user-credit", headers={"Authorization": f"Bearer {api_key}"})
            response.raise_for_status()
            data = response.json()
            credit = data.get("credit", 0)

            return credit
        except requests.RequestException:
            return 0  
