# -*- coding: utf-8 -*-
import json
import logging
from odoo import http, _
from odoo.http import request, Response
from odoo.exceptions import AccessError, UserError, AccessDenied

logger = logging.getLogger(__name__)


def deserialise_request_data(data):
    return json.loads(data.decode("utf-8"))


class LoginApi(http.Controller):

    @http.route('/api/login', type='json', methods=['POST'], auth='public', csrf=False, cors="*")
    def user_login(self, **args):
        args = deserialise_request_data(request.httprequest._cached_data)
        return request.env['res.users'].user_login(args)

    @http.route('/api/logout', type='json', methods=['POST'], auth='public', csrf=False, cors="*")
    def user_logout(self, **args):
        try:
            request.session.logout()
            return {'success': True}
        except Exception as e:
            return {'success': False, 'error': e}

    @http.route('/reset/password', type='json', methods=['POST'], auth="jwt_user_auth", csrf=False, cors="*")
    def reset_password(self, **args):
        try:
            args = deserialise_request_data(request.httprequest._cached_data)
            if 'old_password' not in args or 'new_password' not in args:
                return {'success': False, 'error': 'Params Error'}
            try:
                user = request.env["res.users"].sudo().search([('partner_id', '=', request.jwt_partner_id)])
                if request.env['res.users'].with_user(user).change_password(args.get('old_password'),
                                                                            args.get('new_password')):
                    return {'success': True}
            except AccessDenied as e:
                msg = e.args[0]
                if msg == AccessDenied().args[0]:
                    msg = _('The old password you provided is incorrect, your password was not changed.')
            except UserError as e:
                msg = e.args[0]
            return {'success': False, 'error': msg}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    # @http.route('/api/get_action', auth="jwt_user_auth", methods=['GET'], csrf=False, cors="*")
    # def get_action(self, **kw):
    #     responseData = {'success': False, 'data': None}
    #     data = []
    #     if request.httprequest.method == 'GET':
    #         try:
    #             if request.env.user._is_public():
    #                 responseData['success'] = False
    #                 responseData['error'] = _('No user is registred with this id')
    #             else:
    #                 args = deserialise_request_data(request.httprequest._cached_data)
    #                 operationObj = request.env['treatment.action']
    #                 operations_ids = operationObj.sudo().browse(args.get('operations_ids'))
    #                 for operation in operations_ids:
    #                     vals = {
    #                         'id': operation.id,
    #                         'name': operation.name,
    #                         'sequence': operation.sequence,
    #                         'replace_tooth': operation.replace_tooth,
    #                         'replace_racine': operation.replace_racine,
    #                         'img_top_replace': "/web/image?model=treatment.action&id=%s&field=img_top_replace" % (
    #                             operation.id) if operation.img_top_replace else '',
    #                         'img_bottom_replace': "/web/image?model=treatment.action&id=%s&field=img_bottom_replace" % (
    #                             operation.id) if operation.img_bottom_replace else '',
    #                         'racine_bottom_replace': "/web/image?model=treatment.action&id=%s&field=racine_bottom_replace" % (
    #                             operation.id) if operation.racine_bottom_replace else '',
    #                         'racine_top_replace': "/web/image?model=treatment.action&id=%s&field=racine_top_replace" % (
    #                             operation.id) if operation.racine_top_replace else '',
    #                     }
    #                     data.append(vals)
    #                 responseData['data'] = data
    #                 responseData['success'] = True
    #         except Exception as e:
    #             responseData['success'] = False
    #             responseData['error'] = e
    #     return Response(json.dumps(responseData), content_type="application/json", status=200)
