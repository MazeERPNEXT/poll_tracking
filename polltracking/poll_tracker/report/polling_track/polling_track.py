# Copyright (c) 2024, Mazeworks and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from pypika import Query, Table, Field, functions as fn

def execute(filters=None):
    # Define tables
    polling_count = Table("Polling Count")
    polling_details = Table("Polling details")
    
    # Define fields
    state = Field("state")
    reporter = Field("reporter")
    constituency = Field("constituency")
    round = Field("round")
    party = Field("party")
    candidate = Field("candidate")
    total = Field("total")
    
    # Construct the query
    query = Query.from_(polling_count) \
        .select(polling_count.state,
                polling_count.reporter,
                polling_count.constituency,
                polling_count.round,
                polling_details.party,
                polling_details.candidate,
                polling_details.total) \
        .join(polling_details) \
        .on(polling_details.parent == polling_count.name)
    
    # Apply filters
    # if filters.get("round") or filters.get("constituency"):
    #     query = query.where(
    #         (polling_count.reporter == 'jothi') &
    #         (polling_count.round == filters.get("round")) &
    #         (polling_count.constituency == filters.get("constituency"))
    #     )
    frappe.errprint(str(query))
    # Execute the query
    result_set = frappe.db.sql(str(query))
    
    # Format result set into columns and data
    columns = result_set.columns
    data = result_set.fetchall()
    
    return columns, data

    # data = [
	# 		{
	# 			'state': 'Application of Funds (Assets)',
	# 			'reporter': 'INR',
	# 			'constituency': '15182212.738',
	# 			'round':'R1'
                
	# 		},
	# 		{
	# 			'state': 'Current Assets - GTPL',
	# 			'reporter': 'INR',
	# 			'constituency': '17117932.738',
	# 			'round':'R1'
                
	# 		}
			
	# 	]