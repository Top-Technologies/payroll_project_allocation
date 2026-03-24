from odoo import models, fields
from odoo.exceptions import ValidationError
from odoo.tools import float_round, float_compare

class HrPayslipLine(models.Model):
    _inherit = 'hr.payslip.line'

    analytic_distribution = fields.Json(string="Analytic Distribution")

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

        for slip in self:

            slip.compute_project_allocation()

            if not slip.project_line_ids:
                continue

            # ✅ Build analytic distribution dict
            distribution = {}
            for proj in slip.project_line_ids:
                distribution[str(proj.analytic_account_id.id)] = proj.percentage / 100

            # ✅ Apply to ALL payslip lines (or filter if needed)
            for line in slip.line_ids:
                line.analytic_distribution = distribution

        return res

   