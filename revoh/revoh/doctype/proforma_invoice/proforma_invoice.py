# Copyright (c) 2023, Jagadeesan and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import money_in_words
import re
import math
from frappe.model.mapper import get_mapped_doc
from frappe.utils import add_days, cint, cstr, flt, get_link_to_form, getdate, nowdate, strip_html
from frappe.contacts.doctype.address.address import get_company_address
from frappe.model.utils import get_fetch_values
from erpnext.accounts.party import get_party_account
from erpnext.stock.doctype.item.item import get_item_defaults
from erpnext.setup.doctype.item_group.item_group import get_item_group_defaults


class ProformaInvoice(Document):
	
	def validate(self):
		self.grant_commission_make_false()
		self.validate_grand_and_net_total_without_discount_and_without_tax()
		self.validate_grand_and_net_total_without_discount_and_with_tax()
		self.get_decimal_value()
		self.get_amount_money_in_words()

	def grant_commission_make_false(self):
		for item in self.items:
			item.grant_commission = 0

	def validate_grand_and_net_total_without_discount_and_without_tax(self):
		if self.sales_taxes_and_charges_template == "":
			if self.apply_additional_discount_on == "" and self.additional_discount_percentage == 0.0:
				self.net_total = self.total
				self.grand_total_company_currency = self.total
				self.total_taxes_and_charges_company_currency = 0.0
			
	def validate_grand_and_net_total_without_discount_and_with_tax(self):
		taxes_and_charges = 0.0
		grand_total_after_taxes = 0.0
		if self.sales_taxes_and_charges_template:
			if self.apply_additional_discount_on == "" and self.additional_discount_percentage == 0.0:
				for tax in self.sales_taxes_and_charges:
					self.net_total = self.total

					tax.tax_amount = ((int(tax.rate)/100) * float(self.total)) 
					tax.total = tax.tax_amount + float(self.total)

					self.tax_calculation()

					taxes_and_charges += tax.tax_amount
					self.total_taxes_and_charges_company_currency = taxes_and_charges

					grand_total_after_taxes += tax.total
					self.grand_total_company_currency = grand_total_after_taxes
					
	def get_decimal_value(self):
		if self.disable_rounded_total == 0:
			decimal_value = math.modf(self.grand_total_company_currency)
			value_1,value_2 = decimal_value
			self.rounding_adjustment_company_currency = value_1
			self.rounded_total_company_currency = value_2
		else:
			self.rounded_total_company_currency = self.grand_total_company_currency

	def get_amount_money_in_words(self):
		if self.grand_total_company_currency > 0:
			company_currency = frappe.db.get_value('Company',{'name':self.company},['default_currency'])
			self.in_words_company_currency = money_in_words(self.grand_total_company_currency,company_currency)

	@frappe.whitelist()
	def get_address_name(self):
		customer_address_name = frappe.get_doc('Customer',self.customer)
		if customer_address_name.custom_address_id:
			address_name = frappe.db.get_value('Address',{'name':customer_address_name.custom_address_id},['name','is_shipping_address'])
			if address_name[1] == 1:
				self.shipping_address_name = address_name[0]
			else:
				self.customer_address = address_name[0]

	@frappe.whitelist()
	def get_company_address_name(self):
		address_name = frappe.db.get_value('Company',{'name':self.company},['custom_address_name'])
		if address_name:
			self.company_address_name = address_name


	@frappe.whitelist()
	def tax_calculation(self):
		try:
			for idx,item in enumerate(self.sales_taxes_and_charges):
				self.sales_taxes_and_charges[idx+1].total = self.sales_taxes_and_charges[idx+1].tax_amount + item.total
		except:
			pass
			
	@frappe.whitelist()
	def change_taxes_and_charges(self):
		if self.apply_additional_discount_on == "Net Total" and self.additional_discount_percentage > 0.0:
			for tax in self.sales_taxes_and_charges:
				if self.net_total:
					tax.tax_amount = (tax.rate/100) * float(self.net_total)
					tax.total = tax.tax_amount + self.net_total	

	@frappe.whitelist()
	def get_discount_net_total(self):
		taxes_and_charges = 0.0
		grand_total_after_taxes = 0.0
		if self.apply_additional_discount_on == "Net Total":
			if self.additional_discount_percentage > 0.0:
				additional_discount_amount = ((int(self.additional_discount_percentage)/100) * float(self.total))
				self.additional_discount_amount_company_currency = additional_discount_amount
				net_total_change_on_discount = float(self.total) - additional_discount_amount
				self.net_total = net_total_change_on_discount
			
				for tax in self.sales_taxes_and_charges:
					tax.tax_amount = ((int(tax.rate)/100) * float(net_total_change_on_discount)) 
					tax.total = tax.tax_amount + float(net_total_change_on_discount)
				
					self.tax_calculation()
					taxes_and_charges += tax.tax_amount
					self.total_taxes_and_charges_company_currency = taxes_and_charges

					grand_total_after_taxes += tax.total
					self.grand_total_company_currency = grand_total_after_taxes



#here its starting the frappe call codes
@frappe.whitelist()		
def get_discount_grand_total(grand_total,discount_percent):
	datalist = []
	data = {}
	additional_discount_amount = ((int(discount_percent)/100) * float(grand_total))
	grand_total_change_on_discount = float(grand_total) - additional_discount_amount

	data.update({
		'additional_discount_amount':additional_discount_amount,
		'grand_total_change_on_discount':grand_total_change_on_discount,
	})
	datalist.append(data.copy())
	return datalist

@frappe.whitelist()
def get_taxes(taxes,net_total):
	datalist = []
	data = {}
	sales_taxes = frappe.get_doc('Sales Taxes and Charges Template',taxes)
	for tax in sales_taxes.taxes:
		if net_total:
			tax_amount = (tax.rate / 100) * float(net_total)
			total = tax_amount + float(net_total)
		else:
			tax_amount = float(0.0)	
			total = float(0.0)
		data.update({
			'charge_type':tax.charge_type,
			'account_head':tax.account_head, 
			'description':tax.description,
			'rate':tax.rate,
			'tax_amount':tax_amount,
			'total':total,
	 		'account_currency':tax.account_currency
		})
		datalist.append(data.copy())
	return datalist	

@frappe.whitelist()
def uom_conversion_factor(item):
	get_item_uom = frappe.get_doc("Item",item)
	for uom in get_item_uom.uoms:
		conversion_factor = uom.conversion_factor
		return conversion_factor	
	
@frappe.whitelist()
def shipping_address_html_format(shipping_address):
	get_address = frappe.get_doc('Address',shipping_address)
	data  = ""
	data = "<table border = '2' width= 80%>"
	data += "<tr><td>%s</td><tr>"%(get_address.address_title)
	data += "<tr><td>%s</td><tr>"%(get_address.address_type)
	data += "<tr><td>%s</td><tr>"%(get_address.address_line1)
	data += "<tr><td>%s</td><tr>"%(get_address.address_line2)
	data += "<tr><td>%s</td><tr>"%(get_address.city)
	data += "<tr><td>%s</td><tr>"%(get_address.state)
	data += "<tr><td>%s</td><tr>"%(get_address.country)
	data += "<tr><td>%s</td><tr>"%(get_address.pincode)
	data += '</table>'
	return data	

@frappe.whitelist()
def customer_address_html_format(customer):
	get_address = frappe.get_doc('Address',customer)
	data  = ""
	data = "<table border = '2' width= 80%>"
	data += "<tr><td>%s</td><tr>"%(get_address.address_title)
	data += "<tr><td>%s</td><tr>"%(get_address.address_type)
	data += "<tr><td>%s</td><tr>"%(get_address.address_line1)
	data += "<tr><td>%s</td><tr>"%(get_address.address_line2)
	data += "<tr><td>%s</td><tr>"%(get_address.city)
	data += "<tr><td>%s</td><tr>"%(get_address.state)
	data += "<tr><td>%s</td><tr>"%(get_address.country)
	data += "<tr><td>%s</td><tr>"%(get_address.pincode)
	data += '</table>'
	return data	

@frappe.whitelist()
def contact_html_format(contact):
	get_contact = frappe.get_doc('Contact',contact)
	data  = ""
	data = "<table border = '2' width= 80%>"
	data += "<tr><td>%s</td><tr>"%(get_contact.first_name)
	data += "<tr><td>%s</td><tr>"%(get_contact.user)
	data += "<tr><td>%s</td><tr>"%(get_contact.address)
	data += "<tr><td>%s</td><tr>"%(get_contact.status)
	data += "<tr><td>%s</td><tr>"%(get_contact.salutation)
	data += "<tr><td>%s</td><tr>"%(get_contact.designation)
	data += "<tr><td>%s</td><tr>"%(get_contact.gender)
	data += "<tr><td>%s</td><tr>"%(get_contact.company_name)
	data += '</table>'
	return data	

@frappe.whitelist()
def company_html_format(company):
	get_address = frappe.get_doc('Address',company)
	data  = ""
	data = "<table border = '2' width= 80%>"
	data += "<tr><td>%s</td><tr>"%(get_address.address_title)
	data += "<tr><td>%s</td><tr>"%(get_address.address_type)
	data += "<tr><td>%s</td><tr>"%(get_address.address_line1)
	data += "<tr><td>%s</td><tr>"%(get_address.address_line2)
	data += "<tr><td>%s</td><tr>"%(get_address.city)
	data += "<tr><td>%s</td><tr>"%(get_address.state)
	data += "<tr><td>%s</td><tr>"%(get_address.country)
	data += "<tr><td>%s</td><tr>"%(get_address.pincode)
	data += '</table>'
	return data	

@frappe.whitelist()
def make_sales_order(source_name, target_doc=None, ignore_permissions=False):
	def postprocess(source, target):
		set_missing_values(source, target)

	def set_missing_values(source, target):
		target.flags.ignore_permissions = True
		target.run_method("set_missing_values")
		target.delivery_date = source.date
		target.taxes_and_charges = source.sales_taxes_and_charges_template
		
	def update_item(source, target, source_parent):
		target.amount = flt(source.amount) - flt(source.billed_amt)
		target.base_amount = target.amount * flt(source_parent.conversion_rate)
		target.qty = (
			target.amount / flt(source.rate)
			if (source.rate and source.billed_amt)
			else source.qty - source.returned_qty
		)
		target.delivery_date = source.delivery_date

	doclist = get_mapped_doc(
		"Proforma Invoice",
		source_name,
		{
			"Proforma Invoice": {
				"doctype": "Sales Order",
				"field_map": {
					"party_account_currency": "party_account_currency",
					"payment_terms_template": "payment_terms_template",
				},
				"field_no_map": ["payment_terms_template"],
				"validation": {"docstatus": ["=", 1]},
			},
			"Proforma Invoice Item": {
				"doctype": "Sales Order Item",
				"field_map": {
					"name": "custom_proforma_detail",
					"parent": "proforma_invoice",
				},
				"postprocess": update_item,
				"condition": lambda doc: doc.qty
				and (doc.base_amount == 0 or abs(doc.billed_amt) < abs(doc.amount)),
			},
			"Sales Taxes and Charges": {"doctype": "Sales Taxes and Charges", "add_if_empty": True},
			"Sales Team": {"doctype": "Sales Team", "add_if_empty": True},
		},
		target_doc,
		postprocess,
		ignore_permissions=ignore_permissions,
	)

	automatically_fetch_payment_terms = cint(
		frappe.db.get_single_value("Accounts Settings", "automatically_fetch_payment_terms")
	)
	if automatically_fetch_payment_terms:
		doclist.set_payment_schedule()

	doclist.set_onload("ignore_price_list", True)

	return doclist


@frappe.whitelist()
def make_sales_invoice(source_name, target_doc=None, ignore_permissions=False):
	def postprocess(source, target):
		set_missing_values(source, target)
		# Get the advance paid Journal Entries in Sales Invoice Advance
		if target.get("allocate_advances_automatically"):
			target.set_advances()

	def set_missing_values(source, target):
		target.flags.ignore_permissions = True
		target.run_method("set_missing_values")
		target.run_method("set_po_nos")
		target.run_method("calculate_taxes_and_totals")

		if source.company_address:
			target.update({"company_address": source.company_address})
		else:
			# set company address
			target.update(get_company_address(target.company))

		if target.company_address:
			target.update(get_fetch_values("Sales Invoice", "company_address", target.company_address))

		# set the redeem loyalty points if provided via shopping cart
		if source.loyalty_points and source.order_type == "Shopping Cart":
			target.redeem_loyalty_points = 1

		target.debit_to = get_party_account("Customer", source.customer, source.company)

	def update_item(source, target, source_parent):
		target.amount = flt(source.amount) - flt(source.billed_amt)
		target.base_amount = target.amount * flt(source_parent.conversion_rate)
		target.qty = (
			target.amount / flt(source.rate)
			if (source.rate and source.billed_amt)
			else source.qty - source.returned_qty
		)

		if source_parent.project:
			target.cost_center = frappe.db.get_value("Project", source_parent.project, "cost_center")
		if target.item_code:
			item = get_item_defaults(target.item_code, source_parent.company)
			item_group = get_item_group_defaults(target.item_code, source_parent.company)
			cost_center = item.get("selling_cost_center") or item_group.get("selling_cost_center")

			if cost_center:
				target.cost_center = cost_center

	doclist = get_mapped_doc(
		"Proforma Invoice",
		source_name,
		{
			"Proforma Invoice": {
				"doctype": "Sales Invoice",
				"field_map": {
					"party_account_currency": "party_account_currency",
					"payment_terms_template": "payment_terms_template",
				},
				"field_no_map": ["payment_terms_template"],
				"validation": {"docstatus": ["=", 1]},
			},
			"Proforma Invoice Item": {
				"doctype": "Sales Invoice Item",
				"field_map": {
					"name": "custom_proforma_detail",
					"parent": "proforma_invoice",
				},
				"postprocess": update_item,
				"condition": lambda doc: doc.qty
				and (doc.base_amount == 0 or abs(doc.billed_amt) < abs(doc.amount)),
			},
			"Sales Taxes and Charges": {"doctype": "Sales Taxes and Charges", "add_if_empty": True},
			"Sales Team": {"doctype": "Sales Team", "add_if_empty": True},
		},
		target_doc,
		postprocess,
		ignore_permissions=ignore_permissions,
	)

	automatically_fetch_payment_terms = cint(
		frappe.db.get_single_value("Accounts Settings", "automatically_fetch_payment_terms")
	)
	if automatically_fetch_payment_terms:
		doclist.set_payment_schedule()

	doclist.set_onload("ignore_price_list", True)

	return doclist