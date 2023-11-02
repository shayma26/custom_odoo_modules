from odoo import models, fields, api
from dateutil.relativedelta import relativedelta


class FleetVehicleBook(models.Model):
    _name = "fleet.vehicle.book"
    _rec_name = 'seq'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    _sql_constraints = [('check_book_duration', 'CHECK(end_date > start_date AND start_date > booking_date)',
                         'Please enter valid dates')]

    rent_type = fields.Selection([('day', 'Days'), ('hour', 'Hours'), ('km', 'Kilometers')], default='day', required=True)
    nb_hours = fields.Integer(default=0, compute="_compute_nb_hours", store=True)
    nb_days = fields.Integer(default=0, compute="_compute_nb_days", store=True)
    nb_km = fields.Float(default=0.0)
    state = fields.Selection(
        [('draft', 'Draft'),
         ('confirm', 'Confirm'),
         ('open', 'In progress'),
         ('invoice', 'Invoice'),
         ('done', 'Done'),
         ('canceled', 'Canceled')], default='draft', tracking=True)
    booking_date = fields.Datetime(default=fields.Datetime.now())
    start_date = fields.Datetime(required=True, tracking=True)
    end_date = fields.Datetime(required=True, tracking=True)
    deposit = fields.Float(required=True)
    customer_id = fields.Many2one('res.partner', tracking=True)
    driver = fields.Boolean()
    driver_id = fields.Many2one(related="vehicle_id.driver_id", store=True, default=None)
    vehicle_id = fields.Many2one("fleet.vehicle", required=True, tracking=True)
    vehicle_model_id = fields.Many2one(related="vehicle_id.model_id", store=True)
    seq = fields.Char(default='BOOK/xxx', readonly=True)
    vehicle_rent_km = fields.Float(related="vehicle_id.rent_km", store=True)
    vehicle_rent_day = fields.Float(related="vehicle_id.rent_day", store=True)
    vehicle_rent_hour = fields.Float(related="vehicle_id.rent_hour", store=True)
    invoice_id = fields.Many2one("account.move")
    total_price = fields.Float(string="Total", compute="_compute_total_price", store=True)


    @api.model
    def create(self, values):
        values['seq'] = self.env['ir.sequence'].next_by_code('fleet.vehicle.book')
        return super(FleetVehicleBook, self).create(values)

    @api.depends('rent_type','start_date','end_date')
    def _compute_nb_days(self):
        for record in self:
            if record.end_date and record.start_date:
                days = abs((record.end_date - record.start_date).days)
                print("days ",days)
                record.nb_days = days

    @api.depends('rent_type','start_date','end_date','nb_days')
    def _compute_nb_hours(self):
        for record in self:
            if record.end_date and record.start_date:
                hours = abs((record.end_date - record.start_date).seconds)/3600 + record.nb_days * 24
                print("hours", hours)
                record.nb_hours = hours

    @api.depends('rent_type','nb_hours','nb_km','nb_days','vehicle_rent_hour','vehicle_rent_day','vehicle_rent_km')
    def _compute_total_price(self):
        for record in self:
            print(record.rent_type)
            if record.rent_type == 'hour':
                record.total_price = record.nb_hours * record.vehicle_rent_hour
            elif record.rent_type == 'day':
                record.total_price = record.nb_days * record.vehicle_rent_day
            elif record.rent_type == 'km':
                record.total_price = record.nb_km * record.vehicle_rent_km
            else:
                record.total_price = 0
            print("total", record.total_price)
    def action_book_confirm(self):
        print("confirm")
        vehicle = self.env['fleet.vehicle'].browse(self.vehicle_id).id
        for record in self:
            record.state = 'confirm'
            vehicle.state = 'in_progress'
        return True

    def action_book_open(self):
        print("In Progress")
        for record in self:
            record.state = 'open'
        return True

    def action_book_invoice(self):
        print("Invoice")
        journal = self.env["account.journal"].search([("type", "=", "sale")], limit=1)
        print("journal",journal)
        # *******************************
        #TODO account_id is missing
        if not journal:
            print("journal does not exist")
            journal_data = {
                'name': 'Car Rent journal',
                'type': 'sale',
                'code': 'RCj',
            }
            journal = self.env['account.journal'].create(journal_data)
            print("new jornal", journal)
            #*******************************
        for record in self:
            invoice = self.env['account.move'].create({
                    'partner_id': record.customer_id.id,
                    'move_type': "out_invoice",
                    'journal_id': journal.id,
                    'invoice_date': fields.Date.today(),
                    'invoice_line_ids': [
                        (
                            0,  # 0 for creation
                            0,  # 0 for creation
                            {
                                'name': record.vehicle_id.name,
                                'quantity': 1.0,
                                'price_unit': record.nb_hours * record.vehicle_rent_hour + record.nb_days * record.vehicle_rent_day + record.nb_km * record.vehicle_rent_km,
                                'product_id': self.env.ref('fleet_custom.rent_car_service').id,
                            }
                        ),
                        (
                            0,
                            0,
                            {
                                'name': 'Deposit',
                                'quantity': 1.0,
                                'price_unit': record.deposit,
                                'product_id': self.env.ref('fleet_custom.rent_car_service').id

                            }
                        )
                    ]
            })
            record.invoice_id = invoice.id
            print(record.invoice_id)
            record.state = 'invoice'
        return True

    def action_book_done(self):
        print("Done")
        vehicle = self.env['fleet.vehicle'].browse(self.vehicle_id).id
        for record in self:
            record.state = ('done')
            vehicle.state = 'unavailable'
        return True

    def action_cancel_car(self):
        print("Cancel")
        vehicle = self.env['fleet.vehicle'].browse(self.vehicle_id).id
        for record in self:
            record.state = ('canceled')
            vehicle.state = 'available'


    def open_invoice(self):
        val = {
            'view_mode': 'form',
            'view_id': self.env.ref('account.view_move_form').id,
            'res_model': 'account.move',
            'context': "{'move_type':'out_invoice'}",
            'type': 'ir.actions.act_window',
            'res_id': self.invoice_id.id,
             }
        return val
