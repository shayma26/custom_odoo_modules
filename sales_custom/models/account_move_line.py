from odoo import fields, models, api


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    order_line_sales_margin = fields.Float(string="Sales Margin")
    cost = fields.Float()
    salesman_ids = fields.Many2many('res.users', string="Salespersons")

    @api.onchange("price_unit")
    def _onchange_price_unit(self):
        for record in self:
            if record.price_unit:
                record.order_line_sales_margin = record.cost / record.price_unit

    @api.onchange("order_line_sales_margin")
    def _onchange_sales_margin(self):
        for record in self:
            if record.order_line_sales_margin:
                record.price_unit = record.cost / record.order_line_sales_margin
