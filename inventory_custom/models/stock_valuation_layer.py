from odoo import api, fields, models

class StockValuationLayer(models.Model):
    _inherit = "stock.valuation.layer"

    item_number = fields.Char(compute="_compute_item_number")
    qty_available = fields.Float(related="product_id.qty_available")#contains negative numbers
    picking_code = fields.Selection(related="stock_move_id.picking_code")
    uom_qty = fields.Float(related="stock_move_id.product_uom_qty")
    product_qty = fields.Float(related="stock_move_id.product_qty")
    available_stock = fields.Float(compute="_compute_calc_availability")
    inward = fields.Float(compute="_compute_calc_inward")
    outward = fields.Float(compute="_compute_calc_outward")
    def _compute_item_number(self):
        for record in self:
            record.item_number = record.product_id.default_code

    def _compute_calc_inward(self):
        for record in self:
            if record.picking_code == 'incoming':
                record.inward = record.product_qty
            else:
                record.inward = 0
    def _compute_calc_outward(self):
        for record in self:
            if record.picking_code == 'outgoing':
                record.outward = record.product_qty
            else:
                record.outward = 0
    def _compute_calc_availability(self):
        for record in self:
            record.available_stock = record.qty_available - record.outward + record.inward
