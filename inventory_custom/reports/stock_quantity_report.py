# -*- coding: utf-8 -*-

from odoo import models, fields, api

class StockQuantityReport(models.AbstractModel):
    #  _name = Use prefix `report.` along with `module_name.report_name`
    _name = 'report.inventory_custom.stock_quantity_report_view'

    @api.model
    def _get_report_values(self, docids, data=None):

        inventory_datetime = data['form']['inventory_datetime']
        stock = data['stock']
        warehouses = self.env['stock.warehouse'].search([])
        docs = []

        for wh in warehouses:
            wh_stock = []
            stock_products = []

            [stock_products.append(x['product_id']) for x in stock if x['product_id'] not in stock_products]
            for p in stock_products:
                inward = 0
                outward = 0
                has_product = False
                for s in stock:
                    if s['warehouse_id'][0] == wh.id and s['state'] == 'done' and s['product_id'][0] == p[0]:
                        has_product = True
                        if s['picking_code'] == "incoming":
                            inward += s['quantity_done']
                        elif s['picking_code'] == "outgoing":
                            outward += s['quantity_done']
                if has_product:
                    product = self.env['product.product'].search([('id', '=', p[0])])
                    open_stock = product.qty_available - inward + outward
                    wh_stock.append({
                            'product_num': product.default_code,
                            'description': product.name,
                            'open_stock': open_stock,
                            'inward': inward,
                            'outward': outward,
                            'avail_stock': product.qty_available,
                            'cost_price': product.standard_price,
                            'value': product.qty_available * product.standard_price,
                            })

            docs.append({
                    'wh_name': wh.name,
                    'company': wh.company_id.name,
                    'location': wh.view_location_id.name,
                    'wh_stock': wh_stock,
                })
        print("docs",docs)

        return {
            'inv_date': inventory_datetime,
            'docs': docs,
        }