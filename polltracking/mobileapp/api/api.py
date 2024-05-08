import frappe
from frappe import auth
from frappe.utils import get_site_name
import base64
from datetime import datetime 
from frappe import _

@frappe.whitelist(allow_guest=True )
def mobile_login(usr,pwd):
    try:
        login_manager=frappe.auth.LoginManager()
        login_manager.authenticate(user=usr,pwd=pwd)
        login_manager.post_login()
    except frappe.exceptions.AuthenticationError:
        frappe.clear_messages()
        frappe.local.response['message']={
            "success_key":0,
            "message":"Authentication Error!"
        }
        return
    
    api_generate=generate_keys(frappe.session.user)
    user=frappe.get_doc('User',frappe.session.user)
    datetime_obj = datetime.strptime(user.last_login, "%Y-%m-%d %H:%M:%S.%f")

    # Format the datetime object
    user_last_login = datetime_obj.strftime("%Y-%m-%d %H:%M:%S")
    reporter = frappe.get_doc("Reporter",user.username)
    frappe.local.response['message']={
            "success_key":1,
            "message":"Authentication Success",
            "sid":frappe.session.sid,
            "frappe_token":api_generate['token'],
            "email":user.email,
            "first_name":user.first_name,
            "middle_name":user.middle_name,
            "last_name":user.last_name,
            "full_name":user.full_name,
            "username":user.username,
            "reporter":reporter,
            "role_profile_name":user.role_profile_name,
            "gender":user.gender,
            # "birth_date":user.birth_date,
            "phone":user.phone,
            "location":user.location,
            "mobile_no":user.mobile_no,
            "last_login":user_last_login,
            "banner_image":user.banner_image,
            "image":str(user.user_image),
            "site_name":get_site_name(frappe.local.request.host),
            "roles": frappe.get_roles(),
        }
    
    
@frappe.whitelist( allow_guest=True )    
def generate_keys(user):
    user_details = frappe.get_doc("User", user)
    api_secret = None
    if not user_details.api_key:
        api_key = frappe.generate_hash(length=15)
        user_details.api_key = api_key
    if not user_details.api_secret:
        api_secret = frappe.generate_hash(length=15)
        user_details.api_secret = api_secret
    else:
        api_secret=user_details.get_password('api_secret')
        user_details.api_secret = api_secret
        
    user_details.save(ignore_permissions=True)

    api_key_bytes = user_details.api_key.encode('ascii')
    api_secret_bytes = api_secret.encode('ascii')
    base64_bytes = base64.b64encode(api_key_bytes+b':'+api_secret_bytes)
    token = base64_bytes.decode('ascii')
    
    return {"token": token}

# @frappe.whitelist(allow_guest=True)
# def registered_user_profile_details(email):
#     reporter = frappe.get_doc("Reporter",email)
#     user = frappe.get_doc("User",reporter.user)
#     # Convert string to datetime object
#     datetime_obj = datetime.strptime(user.last_login, "%Y-%m-%d %H:%M:%S.%f")

#     # Format the datetime object
#     user_last_login = datetime_obj.strftime("%Y-%m-%d %H:%M:%S")
#     return {
#             "reporter":reporter,
#             # "user":user
#             # "user":{
#             #     "name":user.name,
#             #     "first_name":user.first_name,
#             #     "email":user.email,
#             #     "username":user.username,
#             #     "full_name":user.full_name,
#             #     "language":user.language,
#             #     "last_login":user_last_login,
#             #     "role_profiles":user.role_profiles,
#             #     "roles":user.roles                
#             #      }
#             }
     
@frappe.whitelist(allow_guest=True)
def reporter_to_key_in_polliing_count(data):
    return data


@frappe.whitelist(allow_guest=True)
def get_constituency_and_candidates(user_email):
    # Authenticate user
    # user = frappe.session.user
    user = user_email
    if not user or not  "News Reporter" in frappe.get_roles(user):
        frappe.throw(_("Access Denied"), frappe.PermissionError)
    user = frappe.get_doc("User",user)
    reporter = frappe.get_all("Reporter", filters={"user_name": user.username}, fields=["*"])

    # Retrieve reporter's constituency
    constituency = frappe.get_value("Reporter", reporter[0].user_name, "constituency")
    
    # Fetch candidates and parties for the constituency
    candidates = frappe.get_all("Election Candidate", filters={"constituency": constituency}, fields=["candidate_name", "party","party_image","votes"])
    
    # Prepare response
    response = {
        "constituency": constituency,
        "candidates": candidates
    }
    return response
# @frappe.whitelist(allow_guest=True)
# @frappe.whitelist( allow_guest=True ) 
# def get_sales_invoice_list():
#     # Get all sales invoice list 
#     sales_invoices = frappe.get_all('sales invoice', fields=['*'],order_by='creation desc')
#     sales_invoice_list = []

#     # Iterate over shipments
#     for sales_invoice in sales_invoices:
#         # Get items for the current shipment
#         items = frappe.get_all('Items', fields=['*'], filters={'parent': sales_invoice.name})

#         # Create a dictionary entry for the current shipment
#         sales_invoice_dict = {
#             'sales_invoice_details': sales_invoice,
#             'items': items
#         }

#         # Add the shipment_dict to the result_dict using the shipment name as the key
#         sales_invoice_list.append(sales_invoice_dict)
#         frappe.local.response['message'] = sales_invoice_list
   
