# -*- coding: utf-8 -*-

from odoo import _, models
from odoo.exceptions import UserError


class ReportProductTemplateQrCode(models.AbstractModel):
    _name = 'report.product_qrcode.report_producttemplateqrcode'
    _description = 'Product QrCode Report'

    def _get_report_values(self, docids, data):
        return {
            'products': self.env['product.template'].browse(docids)
        }
