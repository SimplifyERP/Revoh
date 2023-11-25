// Copyright (c) 2023, Jagadeesan and contributors
// For license information, please see license.txt
frappe.ui.form.on('Proforma Invoice', {
	
	onload:function(frm){
		if(frm.doc.company){
			frm.call("get_company_address_name")
		}
	},
	refresh:function(frm){
		if(frm.doc.docstatus == 1){
			frm.add_custom_button(__('Sales Order'), function() {frm.trigger("make_sales_order")}, __('Create')); 
			frm.add_custom_button(__('Sales Invoice'), function() {frm.trigger("make_sales_invoice")}, __('Create'));
		}
		if(frm.doc.customer_address || frm.doc.shipping_address_name){
			frm.trigger("get_shipping_address_html_format")
			frm.trigger("get_customer_address_html_format")
		}
		if(frm.doc.contact_person){
			frm.trigger("get_contact_html_format")
		}
		if(frm.doc.company_address_name){
			frm.trigger("get_company_html_format")
		}
	},
	make_sales_order() {
		frappe.model.open_mapped_doc({
			method: 'revoh.revoh.doctype.proforma_invoice.proforma_invoice.make_sales_order',
			frm: cur_frm
		})
	},
	make_sales_invoice() {
		frappe.model.open_mapped_doc({
			method:'revoh.revoh.doctype.proforma_invoice.proforma_invoice.make_sales_invoice',
			frm: cur_frm
		})
	},
	before_save:function(frm){
		if(!frm.doc.__islocal){
			frm.trigger("get_shipping_address_html_format")
			frm.trigger("get_customer_address_html_format")
			frm.trigger("get_contact_html_format")
			frm.trigger("get_company_html_format")
			frm.refresh()
		}
	},
	validate:function(frm){
		frm.trigger("items_table_update")
		if(!frm.doc.sales_taxes_and_charges_template){
			$.each(frm.doc.sales_taxes_and_charges,function(i,v){
				cur_frm.get_field("sales_taxes_and_charges").grid.grid_rows[v.idx-1].remove();
			})
		}
		frm.trigger("sales_taxes_and_charges_template")
	},
	items_table_update(frm){
		$.each(frm.doc.items,function(i,v){
			if(v.rate){
				v.base_rate = v.rate
				v.net_rate = v.rate
				v.base_net_rate = v.rate
			}
			if(v.amount){
				v.base_amount = v.amount
				v.net_amount = v.amount
				v.base_net_amount = v.amount
				v.gross_profit = v.amount
			}
		})
	},
	customer(frm){
		if(frm.doc.customer){
			frm.call('get_address_name')
		}
	},
	sales_taxes_and_charges_template(frm){
		if(frm.doc.sales_taxes_and_charges_template){
			frappe.call({
				method:'revoh.revoh.doctype.proforma_invoice.proforma_invoice.get_taxes',
				args:{
					taxes:frm.doc.sales_taxes_and_charges_template,
					net_total:frm.doc.net_total
				},
				callback(r){
					frm.clear_table('sales_taxes_and_charges')
					$.each(r.message,function(i,v){
							frm.add_child('sales_taxes_and_charges',{
								'charge_type':v.charge_type,
								'account_head':v.account_head, 
								'description':v.description,
								'rate':v.rate,
								'tax_amount':v.tax_amount,
								'total':v.total,
								'account_currency':v.account_currency
							})
						frm.refresh_field('sales_taxes_and_charges')
					})
					frm.call("tax_calculation")
				}
			})
		}
	},
	additional_discount_percentage(frm){
		if(frm.doc.additional_discount_percentage){
			if(frm.doc.apply_additional_discount_on == "Grand Total"){
				frm.trigger("discount_applied_on_grand_total")	
			}
			else if(frm.doc.apply_additional_discount_on == "Net Total"){
				frm.call("get_discount_net_total")
			}
		}
	},
	apply_additional_discount_on(frm){
		if(frm.doc.apply_additional_discount_on == "Grand Total"){
			if(frm.doc.additional_discount_percentage){
				frm.trigger("discount_applied_on_grand_total")
				
			}	
		}
		else if((frm.doc.apply_additional_discount_on == "Net Total")){
			if(frm.doc.additional_discount_percentage){
				frm.call("get_discount_net_total")
				
			}
		}
		else{
			frm.set_value("additional_discount_amount_company_currency","")
			frm.set_value("additional_discount_percentage",0.0)
		}
	},
	discount_applied_on_grand_total(frm){
		frappe.call({
			method:'revoh.revoh.doctype.proforma_invoice.proforma_invoice.get_discount_grand_total',
			args:{
				grand_total:frm.doc.grand_total_company_currency,
				discount_percent:frm.doc.additional_discount_percentage,
			},
			callback(r){
				if(r.message){
					$.each(r.message,function(i,v){
						frm.set_value("additional_discount_amount_company_currency",v.additional_discount_amount)
						frm.set_value('grand_total_company_currency',v.grand_total_change_on_discount)
					})
				}
			}
		})
	},
	get_shipping_address_html_format(frm){
		if(frm.doc.shipping_address_name){
			frappe.call({
				method:'revoh.revoh.doctype.proforma_invoice.proforma_invoice.shipping_address_html_format',
				args:{
					shipping_address:frm.doc.shipping_address_name
				},
				callback(r){
					frm.fields_dict.shipping_address.$wrapper.empty().append(r.message)
				}
			})
		}
	},
	get_customer_address_html_format(frm){
		if(frm.doc.customer_address){
			frappe.call({
				method:'revoh.revoh.doctype.proforma_invoice.proforma_invoice.customer_address_html_format',
				args:{
					customer:frm.doc.customer_address
				},
				callback(r){
					frm.fields_dict.address.$wrapper.empty().append(r.message)
				}
			})
		}
	},
	get_contact_html_format(frm){
		if(frm.doc.contact_person){
			frappe.call({
				method:'revoh.revoh.doctype.proforma_invoice.proforma_invoice.contact_html_format',
				args:{
					contact:frm.doc.contact_person
				},
				callback(r){
					frm.fields_dict.contact.$wrapper.empty().append(r.message)
				}
			})

		}
	},
	get_company_html_format(frm){
		if(frm.doc.company_address_name){
			frappe.call({
				method:'revoh.revoh.doctype.proforma_invoice.proforma_invoice.company_html_format',
				args:{
					company:frm.doc.company_address_name
				},
				callback(r){
					frm.fields_dict.company_address.$wrapper.empty().append(r.message)
				}
			})

		}
	},
	total_taxes_and_charges(frm){
		var total_taxes_and_charges = 0
		$.each(frm.doc.sales_taxes_and_charges,function(i,v){ total_taxes_and_charges += v.tax_amount; })
		frm.set_value('total_taxes_and_charges_company_currency',total_taxes_and_charges)	
	},
	grand_total(frm){
		var grand_total = 0
		$.each(frm.doc.sales_taxes_and_charges,function(i,v){ grand_total += v.total; })
		frm.set_value('grand_total_company_currency',grand_total)
		
	}
});

frappe.ui.form.on('Proforma Invoice Item', {
	item_code:function(frm,cdt,cdn){
		var row = locals[cdt][cdn]
		row.delivery_date = frm.doc.date
		frappe.call({
			method:'revoh.revoh.doctype.proforma_invoice.proforma_invoice.uom_conversion_factor',
			args:{
				item:row.item_code
			},
			callback(r){
				if(r.message){
					row.conversion_factor = r.message
				}
			}
		})
		frm.refresh_field("items")
	},
	qty: function(frm, cdt, cdn) {
		var total_qty = 0
		$.each(frm.doc.items, function(i, d) { total_qty += d.qty; });
		frm.set_value("total_quantity", total_qty);

		//the below code again trigger on qty will change
		var row = locals[cdt][cdn]
		if(row.rate > 0.0){
			row.amount = row.qty * row.rate
			//the below code again trigger on qty will change
			var total_amount = 0
			$.each(frm.doc.items, function(i, d) { total_amount += d.amount; });
			frm.set_value("total", total_amount);
			frm.set_value("net_total", total_amount);
			frm.set_value("grand_total_company_currency", total_amount);
		}
		else{
			row.amount = 0.0
			frm.set_value("total", 0.0);
			frm.set_value("net_total", 0.0);
			frm.set_value("grand_total_company_currency", 0.0);
		}

		// //the below code is after save the document again the items will add net_total,sales and taxes table and grand_total with tax rate updated
		// if(!frm.doc.__islocal){
		// 	frm.call("update_tax_and_grand_total")
			
		// }
    },
	rate:function(frm,cdt,cdn){
		var row = locals[cdt][cdn]
		row.amount = row.qty * row.rate
		row.net_rate = row.rate
		frm.refresh_field("items")

		//the below code will get the amount to set in total field
		var total_amount = 0
		$.each(frm.doc.items, function(i, d) { total_amount += d.amount; });
		frm.set_value("total", total_amount);
		frm.set_value("net_total", total_amount);
		frm.set_value("grand_total_company_currency", total_amount);

		// the below code is after save the document again the items will add net_total,sales and taxes table and grand_total with tax rate updated
		// if(!frm.doc.__islocal){
		// 	frm.call("update_tax_and_grand_total")
		// }	
	},
	before_items_remove: function(frm, cdt, cdn) {
		var deleted_row = frappe.get_doc(cdt, cdn);
		var total_qty = frm.doc.total_quantity - deleted_row.qty
		frm.set_value("total_quantity", total_qty);

		var deleted_row = frappe.get_doc(cdt, cdn);
		var total_amount = frm.doc.total - deleted_row.amount
		frm.set_value("total", total_amount);
		frm.set_value("net_total", frm.doc.total);
	},
	
})

frappe.ui.form.on('Sales Taxes and Charges', {
	before_sales_taxes_and_charges_remove:function(frm,cdt,cdn){
		var deleted_row = frappe.get_doc(cdt, cdn);
		var grand_total = frm.doc.grand_total - deleted_row.total
	}
})

