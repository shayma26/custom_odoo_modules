from odoo import api, fields, models

from odoo.exceptions import UserError, AccessError, ValidationError

from odoo.tools import float_compare


class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "estate offers"
    _order = "price desc"  # to order offers by price from the highest to lowest or you can order your list in the tree view with "default_order" attribute

    _sql_constraints = [
        ('positive_amounts', 'CHECK(price>0)', 'The price should be a positive number')]

    price = fields.Float()
    status = fields.Selection([('accepted', 'Accepted'), ('refused', 'Refused')], copy=False)
    partner_id = fields.Many2one('res.partner', required=True)
    property_id = fields.Many2one('estate.property', required=True)
    validity = fields.Integer(default=7, string="Validity (days)")
    date_deadline = fields.Date(compute="_compute_date_deadline", inverse="_inverse_date_deadline", string="Deadline")
    create_date = fields.Datetime(readonly=True, default=fields.Datetime.now)

    property_type_id = fields.Many2one(related="property_id.property_type_id", store=True)
    #related fields are like computed fields, they are not stored automatically unless you set it true manually

    @api.model
    def create(self, vals):
        property = self.env['estate.property'].browse(vals['property_id'])
        #if property.mapped('offer_ids.price'):
            #if float_compare(self.price, min(property.mapped('offer_ids.price')), precision_rounding=0.01) == -1:
             #   raise UserError('You cannot create an offer with a lower amount that than an existing offer')
        property.state = 'received'
        return super().create(vals)

    @api.depends("create_date", "validity")
    def _compute_date_deadline(self):
        for record in self:
            record.date_deadline = fields.Date.to_date(fields.Datetime.add(record.create_date, days=record.validity))

    def _inverse_date_deadline(self):
        for record in self:
            record.validity = abs((record.date_deadline - fields.Date.to_date(record.create_date)).days)

    def action_accept(self):
        for record in self:
            if ('accepted') in record.mapped('property_id.offer_ids.status'):
                raise UserError(('Only one offer can be accepted!'))
            else:
                record.status = ('accepted')
                record.property_id.state = ('accepted')
                record.property_id.buyer_id = record.partner_id
                record.property_id.selling_price = record.price
        return True

    def action_refuse(self):
        for record in self:
            if record.status == ('accepted'):
                record.property_id.buyer_id = None
                record.property_id.selling_price = None
            record.status = ('refused')
        return True
