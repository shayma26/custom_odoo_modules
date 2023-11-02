from odoo import fields, models

class EstatePropertyTag(models.Model):
    _name = "estate.property.tag"
    _description = "property tags"
    _order = "name"

    _sql_constraints = [
        ('unique', 'UNIQUE(name)', 'The name must be unique')
    ]

    name = fields.Char(required=True)
    color = fields.Integer()