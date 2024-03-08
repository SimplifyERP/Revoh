
from frappe import _, get_doc, sendmail, attach_print
from datetime import datetime

def send_salary_slip_email(doc, method):
    employee = get_doc("Employee", doc.employee)
    if employee.personal_email:
        # Convert start_date string to date object
        start_date = datetime.strptime(doc.start_date, '%Y-%m-%d')
        # Format start_date as day month year
        formatted_start_date = start_date.strftime("%B %Y")
        subject = _("Payslip for {0}").format(formatted_start_date)
        message = """
        <p>Hi {0},</p>
        <p>I hope this mail finds you well. Kindly find your Payslip for {1} attached.</p>
        <p>Regards,</p>
        <p>Bhuvanesh G</p>
        <p>Human Resource & Administration</p>
        <address>
            REVOH INNOVATIONS PRIVATE LIMITED,<br>
            First Floor, No. 1FA, IIT Madras Research Park,<br>
            Kanagam Road, Taramani,<br>
            Chennai, Tamil Nadu, 600113<br>
        </address>
        """.format(doc.employee_name, formatted_start_date)
        attachments = []
        attachments.append(attach_print(doc.doctype,doc.name,doc=doc,print_format="Salary Slip",lang="en",letterhead=None,))
        sendmail(
            recipients=employee.personal_email,
            subject=subject,
            message=message,
            attachments=attachments
        )
