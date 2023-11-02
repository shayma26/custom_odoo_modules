from odoo import models, fields, api


class SaleReport(models.Model):
    _inherit = "sale.report"

    salesman_ids = fields.Many2one("res.users", string="Salespersons", readonly=True)

    price_total_per_salesman = fields.Float('Total', readonly=True)


    def _from_sale(self):
        res = super()._from_sale()
        res += """JOIN res_users_sale_order_line_rel rel ON rel.sale_order_line_id = l.id
            JOIN res_users us ON us.id = rel.res_users_id"""
        return res


    def _select_additional_fields(self):
        res = super()._select_additional_fields()
        res['salesman_ids'] = "us.id"
        res['price_total_per_salesman'] = "l.price_total_per_salesman"
        return res

    def _group_by_sale(self):
        res = super()._group_by_sale()
        res += """,
                    us.id,
                    l.price_total_per_salesman"""
        return res
