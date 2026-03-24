from odoo import models, fields
from odoo.exceptions import ValidationError

class HrContract(models.Model):
    _inherit = 'hr.contract'

    project_allocation_ids = fields.One2many(
        'employee.project.allocation',
        'contract_id',
        string="Project Allocation"
    )
    
    # DEDUCTIONS
    oil_deduction = fields.Monetary(string="Oil Deduction")
    loan_advance_deduction = fields.Monetary(string="Loan/Advance Deduction")
    penalty_deduction = fields.Monetary(string="Penalty")
    medical_insurance_deduction = fields.Monetary(string="Medical Insurance Deduction")
    provident_fund_deduction = fields.Monetary(string="Provident Fund Deduction")
    tax_deduction = fields.Monetary(string="Tax Deduction")
    other_deductions = fields.Monetary(string="Other Deductions")
    
    # ADDITIONS
    overtime_addition = fields.Monetary(string="Overtime Addition")
    taxable_transport_allowance = fields.Monetary(string="Taxable Transport Allowance")
    position_allowance = fields.Monetary(string="Position Allowance")
    house_allowance = fields.Monetary(string="House Allowance")
    non_taxable_transport_allowance = fields.Monetary(string="Non Taxable Transport Allowance")
    hardship_allowance = fields.Monetary(string="Hardship Allowance")
    risk_allowance = fields.Monetary(string="Risk Allowance")
    other_allowances = fields.Monetary(string="Other Allowances")

    def action_open(self):
        res = super().action_open()

        for contract in self:
            allocations = contract.project_allocation_ids
            total = sum(allocations.mapped('percentage'))

            if allocations and round(total, 2) != 100:
                raise ValidationError(
                    f"Contract allocation must be 100% (current: {total}%)"
                )

        return res