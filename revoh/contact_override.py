import frappe
from frappe.contacts.doctype.contact.contact import Contact


class CustomContact(Contact):

    def before_save(self):
        for address_link in self.links:
            if address_link.link_doctype == "Customer":
                frappe.db.set_value('Customer',address_link.link_name,'custom_contact_name',self.name)
                 