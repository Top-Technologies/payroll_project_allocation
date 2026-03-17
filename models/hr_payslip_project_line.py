from odoo import models, fields

class PayslipProjectLine(models.Model):
    _name = 'hr.payslip.project.line'
    _description = 'Payslip Project Distribution'

    payslip_id = fields.Many2one('hr.payslip', ondelete='cascade')

    employee_id = fields.Many2one('hr.employee')

    analytic_account_id = fields.Many2one(
        'account.analytic.account',
        string="Project"
    )

    percentage = fields.Float()
    amount = fields.Monetary()

    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.company.currency_id
    )