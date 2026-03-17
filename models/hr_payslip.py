from odoo import models, fields
from odoo.exceptions import ValidationError
from odoo.tools import float_round

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

            if round(total_percentage, 2) != 100:
                raise ValidationError("Project allocation must equal 100%")

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

            distribution = {}

            for line in slip.project_line_ids:

                project = line.analytic_account_id

                if not project.budget_currency_id:
                    raise ValidationError(
                        f"Project {project.name} has no budget currency set."
                    )

                # ✅ Convert salary to project currency
                converted_amount = slip.currency_id._convert(
                    line.amount,
                    project.budget_currency_id,
                    slip.company_id,
                    slip.date_to
                )

                # ✅ CHECK BUDGET LIMIT
                if project.consumed_amount + converted_amount > project.budget_amount:
                    raise ValidationError(
                        f"Budget exceeded for project {project.name}"
                    )

                # ✅ UPDATE CONSUMED AMOUNT
                project.consumed_amount += converted_amount

                # ✅ Prepare analytic distribution
                distribution[str(project.id)] = line.percentage / 100

            # ✅ Apply analytic distribution to journal entries
            for move_line in slip.move_id.line_ids:
                if move_line.account_id.internal_group == 'expense':
                    move_line.analytic_distribution = distribution

        return res