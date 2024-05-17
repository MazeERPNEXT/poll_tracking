import frappe
from frappe.utils import get_site_name
import base64
from datetime import datetime 
from frappe import _
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



def fetch_initial_candidate_details(user_email,round):
    
    users_exists = frappe.db.exists("User", user_email)
    if not users_exists:
        return {"error_msg":"User is not exists"}
    
    user = frappe.get_doc("User",user_email)
    # if not user or not  "News Reporter" in frappe.get_roles(user.email):
    #     frappe.throw(_("Access Denied"), frappe.PermissionError)
    return fetch_reporter_against_polling_details(user,round)
    
    
def fetch_reporter_against_polling_details(user,round):
    reporter = frappe.get_all("Reporter", filters={"user_name": user.username}, fields=["*"])
    
    constituency = frappe.get_value("Reporter", reporter[0].user_name, "constituency")
    
    # Fetch candidates and parties for the constituency
    candidates = frappe.get_all("Election Candidate", filters={"constituency": constituency}, fields=["candidate_name", "party","party_image","votes"])
    condidate_details = []

    polling_round_list = frappe.get_all("Polling Count",filters = {"round":round},fields = ['*'])
   
    if polling_round_list:
        for polling_round_row in polling_round_list:    
            polling_items = frappe.get_all("Polling details",filters = {'parent':polling_round_row.name},fields = '*')
            for polling_item in  polling_items:
                    condidate_details.append({
                    "candidate_name":polling_item.candidate,
                    "party":polling_item.party,
                    "party_image":get_url()+":8000"+polling_item.party_name_image if polling_item.party_name_image else None,
                    "votes":polling_item.current_rounds_votes,
                })
            sorted_condidate_details = sorted(condidate_details, key=lambda x: x['candidate_name'])

                    
        response = {
            "constituency": constituency,
            "reporter":user.username,
            "round":round,
            "candidates": sorted_condidate_details
        }
    else:
        for condidate in candidates:
            condidate_details.append({
                "candidate_name":condidate.candidate_name,
                "party":condidate.party,
                "party_image":get_url()+":8000"+condidate.party_image,
                "votes":0,
            })
        
        response = {
            "constituency": constituency,
            "reporter":user.username,
            "round":round,
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
        previous_round = f"R{int(data['round'][1:]) - 1}"
        if int(data["round"][1:]) > 0:
            previous_round = f"R{int(data['round'][1:]) - 1}"
            previous_round_polling_list = frappe.get_all("Polling Count", filters={"round": previous_round},fields = ['*'])
            if previous_round_polling_list:
                previous_round_polling_count = frappe.get_doc("Polling Count", previous_round_polling_list[0].name)
                previous_round_votes_map = {candidate.candidate: candidate.current_rounds_votes for candidate in previous_round_polling_count.polling_items}
            else:
                previous_round_votes_map = {}
        else:
            previous_round_votes_map = {}

        for candidate_data in data["candidates"]:
            # Update or append candidates' votes
            candidate_name = candidate_data["candidate_name"]
            current_round_votes = candidate_data["votes"]
            # total = current_round_votes
            previous_round_votes = previous_round_votes_map.get(candidate_name, 0)  # Get previous round votes for the candidate
            existing_candidate = next((c for c in polling_count.polling_items if c.candidate == candidate_name), None)
            if existing_candidate:
                existing_candidate.current_rounds_votes = current_round_votes
                existing_candidate.previous_rounds_votes = previous_round_votes
                existing_candidate.total = current_round_votes + previous_round_votes
            # else:
            #     # Append new candidate if not already in the list
            #     polling_item = frappe.new_doc("Polling Details")
            #     polling_item.candidate = candidate_name
            #     polling_item.party = candidate_data["party"]
            #     polling_item.current_rounds_votes = current_round_votes
            #     polling_item.previous_rounds_votes = previous_round_votes
            #     polling_item.total = previous_round_votes + current_round_votes
            #     polling_count.append("polling_items", polling_item)

        polling_count.save(ignore_permissions=True)
        frappe.db.commit()
        return {'success_msg': "Data Updated Successfully"}
    else:
        # Insert new record
        previous_round = f"R{int(data['round'][1:]) - 1}"
        if int(data["round"][1:]) > 0:
            previous_round = f"R{int(data['round'][1:]) - 1}"
            previous_round_polling_list = frappe.get_all("Polling Count", filters={"round": previous_round},fields = ['*'])
            if previous_round_polling_list:
                previous_round_polling_count = frappe.get_doc("Polling Count", previous_round_polling_list[0].name)
                previous_round_votes_map = {candidate.candidate: candidate.current_rounds_votes for candidate in previous_round_polling_count.polling_items}
            else:
                previous_round_votes_map = {'candidate_name':0}
        else:
            previous_round_votes_map = {}
        
        polling_count = frappe.new_doc("Polling Count")
        polling_count.state = "Tamil Nadu"
        polling_count.constituency = data["constituency"]
        polling_count.reporter = user.username
        polling_count.round = data["round"]
        

        # Add candidates as child documents
        for candidate_data in data["candidates"]:
            candidate_name = candidate_data["candidate_name"]
            previous_round_votes = previous_round_votes_map.get(candidate_name, 0)  # Get previous round votes for the candidate
            # existing_candidate = next((c for c in polling_count.polling_items if c.candidate == candidate_name), None)

            polling_count.append("polling_items",{
                "candidate": candidate_name,
                "party": candidate_data["party"],
                # "party_image":candidate_data['party_image'],
                "current_rounds_votes": candidate_data["votes"],
                "previous_rounds_votes": previous_round_votes,
                "total":previous_round_votes + candidate_data["votes"]
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
            "party_image": get_url() +":8000"+ party.party_name_image,
            "votes": candidate.current_rounds_votes
        }
        response["candidates"].append(candidate_data)

    return response


@frappe.whitelist()
def get_constituency_and_candidates(user_email = None,data = None,round = None):
    try:
        user_email = frappe.session.user or user_email
        user = frappe.get_doc("User",user_email)
        
        if round:
            return  fetch_initial_candidate_details(user_email,round)
            
        elif data and user_email:
            return store_votes(user_email, data)
        
    except Exception as e :
        return print(e)        
