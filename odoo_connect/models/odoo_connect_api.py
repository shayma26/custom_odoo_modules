# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.http import request
from ..tools.tools import generate_token


class OdooConnectApi(models.Model):
    _name = 'odoo.connect.api'
    _description = "Odoo API"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'website.published.mixin']

    name = fields.Char('URL Name', required=True, help="The name used in the URL to call API")
    description = fields.Html('Description', help="A brief description of this API: purpose,integration system,...")
    api_line_ids = fields.One2many('odoo.connect.api.line', 'api_id', string="API Lines", required=True)
    version = fields.Char(default="1.0.0")

    _sql_constraints = [
        ('unique_name', 'UNIQUE(name)', "It appears that you've already created an API using the same name.")
    ]

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['name'] = vals['name'].replace(" ", "_")
        return super().create(vals_list)

    def write(self, vals):
        if vals.get('name'):
            vals['name'] = vals.get('name').replace(" ", "_")
        return super().write(vals)


    def action_preview(self):
        response = {
            'type': 'ir.actions.act_url',
            'target': 'new',
            'url': '/documentation/%s' % self.id
        }
        if not self.is_published:
            token = generate_token()
            response['url'] = response['url'] + "?token=%s" % token
            request.session['token'] = token
        return response
