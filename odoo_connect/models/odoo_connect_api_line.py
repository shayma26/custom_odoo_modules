# -*- coding: utf-8 -*-
import ast
import base64

from odoo.exceptions import ValidationError
from odoo import models, fields, api
from string import capwords
from ..tools.tools import format_data, replace_last, insert_after
from odoo.http import request


class OdooConnectApiLine(models.Model):
    _name = 'odoo.connect.api.line'
    _description = "Odoo API Line"

    name = fields.Char(required=True, help="The name used in the URL to call this line from the API")
    title = fields.Char('Title', help="Name of this API line")
    description = fields.Text(compute='_compute_api_line_description')
    api_name = fields.Char(related="api_id.name", readonly=True)
    api_id = fields.Many2one('odoo.connect.api', readonly=True)
    method = fields.Selection(
        [('get', 'GET'), ('post', 'POST'), ('put', 'PUT'), ('delete', 'DELETE'), ('report', 'REPORT')], required=True,
        default='get')
    model_id = fields.Many2one('ir.model', string='Model', required=True, ondelete='cascade')
    fields_ids = fields.Many2many('ir.model.fields', help='''Selecting fields is mandatory when using POST and PUT 
    methods and when using Excel report type in REPORT method''', domain="[('model_id','=',model_id)]")
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
    accept_attachment = fields.Boolean()

    _sql_constraints = [
        ('unique_api', 'UNIQUE(name,method,model_id)',
         "It appears that you've already created an API using the same"
         " method and model. Please review your existing "
         "API configurations to ensure there are no duplicates")
    ]

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('title'):
                vals['title'] = capwords(vals.get('title'))
            if not vals.get('title') and vals.get('name'):
                vals['title'] = capwords(vals.get('name').replace("_", " "))
        return super().create(vals_list)

    def write(self, vals):
        if vals.get('title'):
            vals['title'] = capwords(vals.get('title'))
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
            record.accept_attachment = None

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
                    record.response_preview = "%s File" % record.report_type.upper() if record.report_type else "File"
                elif record.report_response_type == 'url':
                    report = 'report/'
                    record.response_preview = record.response_preview = ('{\n"jsonrpc": "2.0",\n"id": id,\n"result": {'
                                                                         '\n\t"success": "true",\n\t"error": "",'
                                                                         '\n\t"data":"url"\n\t}\n}')
            else:
                method = record.method.upper() + ' '
            record.request_preview = method
            if record.name:
                record.request_preview += self.get_base_url() + '/api/' + report + record.api_name + '/' + record.name + has_id

    @api.onchange('accept_attachment')
    def _onchange_accept_attachment(self):
        for record in self:
            if record.method == 'post':
                if record.body_preview:
                    if record.accept_attachment:
                        record.body_preview = replace_last(record.body_preview, '\n}',',\n\t"attachment": binary_value\n}')
                    else:
                        record.body_preview = replace_last(record.body_preview,',\n\t"attachment": binary_value\n}','\n}')


    @api.onchange('method', 'fields_ids', 'model_id')
    def _onchange_body_response_preview(self):
        for record in self:
            record.response_preview = ('{\n"jsonrpc": "2.0",\n"id": id,\n"result": {\n\t"success": "true",\n\t"error": '
                                       '"",\n\t"data":\n\t}\n}')
            response_data = ""

            if record.method == 'get':
                record.body_preview = '{\n\t"page_size": int_value, \n\t"page_number": int_value\n}'
                if record.fields_ids:
                    fields = record.fields_ids
                else:
                    fields = record.model_id.field_id
                response_data = '[\n'
                if fields:
                    response_data += '\t\t{\n'
                    for field in fields:
                        response_data += '''\t\t\t"%s": %s_value,\n''' % (field.name, field.ttype)
                response_data = replace_last(response_data, ',', '\n\t\t}')
                response_data += '''\t\t{\n\t\t\t"total_records": int_value\n\t\t\t"total_pages": int_value\n\t\t}\n\t\t]'''
            else:
                if record.fields_ids and (record.method == 'post' or record.method == 'put'):
                    record.body_preview = '{\n'
                    for field in record.fields_ids:
                        record.body_preview += '\t"%s": %s_value,\n' % (field.name, field.ttype)
                    record.body_preview = replace_last(record.body_preview, ',', '\n}')
                if not record.fields_ids:
                    record.body_preview = "Please Select Fields"
                if record.method == 'post':
                    response_data = ' {"ids": [id] }'
                if record.method == 'put' or record.method == 'delete':
                    response_data = ' {"id": id }'
            record.response_preview = insert_after(record.response_preview, response_data, '"data":')

    def _compute_api_line_description(self):
        for record in self:
            if record.method == 'get':
                fields = 'fields: ' + ', '.join(record.fields_ids.mapped('name')) if record.fields_ids else 'all fields.'
                record.description = record.name + '  fetches all the records from the model ' + record.model_name + ' and display them using ' + fields
            elif record.method == 'post':
                record.description = record.name + " will create new record(s) for the model " + record.model_name + " after providing these fields' values in the body: " + ', '.join(
                    record.fields_ids.mapped('name'))
            elif record.method == 'put':
                record.description = record.name + " fetches the records using the specified id(s) from the model " + record.model_name + " and update the following fields: " + ', '.join(
                    record.fields_ids.mapped('name'))
            elif record.method == 'delete':
                record.description = record.name + " fetches all the record having the specified id from the model " + record.model_name + " and delete them."
            elif record.method == 'report':
                if record.report_type == 'excel':
                    record.description = record.name + " returns the Excel " + record.report_response_type + " that contains all the records from the model " + record.model_name + " and display them using the fields: " + ', '.join(
                        record.fields_ids.mapped('name'))
                elif record.report_type == 'pdf':
                    record.description = record.name + " returns the PDF " + record.report_response_type + " that contains the " + record.report_template_name + " report of the model " + record.model_name

    def _create_record_and_check_attach(self, dic, model, ids_list):
        has_attach = False
        attach_data = ""
        if dic.get('attachment'):
            has_attach = True
            attach_data = dic.pop('attachment')
        obj_id = model.create(dic).id
        ids_list.append(obj_id)
        if has_attach:
            self.env['ir.attachment'].create({
                'type': 'binary',
                'name': 'ATTACH-%s-' % fields.Date.today().strftime('%Y-%m-%d'),
                'res_model': self.model_name,
                'res_id': obj_id,
                'datas': attach_data,
            })

    def api_action(self, method, user, record_id=None, vals=None):
        model_obj = self.env[self.model_id.model].with_user(user)
        model_fields = self.fields_ids.mapped('name')
        if vals and method != 'GET':
            if vals.get('data'):
                vals = vals.get('data')
                output_data = []
                for item in vals:
                    filtered_item = {key: format_data(self.model_id, key, item[key]) for key in model_fields if
                                     item.get(key)}
                    if self.accept_attachment and item.get('attachment'):
                        filtered_item['attachment'] = item.get('attachment')
                    output_data.append(filtered_item)
                vals = output_data
            else:
                output_data = {key: format_data(self.model_id, key, vals[key]) for key in model_fields if vals.get(key)}
                if self.accept_attachment and vals.get('attachment'):
                    output_data['attachment'] = vals.get('attachment')
                vals = output_data
        if method == 'GET':
            domain_list = ast.literal_eval(self.domain) if self.domain else []  # convert str to list
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
                    result.append({'total_records': total_records, "total_pages": total_pages})
                return result
        if method == 'POST':
            ids_list = []
            if isinstance(vals, list):
                for val in vals:
                    self._create_record_and_check_attach(val,model_obj,ids_list)
            else:
                self._create_record_and_check_attach(vals,model_obj,ids_list)
            return {'ids': ids_list}
        if method == 'PUT':
            if self.accept_attachment and vals.get('attachment'):
                self.env['ir.attachment'].create({
                    'type': 'binary',
                    'name': 'ATTACH-%s-' % fields.Date.today().strftime('%Y-%m-%d'),
                    'res_model': self.model_name,
                    'res_id': record_id,
                    'datas': vals.get('attachment'),
                })
                vals.pop('attachment')
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
