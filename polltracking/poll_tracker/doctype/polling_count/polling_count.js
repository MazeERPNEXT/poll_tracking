// Copyright (c) 2024, Mazeworks and contributors
// For license information, please see license.txt

frappe.ui.form.on("Polling Count", {
	// refresh(frm) {

	// },
    
    // onload:function(frm){  
    //     if (frm.is_dirty()) {
    //         frappe.show_alert('Please save form before attaching a file')
    //     }
    //     frm.set_query('constituency', () => {
    //         return {
    //             filters: {
    //                 constituency: ['in', []]
    //             }
    //         }
    //     })
    //     if(frm.doc.state === undefined){
    //     frm.doc.state = "TamilNadu";
    //     }
    //     if(frm.doc.reporter === undefined){
    //     frm.doc.reporter = frappe.session.user_fullname
    //     }
    //     if (frm.doc.constituency === undefined){
    //         frappe.db.get_value(
    //             "Reporter",
    //             { user: frappe.session.user },
    //             "constituency",
    //             (r) => {
    //                 if (r && r.constituency) {
    //                     console.log(r)
    //                     frm.set_value("constituency", r.constituency);
    //                 }
    //             }
    //         );
    //     }
        
        
    //     // if (!frm.is_dirty()) {
            
       
    //     for (var i = 0; i < 10; i++) {
    //         var child = cur_frm.add_child("polling_items");
    //         frappe.model.set_value(child.doctype, child.name, "candidate", "sarathi");
    //         frappe.model.set_value(child.doctype, child.name, "party", "DMK");
    //         frappe.model.set_value(child.doctype, child.name, "previous_rounds_votes", "0");
    //         frappe.model.set_value(child.doctype, child.name, "current_rounds_votes", "");
    //         frappe.model.set_value(child.doctype, child.name, "total", "0");

    //     }
    //     var child = cur_frm.add_child("polling_items");
    //     frappe.model.set_value(child.doctype, child.name, "party", "Total");
    //     frappe.model.set_value(child.doctype, child.name, "previous_rounds_votes", "0");
    //     frappe.model.set_value(child.doctype, child.name, "current_rounds_votes", "");
    //     frappe.model.set_value(child.doctype, child.name, "total", "0");
    //         // }
    //     cur_frm.refresh_field("polling_items")
    // },

    // constituency:function(frm){
            
    //     if(frm.doc.constituency){
    //         for (var i = 0; i < 10; i++) {
    //             var child = cur_frm.add_child("polling_items");
    //             frappe.model.set_value(child.doctype, child.name, "candidate", "sarathi");
    //             frappe.model.set_value(child.doctype, child.name, "party", "DMK");
    //             frappe.model.set_value(child.doctype, child.name, "previous_rounds_votes", "0");
    //             frappe.model.set_value(child.doctype, child.name, "current_rounds_votes", "");
    //             frappe.model.set_value(child.doctype, child.name, "total", "0");

    //             }
    //             var child = cur_frm.add_child("polling_items");
    //             frappe.model.set_value(child.doctype, child.name, "party", "Total");
    //             frappe.model.set_value(child.doctype, child.name, "previous_rounds_votes", "0");
    //             frappe.model.set_value(child.doctype, child.name, "current_rounds_votes", "");
    //             frappe.model.set_value(child.doctype, child.name, "total", "0");
    //         }
    //         cur_frm.refresh_field("polling_items")
    // }
});



