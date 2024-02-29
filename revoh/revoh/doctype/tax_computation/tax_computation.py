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
	current_date = start_date
	while current_date <= end_date:
		first_day = frappe.utils.data.get_first_day(current_date)
		last_day = frappe.utils.data.get_last_day(current_date)
		sql_query = """SELECT SUM(gross_pay) as total_gross_pay FROM `tabSalary Slip` WHERE employee = %s AND start_date >= %s AND end_date <= %s"""
		result = frappe.db.sql(sql_query, (employee, first_day, last_day), as_dict=True)
		if result and result[0].total_gross_pay:
			gross_pay_sum += result[0].total_gross_pay
		current_date = frappe.utils.data.add_months(current_date, 1)
		
	return gross_pay_sum
