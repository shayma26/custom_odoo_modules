from odoo import models, fields, api


class OdooConnectApi(models.Model):
    _name = 'odoo.connect.api'

    _sql_constraints = [
        ('unique_name', 'UNIQUE(name)', "It appears that you've already created an API using the same name.")
    ]

    name = fields.Char('URL Name', required=True)
    description = fields.Html('Description')
    api_line_ids = fields.One2many('odoo.connect.api.line', 'api_id', string="API Lines", required=True)
    version = fields.Char(default="1.0.0")

    @api.model
    def create(self, vals):
        vals['name'] = vals['name'].replace(" ", "_")
        return super().create(vals)

    def write(self, vals):
        if vals.get('name'):
            vals['name'] = vals.get('name').replace(" ", "_")
        return super().write(vals)

    def action_preview(self):
        return {
            'type': 'ir.actions.act_url',
            'target': 'new',
            'url': '/documentation/%s' % self.id,
        }
