# -*- coding: utf-8 -*-
from datetime import datetime
import secrets


def format_data(model_obj, key, value):
    field = model_obj.field_id.filtered(lambda rec: rec.name == key)
    if field.ttype == 'many2one':
        record = model_obj.env[field.relation].browse(value)
        if not record.exists():
            raise ValueError('Wrong value for Attribute %s' % key)
    elif field.ttype == 'one2many':
        formatted_list = []
        for item in value:
            formatted_item = (0, 0, item)
            formatted_list.append(formatted_item)
        return formatted_list
    elif field.ttype == 'many2many':
        formatted_list = []
        for item in value:
            if isinstance(item, dict):
                formatted_item = (0, 0, item)
                formatted_list.append(formatted_item)
            else:
                record = model_obj.env[field.relation].browse(item)
                if not record.exists():
                    raise ValueError('Wrong value for Attribute %s' % key)
                else:
                    formatted_item = (4, item, 0)
                    formatted_list.append(formatted_item)
        return formatted_list
    elif field.ttype == 'date':
        if not datetime.strptime(value, "%d-%m-%Y"):
            raise ValueError('Wrong value for Attribute %s' % key)
    elif field.ttype == 'datetime':
        if not datetime.strptime(value, "%d-%m-%Y, %H:%M:%S"):
            raise ValueError('Wrong value for Attribute %s' % key)
    return value


def replace_last(s, old, new):
    parts = s.rsplit(old, 1)
    if len(parts) > 1:
        return parts[0] + new + parts[1]
    else:
        return s


def insert_after(s, insert, after):
    index = s.find(after)
    if index != -1:
        return s[:index + len(after)] + insert + s[index + len(after):]
    else:
        return s


def generate_token():
    # Generate a random token (hexadecimal)
    return secrets.token_hex(16)
