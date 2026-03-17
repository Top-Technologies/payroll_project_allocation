from odoo import models, fields, api
from odoo.exceptions import ValidationError

class EmployeeProjectAllocation(models.Model):
    _name = 'employee.project.allocation'
    _description = 'Employee Project Allocation'

    contract_id = fields.Many2one('hr.contract', required=True)

    employee_id = fields.Many2one(
        'hr.employee',
        related='contract_id.employee_id',
        store=True,
        readonly=True
    )


    analytic_account_id = fields.Many2one(
        'account.analytic.account',
        string="Project",
        required=True
    )

    percentage = fields.Float(required=True)

    @api.constrains('percentage', 'contract_id')
    def _check_percentage(self):
        for rec in self:
            allocations = self.search([
                ('contract_id', '=', rec.contract_id.id)
            ])
            total = sum(allocations.mapped('percentage'))
            if total > 100:
                raise ValidationError("Total allocation cannot exceed 100%")