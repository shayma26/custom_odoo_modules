# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


class RestAPICustomController(http.Controller):

    @http.route(['/api/report_file/<api_name>/<name>/<record_id>', '/api/report_file/<api_name>/<name>'],
                auth='jwt_user_auth', methods=['GET'])
    def get_report_file(self, api_name, name, record_id=None):
        partner_id = request.jwt_partner_id
        user = request.env['res.users'].search([('partner_id', '=', partner_id)])
        res = {
            'success': False,
            'error': '',
            'data': None
        }
        try:
            get_api = request.env['odoo.connect.api'].search([('name', '=', api_name)])
            result = get_api.api_line_ids.filtered(
                lambda rec: rec.name == name and rec.method == 'report' and rec.report_response_type == 'file')
            if record_id:
                ids = [int(i) for i in record_id.split(',')]
            else:
                ids = ""
        except Exception as e:
            res['error'] = 'Error in API: %s' % str(e)
            return res
        if not result:
            res['error'] = 'API does not exist'
            return res
        try:
            report = result.api_action(method='report', user=user, record_id=ids)
        except Exception as e:
            res['error'] = 'Error accrued when calling Api %s' % str(e)
            return res
        if result.report_type == 'pdf':
            pdfhttpheaders = [('Content-Type', 'application/pdf'), ('Content-Length', len(report))]
            return request.make_response(report, headers=pdfhttpheaders)
        elif result.report_type == 'excel':
            xlsxhttpheaders = [
                ('Content-Type', 'application/vnd.openxmlformats-'
                                 'officedocument.spreadsheetml.sheet'),
                ('Content-Length', len(report)),
            ]
            return request.make_response(report, headers=xlsxhttpheaders)

    @http.route(['/api/<api_name>/<name>', '/api/<api_name>/<name>/<int:record_id>'], auth='jwt_user_auth', type='json')
    def odoo_connect_apis(self, api_name, name, record_id=None, **kwargs):
        partner_id = request.jwt_partner_id
        user = request.env['res.users'].search([('partner_id', '=', partner_id)])

        res = {
            'success': False,
            'error': '',
            'data': None
        }
        method = request.httprequest.method
        vals = request.get_json_data()
        if method not in ['GET', 'POST', 'PUT', 'DELETE']:
            res['error'] = 'Method Not allowed'
            return res
        if method in ['PUT', 'DELETE'] and (not record_id or not vals):
            res['error'] = 'Invalid data'
            return res
        try:
            get_api = request.env['odoo.connect.api'].search([('name', '=', api_name)])
            result = get_api.api_line_ids.filtered(lambda rec: rec.name == name and rec.method == method.lower())
        except Exception as e:
            res['error'] = 'API does not exist: %s' % str(e)
            return res
        if not result:
            res['error'] = 'API does not exist'
            return res
        try:
            print("size", kwargs.get('page_size'))
            if kwargs.get('page_size') and kwargs.get('page_number'):
                print("size",kwargs.get('page_size'),"number",kwargs.get('page_number'))
                vals['page_size'] = kwargs.get('page_size')
                vals['page_number'] = kwargs.get('page_number')
            print("vals",vals)
            data = result.api_action(method, user, record_id, vals)
        except Exception as e:
            res['error'] = 'Error accrued when calling Api %s' % str(e)
            return res
        res.update({'success': True, 'data': data})
        return res

    @http.route(['/api/report/<api_name>/<name>/<record_id>', '/api/report/<api_name>/<name>'],
                auth='jwt_user_auth', methods=['GET'], type='json')
    def get_report(self, api_name, name, record_id=None):
        partner_id = request.jwt_partner_id
        user = request.env['res.users'].search([('partner_id', '=', partner_id)])
        res = {
            'success': False,
            'error': '',
            'data': None
        }
        try:
            get_api = request.env['odoo.connect.api'].search([('name', '=', api_name)])
            result = get_api.api_line_ids.filtered(lambda rec: rec.name == name and rec.method == 'report' and rec.report_response_type == 'url')
            if record_id:
                ids = [int(i) for i in record_id.split(',')]
            else:
                ids = ""
        except Exception as e:
            res['error'] = 'Error in API: %s' % str(e)
            return res
        if not result:
            res['error'] = 'API does not exist'
            return res
        try:
            report = result.api_action(method='report', user=user, record_id=ids)
        except Exception as e:
            res['error'] = 'Error accrued when calling Api %s' % str(e)
            return res
        res.update({'success': True, 'data': report})
        return res

    @http.route('/documentation/<int:api_id>', website=True, auth='user', methods=['GET'])
    def index(self, api_id):
        res = {
            'success': False,
            'error': ''
        }
        try:
            api = request.env['odoo.connect.api'].browse(api_id)
            if not api:
                request.redirect('/')
        except Exception as e:
            res['error'] = 'Error accrued when fetching data %s' % str(e)
            return res
        return request.render('odoo_connect.documentation', {
            "api": api,
            "host_url": request.httprequest.host_url
        })

    @http.route('/report_xlsx/<api_name>/<name>', auth='jwt_user_auth', methods=['GET'])
    def get_excel(self, api_name, name):
        report_name = 'odoo_connect.api_data_report_xls'
        report = request.env['ir.actions.report']._get_report_from_name(report_name)
        context = dict(request.env.context)
        get_api = request.env['odoo.connect.api'].search([('name', '=', api_name)])
        api_line = get_api.api_line_ids.filtered(
            lambda rec: rec.name == name)
        data = report.with_context(context)._render_xlsx(report_name, api_line.id, None)[0]
        xlsxhttpheaders = [
            ('Content-Type', 'application/vnd.openxmlformats-'
                             'officedocument.spreadsheetml.sheet'),
            ('Content-Length', len(data)),
        ]
        return request.make_response(data, headers=xlsxhttpheaders)
