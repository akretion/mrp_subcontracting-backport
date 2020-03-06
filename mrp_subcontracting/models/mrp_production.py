# Copyright (C) 2013  Renato Lima - Akretion
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models, fields, api, _
from odoo.tools import float_is_zero
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    @api.multi
    @api.depends('state', 'product_id', 'qty_produced')
    def _compute_product_price(self):
        """Compute Production Order Costs"""
        super(MrpProduction, self)._compute_product_price()
        for p in self:
            whouse = self.env['stock.warehouse'].browse(self.company_id.id)
            if whouse.subcontracting_type_id == p.picking_type_id:
                cost_op_price = 0.00
                moves = p.move_finished_ids.filtered(
                    lambda b: b.quantity_done and b.state == 'done')
                if moves:
                    if moves[0].move_dest_ids:
                        if moves[0].move_dest_ids[0].purchase_line_id:
                            cost_op_price = (moves[0].move_dest_ids[0].purchase_line_id.price_unit)

                    p.product_cost_operation = cost_op_price * p.qty_produced
                    p.product_cost_total += p.product_cost_operation
                    p.product_cost_unit = (p.product_cost_total / p.qty_produced)

    move_finished_ids = fields.One2many(
        comodel_name='stock.move',
        inverse_name='production_id',
        string='Finished Products',
        copy=False,
        states={'done': [('readonly', True)],
                'cancel': [('readonly', True)]},
        domain=lambda self: self._move_finished_domain('output'))

    return_move_finished_ids = fields.One2many(
        comodel_name='stock.move',
        inverse_name='production_id',
        string='Finished Products Returned',
        copy=False,
        states={'done': [('readonly', True)],
                'cancel': [('readonly', True)]},
        domain=lambda self: self._move_finished_domain('return'))

    def _move_finished_domain(self, move_type='output'):
        domain = [('scrapped', '=', False)]
        operator = 'in'
        if move_type == 'return':
            operator = 'not in'

        subcontract_locs = self.env['res.partner'].search(
            []).mapped('property_stock_subcontractor')

        loc_ids = [self.env.ref('stock.stock_location_stock').id]
        if subcontract_locs:
            loc_ids += subcontract_locs.ids
        domain.append(('location_dest_id', operator, loc_ids))
        return domain

    @api.multi
    def button_confirm(self):
        super(MrpProduction, self).button_confirm()

        for prod in self:
            for finish_move in prod.move_finished_ids:
                for move_dest in finish_move.move_dest_ids:
                    if move_dest.is_subcontract:
                        pickings_assigned = prod.get_pickings_by_domain(
                            domain=('state', 'in', ('assigned', 'confirmed')))

                        for picking in pickings_assigned:
                            is_backorders = picking._check_backorder()
                            if is_backorders:
                                UserError(
                                    _('You can not assign this Work Order %s because '
                                      'the Components Partial '
                                      'Avaliable') % prod.name)

                            picking.action_done()

                        prod.write({'state': 'progress'})

                        return prod.open_produce_product()

    @api.multi
    def post_inventory(self):
        result = super(MrpProduction, self).post_inventory()
        self._compute_product_price()
        for prod in self:
            move_finisheds = prod.move_finished_ids.filtered(
                lambda x: x.state in ('done',))
            for mf in move_finisheds:
                move_dests = mf.move_dest_ids.filtered(
                    lambda x: x.is_subcontract and x.state not in ('done','cancel'))
                if move_dests:
                    for md in move_dests:
                        md.write({'price_unit': prod.product_cost_unit})

        return result
