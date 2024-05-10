import frappe
from frappe import auth
from frappe.utils import get_site_name
import base64
from datetime import datetime 
from frappe import _
import json
from frappe.utils import get_url


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


def fetch_initial_candidate_details(user_email):
    users_exists = frappe.db.exists("User", user_email)
    if not users_exists:
        return {"error_msg":"User is not exists"}
    
    user = frappe.get_doc("User",user_email)
    if not user or not  "News Reporter" in frappe.get_roles(user.email):
        frappe.throw(_("Access Denied"), frappe.PermissionError)
    return fetch_reporter_against_polling_details(user)
    
    
def fetch_reporter_against_polling_details(user):
    reporter = frappe.get_all("Reporter", filters={"user_name": user.username}, fields=["*"])
    constituency = frappe.get_value("Reporter", reporter[0].user_name, "constituency")
    # Fetch candidates and parties for the constituency
    candidates = frappe.get_all("Election Candidate", filters={"constituency": constituency}, fields=["candidate_name", "party","party_image","votes"])
    condidate_details = []
    for condidate in candidates:
        condidate_details.append({
            "candidate_name":condidate.candidate_name,
            "party":condidate.party,
            "party_image":get_url()+condidate.party_image,
            "votes":None,
        })
    response = {
            "constituency": constituency,
            "reporter":user.username,
            "round":None,
            "candidates": condidate_details
        }
    return response

def store_votes(user_email, data):
    
    user = frappe.get_doc("User",user_email)
    existing_polling_count = frappe.get_all("Polling Count",
                                            filters={"constituency": data["constituency"],
                                                     "round": data["round"],
                                                    })
    
    if existing_polling_count:
        # Update existing record
        polling_count = frappe.get_doc("Polling Count", existing_polling_count[0].name)
        
        
        for candidate_data in data["candidates"]:
            # Update or append candidates' votes
            candidate_name = candidate_data["candidate_name"]
            current_round_votes = candidate_data["votes"]
            total = current_round_votes
            existing_candidate = next((c for c in polling_count.polling_items if c.candidate == candidate_name), None)
            if existing_candidate:
                existing_candidate.current_rounds_votes = current_round_votes
                # existing_candidate.previous_rounds_votes = previous_round_votes
                existing_candidate.total = total
            else:
                # Append new candidate if not already in the list
                polling_item = frappe.new_doc("Polling Details")
                polling_item.candidate = candidate_name
                polling_item.party = candidate_data["party"]
                polling_item.current_rounds_votes = current_round_votes
                # polling_item.previous_rounds_votes = previous_round_votes
                polling_item.total = total
                polling_count.append("polling_items", polling_item)
        
        polling_count.save(ignore_permissions=True)
        frappe.db.commit()
        return {'success_msg': "Data Updated Successfully"}
    else:
        # Insert new record
        polling_count = frappe.new_doc("Polling Count")
        polling_count.state = "Tamil Nadu"
        polling_count.constituency = data["constituency"]
        polling_count.reporter = user.username
        polling_count.round = data["round"]

        # Add candidates as child documents
        for candidate_data in data["candidates"]:
            polling_count.append("polling_items",{
                "candidate": candidate_data["candidate_name"],
                "party": candidate_data["party"],
                "current_rounds_votes": candidate_data["votes"],
                # "previous_round_votes": candidate_data["previous_round_votes"],
                "total":candidate_data["votes"]
            })
            
        polling_count.insert(ignore_permissions=True)
        frappe.db.commit()
        return {'success_msg': "Data Inserted Successfully"}

def fetch_round_candidate_details(round):
    # Retrieve the polling count record with the given id
    polling_count_list = frappe.get_list("Polling Count" ,filters= {'round':round} ,fields = ['*'])
    
    polling_count = frappe.get_doc("Polling Count", polling_count_list[0].name)
    

    # Check if the polling count record matches the requested round
    if polling_count.round != round:
        return {"error_msg": f"No data found for round '{round}'"}

    # Prepare response with candidate details
    response = {
        "constituency": polling_count.constituency,
        "reporter": polling_count.reporter,
        "round": polling_count.round,
        "candidates": []
    }

    # Add candidate details to the response
    for candidate in polling_count.polling_items:
        party = frappe.get_doc("Political Party",candidate.party)
        candidate_data = {
            "candidate_name": candidate.candidate,
            "party": candidate.party,
            "party_image": get_url() + party.party_name_image,
            "votes": candidate.current_rounds_votes
        }
        response["candidates"].append(candidate_data)

    return response

@frappe.whitelist()
def get_constituency_and_candidates(method = None,data = None,id=None,round = None):
    try:
        user_email = frappe.session.user
        user = frappe.get_doc("User",user_email)
        
        if method == "GET_INITIAL":
            return  fetch_initial_candidate_details(user_email)
            
        elif method == "POST_VOTES":
            return store_votes(user_email, data)
        
        elif method == "GET_ROUND":
            return fetch_round_candidate_details(round)
        else:
            return {"error_msg": "Invalid method"}
            # return fetch_initial_candidate_details(data)
        # users_exists = frappe.db.exists("User", user_email)
        # if not users_exists:
        #     return {"error_msg":"User is not exists"}
        
        # user = user_email
        # if not user or not  "News Reporter" in frappe.get_roles(user):
        #     frappe.throw(_("Access Denied"), frappe.PermissionError)
            
        # user = frappe.get_doc("User",user)
        # reporter = frappe.get_all("Reporter", filters={"user_name": user.username}, fields=["*"])

        # # Retrieve reporter's constituency
        # constituency = frappe.get_value("Reporter", reporter[0].user_name, "constituency")
        
        # # Fetch candidates and parties for the constituency
        # candidates = frappe.get_all("Election Candidate", filters={"constituency": constituency}, fields=["candidate_name", "party","party_image","votes"])
        
        # # Prepare response
        if method == "GET":
         
            response = {
                "constituency": constituency,
                "reporter":user.username,
                "round":None,
                "candidates": candidates
            }
            return response
        elif method == "POST":
            data ={
                "constituency": "Arani",
                "reporter": "jothi",
                "round": 'R2',
                "candidates": [
                    {
                        "candidate_name": "Sarathi",
                        "party": "Aam Aadmi Party",
                        "party_image": "http://polltracking.com:8007/files/Aam_Aadmi_Party_Flag.svg.png",
                        "votes": 1000
                        
                    },
                    {
                        "candidate_name": "Karthick k",
                        "party": "All India Anna Dravida Munnetra Kazhagam",
                        "party_image": "http://polltracking.com:8007/files/Aam_Aadmi_Party_Flag.svg.png",
                        "votes": 1000
                        
                    },
                    {
                        "candidate_name": "Jothi",
                        "party": "Bharatiya Janata Party",
                        "party_image": "http://polltracking.com:8007/files/Aam_Aadmi_Party_Flag.svg.png",
                        "votes": 1000
                    }
                ]
                }
            
            polling_count = frappe.new_doc("Polling Count")
            polling_count.state = "Tamil Nadu"
            polling_count.constituency = data["constituency"]
            polling_count.reporter = user.username
            polling_count.round = data["round"]

            # Add candidates as child documents
            for candidate_data in data["candidates"]:
                polling_count.append("polling_items",{
                    "candidate":candidate_data["candidate_name"],
                    "party":candidate_data["party"],
                        "current_rounds_votes":candidate_data["votes"]
                })
                
            polling_count.insert(ignore_permissions=True)
            frappe.db.commit()
    except Exception as e :
        return e        
    
    
        
        
    # if method == "GET":
        # return response
       
         
    # elif method == "POST":
    #     polling_count = frappe.new_doc("Polling Count")
    #     polling_count.state = "Tamil Nadu"
    #     polling_count.constituency = constituency
    #     polling_count.reporter = user.username
    #     polling_count.round = response.round
        
    #     # Add candidates as child documents
    #     for candidate_data in response.candidates:
    #         candidate = polling_count.append("candidates", {})
    #         candidate.candidate_name = candidate_data["candidate_name"]
    #         candidate.party = candidate_data["party"]
    #         candidate.party_image = candidate_data["party_image"]
    #         candidate.current_rounds_votes = candidate_data["votes"]

    #     # Save the polling count document
    #     polling_count.insert(ignore_permissions=True)
    
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
   
