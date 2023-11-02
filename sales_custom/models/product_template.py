from odoo import fields, models, api


class ProductTemplate(models.Model):
    _inherit = "product.template"

    sales_margin = fields.Float(digits=(6, 2), string="Sales margin")
    '''precision is the total number of significant digit in the given number before and after the decimal point. 
    And the scale is the number of digit after the decimal point.'''
    list_price = fields.Float(
        'Sales Price', default=1.0,
        digits='Product Price',
        help="Price at which the product is sold to customers.", compute="_compute_sales_price"
    )

    @api.depends('sales_margin', 'standard_price')
    def _compute_sales_price(self):
        for record in self:
            if record.sales_margin != 0:
                record.list_price = record.standard_price / record.sales_margin
            else:
                record.list_price = 1.0
