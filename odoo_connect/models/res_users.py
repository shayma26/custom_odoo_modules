# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.http import request
import time
import jwt

#exp time one day
exp_time = 86400


class ResPartner(models.Model):
    _inherit = 'res.users'

    def get_token(self, validator, aud=None, email=None, partner_id=None):

        payload = {
            "aud": aud or validator.audience,
            "iss": validator.issuer,
            "exp": time.time() + exp_time,
        }
        if email:
            payload["email"] = email
        if partner_id:
            payload["id"] = partner_id
        access_token = jwt.encode(
            payload, key=validator.secret_key, algorithm=validator.secret_algorithm
        )
        return "Bearer " + access_token

    @api.model
    def user_login(self, args):
        validator = self.env["auth.jwt.validator"].sudo().search([("name", "=", "user_auth")])
        responseData = {'success': False, 'data': None}
        if 'email' not in args or 'password' not in args:
            responseData['success'] = False
            responseData['error'] = _('Params error')
        if 'email' in args and 'password' in args:
            try:
                login = args.get('email')
                password = args.get('password')
                user_sudo = self.sudo().search(
                    [('login', '=', login)])
                if not user_sudo:
                    responseData['success'] = False
                    responseData['error'] = _('Wrong login/password')
                else:
                    if validator.partner_id_strategy == 'id':
                        token = self.get_token(validator, partner_id=user_sudo.partner_id.id)
                    else:
                        token = self.get_token(validator, email=user_sudo.email)
                    uid = request.session.authenticate(request.session.db, login, password)
                    if uid:
                        user_data = {
                            "id": uid,
                            "name": user_sudo.name,
                            # "imgUrl":user_sudo.avatar_128,

                        }
                    if user_data:
                        responseData["token"] = token
                        responseData['data'] = user_data
                        responseData['success'] = True
                    else:
                        responseData['success'] = False
                        responseData['error'] = {'code': 405, 'message': _('Authentication Failed.')}
            except Exception as e:
                responseData['success'] = False
                responseData['error'] = e
        return responseData


