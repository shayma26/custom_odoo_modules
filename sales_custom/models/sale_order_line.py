from odoo import fields, models, api


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    order_line_sales_margin = fields.Float(string="Sales Margin")
    cost = fields.Float(related="product_template_id.standard_price")
    salesman_ids = fields.Many2many('res.users', string="Salespersons")

    price_total_per_salesman = fields.Monetary(
        string="Total",
        compute='_compute_amount_per_salesman',
        store=True, precompute=True)

    @api.onchange("product_id")
    def _get_sales_margin(self):
        for record in self:
            record.order_line_sales_margin = record.product_template_id.sales_margin


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

    @api.depends('price_total')
    def _compute_amount_per_salesman(self):
        for record in self:
            if record.salesman_ids:
                record.price_total_per_salesman = record.price_total / len(record.salesman_ids)

    def _prepare_invoice_line(self, **optional_values):
        return super(SaleOrderLine, self)._prepare_invoice_line(
            salesman_ids=self.salesman_ids,
            order_line_sales_margin=self.order_line_sales_margin,
            cost=self.cost,
            **optional_values
        )
