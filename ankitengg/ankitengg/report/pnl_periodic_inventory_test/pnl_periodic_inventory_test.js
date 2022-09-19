// Copyright (c) 2016, jyoti and contributors
// For license information, please see license.txt
/* eslint-disable */
frappe.require("assets/erpnext/js/financial_statements.js", function() {
	frappe.query_reports["PnL Periodic Inventory test"] = $.extend({},
		erpnext.financial_statements);

	erpnext.utils.add_dimensions('PnL Periodic Inventory test', 10);

	frappe.query_reports["PnL Periodic Inventory test"]["filters"].push(
		{
			"fieldname": "project",
			"label": __("Project"),
			"fieldtype": "MultiSelectList",
			get_data: function(txt) {
				return frappe.db.get_link_options('Project', txt);
			}
		},
		{
			"fieldname": "include_default_book_entries",
			"label": __("Include Default Book Entries"),
			"fieldtype": "Check",
			"default": 1
		}
	);
});