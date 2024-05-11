# Copyright (c) 2024, Mazeworks and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
	# columns, data = [], []
    data = []
    columns = [
        {
            'fieldname': 'state',
            'label': _('State'),
            'fieldtype': 'Select',
            # 'options': 'Tamil Nadu'
        },
        {
            'fieldname': 'reporter',
            'label': _('Reporter'),
            'fieldtype': 'Data',
            # 'options': 'Currency'
        },
        {
            'fieldname': 'constituency',
            'label': _('Constitueny'),
            'fieldtype': 'Link',
            'options': 'Constituency'
        },
        {
            'fieldname': 'round',
            'label': _('Round'),
            'fieldtype': 'Link',
            'options': 'Polling Round'
        }
    ]
	# reporter = frappe.session.user
    reporter = 'jothi'
    polling_count_list = frappe.get_all("Polling Count",filters = {'reporter':reporter},fields = ['*'])
    for polling_count in polling_count_list:
        data.append(
                {
                'state': polling_count.state,
                'reporter': polling_count.reporter,
                'constituency': polling_count.constituency,
                'round':polling_count.round                
            }
        )   

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