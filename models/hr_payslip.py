from odoo import models, fields
from odoo.exceptions import ValidationError
from odoo.tools import float_round, float_compare

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

            # ✅ Use computed salary (GROSS)
            gross_salary = sum(
                line.total for line in slip.line_ids
                if line.category_id.code == 'GROSS'
            )

            if not gross_salary:
                continue

            contract = slip.contract_id
            allocations = contract.project_allocation_ids

            if not allocations:
                continue

            # ✅ VALIDATION
            total_percentage = sum(allocations.mapped('percentage'))

            if not allocations:
                raise ValidationError(
                    f"No project allocation defined for {slip.employee_id.name}"
                )

            if float_compare(total_percentage, 100, precision_digits=2) != 0:
                raise ValidationError(
                    f"Total allocation for {slip.employee_id.name} must be 100% "
                    f"(current: {total_percentage}%)"
                )

            currency = slip.currency_id
            rounding = currency.rounding

            total_allocated = 0
            lines = []

            # ✅ CALCULATE DISTRIBUTION
            for alloc in allocations:

                amount = float_round(
                    gross_salary * alloc.percentage / 100,
                    precision_rounding=rounding
                )

                total_allocated += amount

                lines.append({
                    'payslip_id': slip.id,
                    'employee_id': slip.employee_id.id,  # ✅ ADD THIS LINE
                    'analytic_account_id': alloc.analytic_account_id.id,
                    'percentage': alloc.percentage,
                    'amount': amount,
                })

            # ✅ HANDLE ROUNDING DIFFERENCE (IMPORTANT IN PRODUCTION)
            difference = float_round(
                gross_salary - total_allocated,
                precision_rounding=rounding
            )

            if difference != 0 and lines:
                lines[0]['amount'] += difference  # adjust first line

            # ✅ CREATE RECORDS
            for line in lines:
                self.env['hr.payslip.project.line'].create(line)


    def compute_sheet(self):
        res = super().compute_sheet()
        self.compute_project_allocation()
        return res

    def action_payslip_done(self):
        res = super().action_payslip_done()

        for slip in self:
            move = slip.move_id

            if not move or not slip.project_line_ids:
                continue

            new_lines = []
            lines_to_remove = self.env['account.move.line']

            for line in move.line_ids:

                # ✅ Only split EXPENSE lines
                if line.account_id.internal_group == 'expense':

                    lines_to_remove |= line

                    for proj in slip.project_line_ids:

                        amount = (line.debit or line.credit) * (proj.percentage / 100)

                        new_lines.append((0, 0, {
                            'name': f"{slip.employee_id.name} - {proj.analytic_account_id.name}",
                            'partner_id': slip.employee_id.address_home_id.id,
                            'account_id': line.account_id.id,
                            'debit': amount if line.debit > 0 else 0.0,
                            'credit': amount if line.credit > 0 else 0.0,
                            'analytic_account_id': proj.analytic_account_id.id,
                            'partner_id': line.partner_id.id,
                        }))

                else:
                    # keep non-expense lines (like payable)
                    new_lines.append((0, 0, {
                        'name': line.name,
                        'account_id': line.account_id.id,
                        'debit': line.debit,
                        'credit': line.credit,
                        'partner_id': line.partner_id.id,
                    }))

            # ✅ Remove old lines and replace
            move.line_ids.unlink()
            move.write({'line_ids': new_lines})

        return res