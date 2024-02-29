// Copyright (c) 2024, Jagadeesan and contributors
// For license information, please see license.txt

frappe.ui.form.on('Tax Computation', {
    type_of_regim: function(frm) {
        var type_of_regim = frm.doc.type_of_regim;
        var income = frm.doc.income;

        if (type_of_regim === "New Regim") {
            if (income) {
                calculate_tds_new_regim(frm, income);
            }
        } else if (type_of_regim === "Old Regim") {
            if (income) {
                calculate_tds_old_regim(frm, income);
            }
        } else {
            frm.set_value('tds', 0); 
        }
    },
    
    type_of_regim: function(frm) {
        var type_of_regim = frm.doc.type_of_regim;
        var income = frm.doc.income;

        if (type_of_regim === "New Regim") {
            if (income) {
                calculate_tds_new_regim(frm, income);
            }
        } else if (type_of_regim === "Old Regim") {
            if (income) {
                calculate_tds_old_regim(frm, income);
            }
        } else {
            frm.set_value('tds', 0); 
        }
    },
    
    end_date: function(frm) {
        var employee = frm.doc.employee;
        var start_date = frm.doc.start_date;
        var end_date = frm.doc.end_date;

        if (employee && start_date && end_date) {
            frappe.call({
                method: 'revoh.revoh.doctype.tax_computation.tax_computation.get_gross_pay',
                args: {
                    'employee': employee,
                    'start_date': start_date,
                    'end_date': end_date
                },
                callback: function(response) {
                    var gross_pay = response.message;
                    if (gross_pay) {
                        frm.set_value('gross_pay', gross_pay);
                        frm.set_value('income', gross_pay-50000);

                        var type_of_regim = frm.doc.type_of_regim;
                        var income = frm.doc.income;

                        if (type_of_regim === "New Regim" && income) {
                            calculate_tds_new_regim(frm, income);
                        } else if (type_of_regim === "Old Regim" && income) {
                            calculate_tds_old_regim(frm, income);
                        }
                    } else {
                        frappe.msgprint('No gross pay found for the selected employee between the given dates.');
                    }
                }
            });
        } else {
            frappe.msgprint('Please select employee, start date, and end date.');
        }
    }
});

function calculate_tds_new_regim(frm, income) {
    var tds = 0; 

    if (income >= 300001 && income <= 600000) {
        tds = income * 0.05;
    } else if (income >= 600001 && income <= 900000) {
        tds = income * 0.10;
    } else if (income >= 900001 && income <= 1200000) {
        tds = income * 0.05;
    }

    frm.set_value('tds', tds);
}

function calculate_tds_old_regim(frm, income) {
    var tds = 0; 
    if (income >= 250001 && income <= 500000) {
        tds = income * 0.05;
    } else if (income >= 500001 && income <= 1000000) {
        tds = income * 0.20;
    } else if (income > 1000000) {
        tds = income * 0.30;
    }

    frm.set_value('tds', tds);
}
