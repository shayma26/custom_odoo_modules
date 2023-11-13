# -*- coding: utf-8 -*-
import ast
from odoo import models, fields, api
from string import capwords
from ..tools.tools import format_data, replace_last, insert_after
from odoo.http import request


class OdooConnectApiLine(models.Model):
    _name = 'odoo.connect.api.line'
    _description = "Odoo API Line"

    name = fields.Char(required=True, help="The name used in the URL to call this line from the API")
    description = fields.Char('Title', help="Name of this API line")
    api_name = fields.Char(related="api_id.name", readonly=True)
    api_id = fields.Many2one('odoo.connect.api', readonly=True)
    method = fields.Selection(
        [('get', 'GET'), ('post', 'POST'), ('put', 'PUT'), ('delete', 'DELETE'), ('report', 'REPORT')], required=True,
        default='get')
    model_id = fields.Many2one('ir.model', string='Model', required=True, ondelete='cascade')
    fields_ids = fields.Many2many('ir.model.fields', help='''Selecting fields is mandatory when using POST and PUT 
    methods and when using Excel report type in REPORT method''')
    report_id = fields.Many2one("ir.actions.report")
    report_template_name = fields.Char(related="report_id.report_name")
    report_type = fields.Selection([('excel', 'EXCEL'), ('pdf', 'PDF')])
    report_response_type = fields.Selection([('url', 'URL'), ('file', 'File')])
    domain = fields.Char()
    model_name = fields.Char(related="model_id.model")
    sort_by_field = fields.Many2one('ir.model.fields',
                                    domain="[('model_id','=',model_id),('ttype','!=','one2many'),('ttype','!=',"
                                           "'binary')]")
    sort_by_order = fields.Selection([('ASC', 'Ascending'), ('DESC', 'Descending')])
    request_preview = fields.Text()
    body_preview = fields.Text()
    response_preview = fields.Text()

    _sql_constraints = [
        ('unique_api', 'UNIQUE(name,method,model_id)',
         "It appears that you've already created an API using the same"
         " method and model. Please review your existing "
         "API configurations to ensure there are no duplicates")
    ]

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('description'):
                vals['description'] = capwords(vals.get('description'))
            if not vals.get('description') and vals.get('name'):
                vals['description'] = capwords(vals.get('name').replace("_", " "))
            print("vals_list", vals)
        return super().create(vals_list)

    def write(self, vals):
        if vals.get('description'):
            vals['description'] = capwords(vals.get('description'))
        return super().write(vals)

    @api.onchange('model_id')
    def _onchange_model(self):
        for record in self:
            if record.model_id:
                record.fields_ids = None
                record.report_id = None
                record.report_response_type = None

    @api.onchange('name')
    def _onchange_name(self):
        for record in self:
            if record.name:
                record.name = record.name.replace(" ", "_").lower()

    @api.onchange('method')
    def _onchange_method(self):
        for record in self:
            record.report_type = None
            record.report_response_type = None

    @api.onchange('method', 'model_id')
    def _onchange_required_fields(self):
        for record in self:
            if record.model_id and record.method == 'post':
                required_fields = record.model_id.field_id.filtered(lambda rec: rec.required)
                if required_fields:
                    record.fields_ids = required_fields.ids

    @api.onchange('name', 'method', 'report_response_type', 'report_type')
    def _onchange_request_response_preview(self):
        for record in self:
            report = ''
            has_id = ''
            if record.method == 'delete' or record.method == 'put':
                has_id = '/{int:id}'
            if record.method == 'report':
                method = 'GET '
                if record.report_response_type == 'file':
                    report = 'report_file/'
                    record.response_preview = "%s File" % record.report_type.upper()
                if record.report_response_type == 'url':
                    report = 'report/'
                    record.response_preview = '''{\n"jsonrpc": "2.0",\n"id": id,\n"result": {\n\t"success": "true",\n\t"error": "",\n\t"data":"url""}\n}'''
            else:
                method = record.method.upper() + ' '
            record.request_preview = method
            if record.name:
                record.request_preview += self.get_base_url() + '/api/' + report + record.api_name + '/' + record.name + has_id

    @api.onchange('method', 'fields_ids', 'model_id')
    def _onchange_body_response_preview(self):
        for record in self:
            record.response_preview = '''{\n"jsonrpc": "2.0",\n"id": id,\n"result": {\n\t"success": "true",
            \n\t"error": "",\n\t"data":\n\t}\n}'''
            response_data = ""
            if record.method == 'get':
                record.body_preview = '''{\n\t"page_size": {int:page_size},\n\t"page_number": {int:page_number}\n}'''
                if record.fields_ids:
                    fields = record.fields_ids
                else:
                    fields = record.model_id.field_id
                response_data = '[\n'
                for field in fields:
                    response_data += '''\t\t"%s": {%s:%s_value},\n''' % (field.name, field.ttype, field.name)
                response_data = replace_last(response_data, ',', '\n')
                response_data += '''\t\t"total_records": {int:total_records}\n\t\t"total_pages": {int:total_records}\n\t]'''
            else:
                if record.fields_ids and (record.method == 'post' or record.method == 'put'):
                    record.body_preview = '{\n'
                    for field in record.fields_ids:
                        record.body_preview += '''\t"%s": {%s:%s_value},\n''' % (field.name, field.ttype, field.name)
                    record.body_preview = replace_last(record.body_preview, ',', '\n}')
                if record.method == 'post':
                    response_data = '''{"ids":[id]}'''
                if record.method == 'put' or record.method == 'delete':
                    response_data = '''{"id":id}'''

            record.response_preview = insert_after(record.response_preview, response_data, '"data":')

    def api_action(self, method, user, record_id=None, vals=None):
        model_obj = self.env[self.model_id.model]
        model_fields = self.fields_ids.mapped('name')
        if vals and method != 'GET':
            if vals.get('data'):
                vals = vals.get('data')
                output_data = []
                for item in vals:
                    filtered_item = {key: format_data(self.model_id, key, item[key]) for key in model_fields if
                                     item.get(key)}
                    output_data.append(filtered_item)
                vals = output_data
            else:
                vals = {key: format_data(self.model_id, key, vals[key]) for key in model_fields if vals.get(key)}
        model_obj = model_obj.with_user(user)
        if method == 'GET':
            domain_list = ast.literal_eval(self.domain)  # convert str to list
            if record_id:
                return model_obj.browse(record_id).read(model_fields)
            else:
                sort_by = '%s %s' % (self.sort_by_field.name, self.sort_by_order) if self.sort_by_field else None
                result = model_obj.search_read(domain=domain_list, fields=model_fields,
                                               order=sort_by)
                if vals.get('page_size') and vals.get('page_number'):
                    total_records = len(result)
                    pages = [result[i:i + vals.get('page_size')] for i in
                             range(0, len(result), vals.get('page_size'))]
                    total_pages = len(pages)
                    result = pages[vals.get('page_number') - 1]
                    result.insert(len(result), {'total_records': total_records, "total_pages": total_pages})
                return result
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
                    ids = ','.join(map(str, record_id))
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
