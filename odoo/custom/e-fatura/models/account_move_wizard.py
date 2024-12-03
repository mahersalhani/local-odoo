from odoo import models, fields, api

class InvoiceEInvoiceWizard(models.TransientModel):
    _name = 'invoice.einvoice.wizard'
    _description = 'Invoice E-Invoice Wizard'

    is_efatura = fields.Boolean(string='Is E-Fatura?', default=False)

    def confirm_selection(self):
        """Set the `is_efatura` flag on the corresponding invoice."""
        active_id = self.env.context.get('active_id')
        if active_id:
            invoice = self.env['account.move'].browse(active_id)
            invoice.is_efatura = self.is_efatura
        return {'type': 'ir.actions.act_window_close'}
