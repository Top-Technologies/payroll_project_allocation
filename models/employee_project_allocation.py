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



    wage = fields.Monetary(

        string="Wage",

        related='contract_id.wage',

        store=True,

        readonly=True

    )



    currency_id = fields.Many2one(

        'res.currency',

        related='contract_id.currency_id',

        store=True,

        readonly=True

    )



    allocated_amount = fields.Monetary(

        string="Project Amount",

        compute='_compute_allocated_amount',

        store=True

    )





    analytic_account_id = fields.Many2one(

        'account.analytic.account',

        string="Project",

        required=True,

        domain="[('plan_id', '!=', False)]"

    )



    percentage = fields.Float(required=True)



    total_percentage = fields.Float(

        string="Total Allocation (%)",

        compute="_compute_total_percentage"

    )



    allocation_status = fields.Selection([

        ('ok', 'OK'),

        ('under', 'Under Allocation'),

        ('over', 'Over Allocation')

    ], compute="_compute_status")



    @api.depends('total_percentage')

    def _compute_status(self):

        for rec in self:

            if rec.total_percentage == 100:

                rec.allocation_status = 'ok'

            elif rec.total_percentage < 100:

                rec.allocation_status = 'under'

            else:

                rec.allocation_status = 'over'



    @api.depends('contract_id', 'percentage')

    def _compute_total_percentage(self):

        for rec in self:

            if rec.contract_id:

                allocations = self.search([

                    ('contract_id', '=', rec.contract_id.id)

                ])

                rec.total_percentage = sum(allocations.mapped('percentage'))

            else:

                rec.total_percentage = 0



    @api.depends('wage', 'percentage')

    def _compute_allocated_amount(self):

        for rec in self:

            rec.allocated_amount = (rec.wage * rec.percentage) / 100 if rec.percentage else 0



    @api.constrains('percentage', 'contract_id')

    def _check_percentage(self):

        for rec in self:

            allocations = self.search([

                ('contract_id', '=', rec.contract_id.id)

            ])

            total = sum(allocations.mapped('percentage'))

            if total != 100:

                raise ValidationError("Total allocation must be exactly 100%")

    

    @api.constrains('percentage')

    def _check_percentage_range(self):

        for rec in self:

            if rec.percentage < 0 or rec.percentage > 100:

                raise ValidationError("Percentage must be between 0 and 100.")