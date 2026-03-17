{
    'name': 'Payroll Project Allocation',
    'version': '1.0',
    'depends': [
        'hr_payroll',
        'hr_work_entry_contract_enterprise',
        'project',
        'analytic',
        'account'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/contract_view.xml',
        'views/employee_project_allocation_view.xml',
    ],
    'installable': True,
}