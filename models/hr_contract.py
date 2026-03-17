from odoo import models, fields

class HrContract(models.Model):
    _inherit = 'hr.contract'

    project_allocation_ids = fields.One2many(
        'employee.project.allocation',
        'contract_id',
        string="Project Allocation"
    )