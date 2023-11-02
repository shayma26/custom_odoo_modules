from odoo import models, fields, api

class StockQuantityInherited(models.TransientModel):
    _inherit = 'stock.quantity.history'

    def action_print_report(self):
        stock = self.env['stock.move'].search_read([('create_date','<',self.inventory_datetime),('warehouse_id','!=',False)])
        data = {
            'form': self.read()[0],#a list of only one item
            'stock': stock,
        }
        # ref `module_name.report_id` as reference.
        return self.env.ref('inventory_custom.stock_quantity_report').report_action(self, data=data)