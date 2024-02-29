# Copyright (c) 2024, Jagadeesan and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class TaxComputation(Document):
	pass

@frappe.whitelist()
def get_gross_pay(employee, start_date, end_date):
    start_date = frappe.utils.data.getdate(start_date)
    end_date = frappe.utils.data.getdate(end_date)
    gross_pay_sum = 0
    
    # Fetch salary slips for the specified employee and date range
    salary_slips = frappe.get_list(
        "Salary Slip",
        filters={
            "employee": employee,
            "start_date": (">=", start_date),
            "end_date": ("<=", end_date)
        },
        fields=["name"]
    )
    
    for slip in salary_slips:
        # Fetch earnings for each salary slip where component is "Gross Pay"
        earnings = frappe.get_list(
            "Salary Detail",
            filters={
                "parent": slip.name,
                "parenttype": "Salary Slip",
                "parentfield": "earnings",
                "salary_component": "Gross Pay" 
            },
            fields=["amount"]
        )
        
        if earnings:
            gross_pay_sum += earnings[0].amount
    
    return gross_pay_sum
