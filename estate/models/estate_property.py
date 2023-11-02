from odoo import api, fields, models
from odoo.exceptions import UserError, AccessError, ValidationError
from odoo.tools import float_compare, float_is_zero


class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "estate properties"
    _order = "id desc"

    _sql_constraints = [
        ('positive_amounts', 'CHECK(expected_price>0)', 'The price should be a positive number'),
        ('positive_areas', 'CHECK(garden_area >= 0 AND living_area >= 0 )', 'The areas should be positive numbers'),
        ('positive_numbers', 'CHECK(bedrooms >= 0 AND facades >= 0 )',
         'The number of bedrooms and facades should be positive')
    ]

    name = fields.Char(required=True)
    description = fields.Text(string="Description")
    postcode = fields.Char()
    date_availability = fields.Date(string="Available From", copy=False,
                                    default=lambda self: fields.Date.add(fields.Date.today(),
                                                                         months=3))  # won't be copied when the record is duplicated
    expected_price = fields.Float(required=True)
    selling_price = fields.Float(readonly=True, copy=False)  # read only
    bedrooms = fields.Integer(default=2)
    living_area = fields.Integer(string="Living Area (sqm)")
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer(string="Garden Area (sqm)")
    garden_orientation = fields.Selection(
        string='Garden Orientation',
        selection=[('north', 'North'), ('south', 'South'), ('east', 'East'), ('west', 'West')],
    )
    active = fields.Boolean(default=True)  # reserved for pre-defined behaviors
    state = fields.Selection(
        [('new', 'New'), ('received', 'Offer Received'), ('accepted', 'Offer Accepted'), ('sold', 'Sold'),
         ('canceled', 'Canceled')], required=True, copy=False, default=('new'))
    property_type_id = fields.Many2one('estate.property.type', string="Type", )
    buyer_id = fields.Many2one('res.partner', copy=False, string="Buyer", readonly=True)
    salesperson_id = fields.Many2one('res.users', default=lambda self: self.env.user, string="Salesperson")
    tag_ids = fields.Many2many('estate.property.tag', string="Tags")
    offer_ids = fields.One2many('estate.property.offer', 'property_id')

    total_area = fields.Integer(compute="_compute_total_area", string="Total Area (sqm)")
    best_price = fields.Float(compute="_compute_best_price", string="Best Offer", default=0)

    # it is not possible to search on a computed field unless a search method is defined or the option store is set to True.
    # when store=True, every time the dependecies are changed, the computed fields are automatically recomputed for ALL THE RECORDS referring to it which can cost a degraded performance

    @api.depends("living_area", "garden_area")  # The object self is a recordset => an ordered collection of records.
    def _compute_total_area(self):
        for record in self:  # Iterating over self gives the records one by one, where each record is itself a
            # collection of size 1
            record.total_area = record.living_area + record.garden_area

    @api.depends("offer_ids.price")
    def _compute_best_price(self):
        for record in self:
            if (record.offer_ids):
                self.best_price = max(record.mapped('offer_ids.price'))
            else:
                self.best_price = 0

    # A compute method sets the field while an inverse method sets the field’s dependencies.

    # In previous sample self corresponds to the record currently edited on the form.
    # When in on_change context all work is done in the cache. So you can alter RecordSet inside your function without being
    # worried about altering database. That’s the main difference with @api.depends

    @api.onchange("garden")
    def _onchange_garden(self):
        if (self.garden):
            self.garden_area = 10
            self.garden_orientation = ('north')
        else:
            self.garden_area = 0
            self.garden_orientation = None

    #------------------ check before saving ------------------

    @api.constrains('selling_price', 'expected_price')
    def _check_price(self):
        for record in self:
            if float_compare(record.selling_price, record.expected_price * 0.9, precision_rounding=0.01) == -1:
                if not float_is_zero(record.selling_price, precision_rounding=0.01):
                    raise ValidationError(
                        "The selling price must be at least 90% of the expected price. You must reduce the expected "
                        "price if you want to accept this offer.")

   #-------------------- Python Inheritance --------------------
    @api.ondelete(at_uninstall=False)
    def _unlink_new_canceled(self):
        for record in self:
            if record.state != 'new' and record.state != 'canceled':
                raise UserError("Only new and canceled properties can be deleted.")

    #------------------ button actions ------------------

    def action_sold(self):
        for record in self:
            if (record.state == ('canceled')):
                # return {
                #   'effect': {
                #      'fadeout': 'slow',
                #     'message': 'Canceled properties cannot be sold',
                #   }
                # }
                raise UserError(('Canceled properties cannot be sold'))
            record.state = ('sold')
        return True

    def action_cancel(self):
        for record in self:
            if (record.state == ('sold')):
                raise UserError(('Sold properties cannot be canceled'))
            else:
                record.state = ('canceled')
        return True
