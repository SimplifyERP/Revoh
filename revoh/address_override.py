import frappe


from frappe.contacts.doctype.address.address import Address



class CustomAddress(Address):

    def before_save(self):
        if self.disabled == 0:
            for address_link in self.links:
                if address_link.link_doctype == "Customer":
                    frappe.db.set_value('Customer',address_link.link_name,'custom_address_id',self.name)
                elif address_link.link_doctype == "Company":
                    frappe.db.set_value('Company',address_link.link_name,'custom_address_name',self.name)

                 