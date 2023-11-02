from odoo import models, fields


class FleetVehicle(models.Model):
    _inherit = "fleet.vehicle"

    city_id = fields.Many2one('res.city')

    rent_km = fields.Float(string="Rent Per Km")
    rent_hour = fields.Float(string="Rent Per Hour")
    rent_day = fields.Float(string="Rent Per Day")
    book_ids = fields.One2many('fleet.vehicle.book', 'vehicle_id')
    state = fields.Selection(
        [('available', 'Available'), ('in_progress', 'In Progress'), ('unavailable', 'Unavailable')],
        default='available',string="Booking state")
    cost_report = fields.One2many("fleet.vehicle.cost.report","vehicle_id")
    costs = fields.Float(related="cost_report.cost", store=True)

    def action_book_car(self):
        res = self.env["fleet.vehicle.book"].search([('vehicle_id', '=', self.id),('state','!=','done'),('state','!=','canceled')], limit=1)
        if res:
            print("vehicle book found")
            print(res.id)
            val = {
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'view_id': self.env.ref('fleet_custom.fleet_vehicle_book_form').id,
                'name': res.seq,
                'res_model': 'fleet.vehicle.book',
                'domain': [('id', '=', res.id), ('vehicle_id', '=', self.id)],
                'res_id': res.id
            }

            return val
        print("no bookings found")
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'name': res.seq,
            'res_model': 'fleet.vehicle.book',
            'context': {'default_vehicle_id': self.id}
        }

    def show_bookings(self):
        return {
                'type': 'ir.actions.act_window',
                'view_mode': 'tree',
                'view_id': self.env.ref('fleet_custom.fleet_vehicle_book_list').id,
                'res_model': 'fleet.vehicle.book',
                'domain': [('vehicle_id', '=', self.id)],
                'name': self.name
            }