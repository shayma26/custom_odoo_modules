# -*- coding: utf-8 -*-
from odoo import models, fields, api, Command
from string import capwords
from ..tools.tools import format_data
from odoo.http import request


class OdooConnectApiLine(models.Model):
    _name = 'odoo.connect.api.line'
    _description = "Odoo API Line"

    name = fields.Char(required=True, help="The name used in the URL to call this line from the API")
    description = fields.Char('Title', help="Name of this API line")
    api_name = fields.Char(related="api_id.name", readonly=True)
    api_id = fields.Many2one('odoo.connect.api', readonly=True)
    method = fields.Selection(
        [('get', 'GET'), ('post', 'POST'), ('put', 'PUT'), ('delete', 'DELETE'), ('report', 'REPORT')], required=True)
    model_id = fields.Many2one('ir.model', string='Model', required=True, ondelete='cascade')
    fields_ids = fields.Many2many('ir.model.fields', help='''Select desired fields''')
    report_id = fields.Many2one("ir.actions.report")
    report_template_name = fields.Char(related="report_id.report_name")
    report_type = fields.Selection([('excel', 'EXCEL'), ('pdf', 'PDF')])
    report_response_type = fields.Selection([('url','URL'),('file','File')])

    _sql_constraints = [
        ('unique_api', 'UNIQUE(name,method,model_id)',
         "It appears that you've already created an API using the same"
         " method and model. Please review your existing "
         "API configurations to ensure there are no duplicates")
    ]

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name'):
                vals['name'] = vals.get('name').replace(" ", "_").lower()
            if vals.get('description'):
                vals['description'] = capwords(vals.get('description'))
            if not vals.get('description') and vals.get('name'):
                vals['description'] = capwords(vals.get('name').replace("_", " "))
        return super().create(vals_list)

    def write(self, vals):
        if vals.get('name'):
            vals['name'] = vals.get('name').replace(" ", "_").lower()
        if vals.get('description'):
            vals['description'] = capwords(vals.get('description'))
        return super().write(vals)

    @api.onchange('model_id')
    def _onchange_model(self):
        for record in self:
            if record.model_id:
                record.fields_ids = None
                self.report_id = None
                self.report_response_type = None
                if self.method == 'post':
                    required_fields = self.model_id.field_id.filtered(lambda rec: rec.required)
                    if required_fields:
                        self.fields_ids = required_fields.ids

    @api.onchange('method')
    def _onchange_method(self):
        self.report_type = None
        self.report_response_type = None

    def api_action(self, method, user, record_id=None, vals=None):
        model_obj = self.env[self.model_id.model]
        model_fields = self.fields_ids.mapped('name')
        if vals:
            if vals.get('data'):
                vals = vals.get('data')
                output_data = []
                for item in vals:
                    filtered_item = {key: format_data(self.model_id, key, item[key]) for key in model_fields if item.get(key)}
                    output_data.append(filtered_item)
                vals = output_data
            else:
                vals = {key: format_data(self.model_id, key, vals[key]) for key in model_fields if vals.get(key)}
        model_obj = model_obj.with_user(user)
        if method == 'GET':
            if record_id:
                return model_obj.browse(record_id).read(model_fields)
            return model_obj.search([]).read(model_fields)
        if method == 'POST':
            return {'ids': model_obj.create(vals).ids}
        if method == 'PUT':
            model_obj.browse(record_id).update(vals)
            return {'id': record_id}
        if method == 'DELETE':
            model_obj.browse(record_id).unlink()
            return {'id': record_id}
        if method == 'report':
            if self.report_response_type == 'url':
                if self.report_type == 'pdf':
                    ids = ','.join(map(str,record_id))
                    return "/report/pdf/%s/%s" % (self.report_template_name, ids)
                elif self.report_type == 'excel':
                    return "/report_xlsx/%s/%s" % (self.api_name, self.name)
            elif self.report_response_type == 'file':
                report = request.env['ir.actions.report']
                context = dict(request.env.context)
                if self.report_type == 'pdf':
                    return report.with_context(context)._render_qweb_pdf(self.report_id.report_name, record_id)[0]

                elif self.report_type == 'excel':
                    report_name = 'odoo_connect.api_data_report_xls'
                    report = report._get_report_from_name(report_name)
                    return report.with_context(context)._render_xlsx(report_name, self.id, None)[0]


