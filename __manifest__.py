{
    'name': 'Payroll Project Allocation',
    'version': '1.0',
    'depends': [
        'hr_payroll',
        'hr',
    'hr_contract',
        'project',
        'analytic',
        'account',
        'account_budget',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/contract_view.xml',
        'views/employee_project_allocation_view.xml',
        'views/hr_payslip_view.xml',
        'views/analytic_account_view.xml',
        'views/hr_payslip_project_line_view.xml',
    ],
    'installable': True,
}