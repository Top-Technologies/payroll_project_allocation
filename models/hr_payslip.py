from odoo import models, fields
from odoo.exceptions import ValidationError

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    project_line_ids = fields.One2many(
        'hr.payslip.project.line',
        'payslip_id',
        string="Project Allocation"
    )

    def compute_project_allocation(self):

        for slip in self:

            slip.project_line_ids.unlink()

            gross_salary = sum(
                line.total for line in slip.line_ids
                if line.category_id.code == 'GROSS'
            )

            contract = slip.contract_id

            allocations = contract.project_allocation_ids

            total_percentage = sum(allocations.mapped('percentage'))

            if total_percentage != 100:
                raise ValidationError("Allocation must be 100%")

            for alloc in allocations:

                amount = gross_salary * alloc.percentage / 100

                self.env['hr.payslip.project.line'].create({
                    'payslip_id': slip.id,
                    'analytic_account_id': alloc.analytic_account_id.id,
                    'percentage': alloc.percentage,
                    'amount': amount,
                })

    def compute_sheet(self):
        res = super().compute_sheet()
        self.compute_project_allocation()
        return res

    def action_payslip_done(self):

        res = super().action_payslip_done()

        for slip in self:

            distribution = {}

            for line in slip.project_line_ids:
                distribution[str(line.analytic_account_id.id)] = line.percentage

            for move_line in slip.move_id.line_ids:
                if move_line.account_id.internal_group == 'expense':
                    move_line.analytic_distribution = distribution

        return res