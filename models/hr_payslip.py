from odoo import models

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    def action_payslip_done(self):
        res = super().action_payslip_done()

        for slip in self:
            contract = slip.contract_id

            allocations = contract.project_allocation_ids

            if not allocations:
                continue

            distribution = {}

            for alloc in allocations:

                distribution[str(alloc.analytic_account_id.id)] = alloc.percentage

            move = slip.move_id

            for line in move.line_ids:
                if line.account_id.internal_group == 'expense':

                    line.analytic_distribution = distribution

        return res