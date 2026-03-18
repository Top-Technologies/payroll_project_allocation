from odoo import models, fields
from odoo.exceptions import ValidationError

class HrContract(models.Model):
    _inherit = 'hr.contract'

    project_allocation_ids = fields.One2many(
        'employee.project.allocation',
        'contract_id',
        string="Project Allocation"
    )
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