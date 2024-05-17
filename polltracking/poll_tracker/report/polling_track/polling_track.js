// Copyright (c) 2024, Mazeworks and contributors
// For license information, please see license.txt

frappe.query_reports["Polling Track"] = {
	
	filters: [
        {
            fieldname: 'state',
            label: __('State'),
            fieldtype: 'Select',
            options: 'Tamil Nadu',
            // default: 'Tamil Nadu'
        },
        {
            fieldname: 'user',
            label: __('User'),
            fieldtype: 'Link',
            options: 'User',
            // default: 'Tamil Nadu'
        },
		{
            fieldname: 'constituency',
            label: __('Constituency'),
            fieldtype: 'Link',
            options: 'Constituency',
            // default: frappe.defaults.get_user_default('company')
        },
        {
            fieldname: 'condidate',
            label: __('Election Candidate'),
            fieldtype: 'Link',
            options: 'Election Candidate',
            // default: frappe.defaults.get_user_default('company')
        },
        {
            fieldname: 'reporter',
            label: __('Reporter'),
            fieldtype: 'Data',
            // options: [
            //     'Monthly',
            //     'Quarterly',
            //     'Half-Yearly',
            //     'Yearly'
            // ],
            // default:frappe.session.user,
            // depends_on: 'eval:doc.company=="Gadget Technologies Pvt. Ltd."'
        },
		
		{
            fieldname: 'party',
            label: __('Party'),
            fieldtype: 'Link',
            options: 'Political Party',
            // default: frappe.defaults.get_user_default('company')
        },
		
		{
            fieldname: 'round',
            label: __('Round'),
            fieldtype: 'Link',
            options: 'Polling Round',
            // default: frappe.defaults.get_user_default('company')
        }
	]
};
