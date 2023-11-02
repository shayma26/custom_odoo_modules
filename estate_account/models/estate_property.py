from odoo import models,fields

class EstateProperty(models.Model):
    _inherit = 'estate.property'
    invoice_id = fields.Many2one("account.move")


    def action_sold(self):
        res=super().action_sold()
        # print("*************************************************")
        journal = self.env["account.journal"].search([("type", "=", "sale")], limit=1)
        for record in self:
            invoice = self.env['account.move'].create({
                'partner_id': record.buyer_id.id,  # the create method doesn't accept recordsets as field values.
                'move_type': "out_invoice",
                'journal_id': journal.id,
                'invoice_line_ids': [
                    (
                        0,  # 0 for creation
                        0,  # 0 for creation
                        {
                            'name': record.name,
                            'quantity': 1.0,
                            'price_unit': record.selling_price * 0.06
                        }
                    ),
                    (
                        0,
                        0,
                        {
                            'name': 'Administration fees',
                            'quantity': 1.0,
                            'price_unit': 100.00
                        }
                    )
                ]
            })
            record.invoice_id = invoice.id
            print(record.invoice_id)
        return res