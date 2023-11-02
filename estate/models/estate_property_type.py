from odoo import api, fields, models


class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "estate types"
    _order = "sequence, name"

    _sql_constraints = [
        ('unique', 'UNIQUE(name)', 'The name must be unique')
    ]

    name = fields.Char(required=True)
    sequence = fields.Integer('Sequence', default=1,
                              help="Used to order types")  # used in combination with the handle widget formanual ordering

    # Relational (for inline view)
    property_ids = fields.One2many("estate.property", "property_type_id", string="Properties")
    offer_ids = fields.One2many("estate.property.offer", "property_type_id")
    offer_count = fields.Integer(compute="_compute_offer_count")

    @api.depends("offer_ids")
    def _compute_offer_count(self):
        for record in self:
            record.offer_count = len(record.offer_ids)
