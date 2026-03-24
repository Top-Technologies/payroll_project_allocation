# from odoo import models, fields

# class AnalyticAccount(models.Model):
#     _inherit = 'account.analytic.account'

#     budget_amount = fields.Monetary(
#         string="Budget Amount"
#     )

#     budget_currency_id = fields.Many2one(
#         'res.currency',
#         string="Budget Currency"
#     )

#     consumed_amount = fields.Monetary(
#         string="Consumed Amount",
#         readonly=True
#     )

#     remaining_amount = fields.Monetary(
#         string="Remaining Budget",
#         compute="_compute_remaining",
#         store=True
#     )
#     fund_source = fields.Char(string="Fund Source")

#     def _compute_remaining(self):
#         for rec in self:
#             rec.remaining_amount = rec.budget_amount - rec.consumed_amount