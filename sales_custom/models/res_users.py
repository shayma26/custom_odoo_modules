from odoo import models,fields

class User(models.Model):
    _inherit = "res.users"

    order_line_ids = fields.Many2many("sale.order.line")