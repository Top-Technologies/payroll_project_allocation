from odoo import models, fields

class HrPayslipProjectLine(models.Model):
    _name = 'hr.payslip.project.line'
    _description = 'Payslip Project Allocation'

    payslip_id = fields.Many2one('hr.payslip', ondelete='cascade')

    analytic_account_id = fields.Many2one(
        'account.analytic.account',
        string="Project",
        required=True
    )

    percentage = fields.Float()

    amount = fields.Monetary()

    currency_id = fields.Many2one(
        'res.currency',
        related='payslip_id.currency_id',
        store=True
    )