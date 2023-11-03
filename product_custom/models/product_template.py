# -*- coding: utf-8 -*-
import base64

from odoo import models, fields, api
from odoo.tools import float_repr


class ProductTemplate(models.Model):
    _inherit = "product.template"

    website_url = fields.Char('Website URL')
    qr_code_str = fields.Char(string='QR Code', compute='_compute_qr_code_str')

    @api.depends('website_url')
    def _compute_qr_code_str(self):
        def get_qr_encoding(tag, field):
            website_url_byte_array = field.encode()
            website_url_tag_encoding = tag.to_bytes(length=1, byteorder='big')
            website_url_length_encoding = len(website_url_byte_array).to_bytes(length=1, byteorder='big')
            return website_url_tag_encoding + website_url_length_encoding + website_url_byte_array

        for record in self:
            qr_code_str = ''
            if record.website_url:
                website_url_enc = get_qr_encoding(1, record.website_url)

                str_to_encode = website_url_enc
                qr_code_str = base64.b64encode(str_to_encode).decode()
            record.qr_code_str = qr_code_str

