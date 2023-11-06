# -*- coding: utf-8 -*-
import base64

from odoo import _,models, fields, api


class ProductTemplate(models.Model):
    _inherit = "product.template"

    website_url = fields.Char('Website URL')

    def action_print_qrcode(self):
        report_action = self.env.ref("product_qrcode.report_product_template_qrcode").report_action(self, data=None)
        return report_action
