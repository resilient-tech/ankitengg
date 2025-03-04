# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt


import frappe
from frappe import _
from frappe.utils import flt

from erpnext.accounts.report.financial_statements import (
	get_columns,
	get_data,
	get_filtered_list_for_consolidated_report,
	get_period_list,
)
from ankitengg.ankitengg.report.financial_statement_test import (
	get_columns_test,
	get_data_test,
	get_filtered_list_for_consolidated_report_test,
	get_period_list_test,
)

def execute(filters=None):
	period_list = get_period_list(
		filters.from_fiscal_year,
		filters.to_fiscal_year,
		filters.period_start_date,
		filters.period_end_date,
		filters.filter_based_on,
		filters.periodicity,
		company=filters.company,
	)
	period_list_test = get_period_list_test(
		filters.from_fiscal_year,
		filters.to_fiscal_year,
		filters.period_start_date,
		filters.period_end_date,
		filters.filter_based_on,
		filters.periodicity,
		company=filters.company,
	)

	income = get_data(
		filters.company,
		"Income",
		"Credit",
		period_list,
		filters=filters,
		accumulated_values=filters.accumulated_values,
		ignore_closing_entries=True,
		ignore_accumulated_values_for_fy=True,
	)
	income_test = get_data_test(
		filters.company,
		"Income",
		"Credit",
		period_list_test,
		filters=filters,
		accumulated_values=filters.accumulated_values,
		ignore_closing_entries=True,
		ignore_accumulated_values_for_fy=True,
	)

	expense = get_data(
		filters.company,
		"Expense",
		"Debit",
		period_list,
		filters=filters,
		accumulated_values=filters.accumulated_values,
		ignore_closing_entries=True,
		ignore_accumulated_values_for_fy=True,
	)
	expense_test = get_data(
		filters.company,
		"Expense",
		"Debit",
		period_list_test,
		filters=filters,
		accumulated_values=filters.accumulated_values,
		ignore_closing_entries=True,
		ignore_accumulated_values_for_fy=True,
	)

	net_profit_loss = get_net_profit_loss(
		income, expense, period_list, filters.company, filters.presentation_currency
	)
	net_profit_loss_test = get_net_profit_loss_test(
		income_test, expense_test, period_list_test, filters.company, filters.presentation_currency
	)

	data = []
	data.extend(income or [])
	data.extend(expense or [])
	sum_data=[]
	sum_data.extend(income_test or [])
	sum_data.extend(expense_test or [])
	if net_profit_loss:
		data.append(net_profit_loss)
	if net_profit_loss_test:
		data.append(net_profit_loss_test)
	columns = get_columns(
		filters.periodicity, period_list, filters.accumulated_values, filters.company
	)

	chart = get_chart_data(filters, columns, income, expense, net_profit_loss)
	print("data-----------",data)
	print("sum_data",sum_data)
	print("filters.periodicity",filters.periodicity)
	print("filters.period_start_date",filters.period_start_date)
	print("filters.period_end_date",filters.period_end_date)
	close_diff_june_22=0
	close_diff_sep_22=0
	close_diff_dec_22=0
	close_diff_mar_23=0
	open_diff_june_22=0
	open_diff_sep_22=0
	open_diff_dec_22=0
	open_diff_mar_23=0
	for x in range(len(data)):
		if data[x].get('account_name') == 'Closing Stocks' and filters.periodicity=="Quarterly":
			print('quaterly data ----', data[x])
			print('monthly data ----', sum_data[x])
			close_diff_june_22=data[x]['jun_2022']-sum_data[x]['jun_2022']
			close_diff_sep_22=data[x]['sep_2022']-sum_data[x]['sep_2022']
			close_diff_dec_22=data[x]['dec_2022']-sum_data[x]['dec_2022']
			close_diff_mar_23=data[x]['mar_2023']-sum_data[x]['mar_2023']
			data[x]['sep_2022'] = sum_data[x]['sep_2022']
			data[x]['jun_2022'] = sum_data[x]['jun_2022']
			data[x]['dec_2022'] = sum_data[x]['dec_2022']
			data[x]['mar_2023'] = sum_data[x]['mar_2023']
			data[x]['total']=sum_data[x]['jun_2022']+sum_data[x]['sep_2022']+sum_data[x]['dec_2022']+sum_data[x]['mar_2023']
		if data[x].get('account_name') == 'Opening Stock' and filters.periodicity=="Quarterly":
			print('quaterly data ----', data[x])
			print('monthly data ----', sum_data[x])
			open_diff_june_22=data[x]['jun_2022']-sum_data[x]['apr_2022']
			open_diff_sep_22=data[x]['sep_2022']-sum_data[x]['jul_2022']
			open_diff_dec_22=data[x]['dec_2022']-sum_data[x]['oct_2022']
			open_diff_mar_23=data[x]['mar_2023']- sum_data[x]['jan_2023']
			data[x]['sep_2022'] = sum_data[x]['jul_2022']
			data[x]['jun_2022'] = sum_data[x]['apr_2022']
			data[x]['dec_2022'] = sum_data[x]['oct_2022']
			data[x]['mar_2023'] = sum_data[x]['jan_2023']
			data[x]['total']=sum_data[x]['apr_2022']+sum_data[x]['jul_2022']+sum_data[x]['oct_2022']+sum_data[x]['jan_2023']
	for x in range(len(data)):
		if data[x].get('account_name') == 'Closing Stocks':
			#print('quaterly data ----', data[x])
			parent=data[x].get('parent_account')
			print("parentof closing",parent)
			for z in data:
				#print(z['account'])
				if z['account']==parent and z['parent_account']!=parent:
					print("before",z['jun_2022'])
					z['jun_2022']=z['jun_2022']-close_diff_june_22
					z['sep_2022']=z['sep_2022']-close_diff_sep_22
					z['dec_2022']=z['dec_2022']-close_diff_dec_22
					z['mar_2023']=z['mar_2023']-close_diff_mar_23
					z['total']=z['jun_2022']+z['sep_2022']+z['dec_2022']+z['mar_2023']
					print("after in closing",z['jun_2022'])
					break
	for x in range(len(data)):
		if data[x].get('account_name') == 'Opening Stock':
			#print('quaterly data ----', data[x])
			parent=data[x].get('parent_account')
			print("parentof opening",parent)
			for z in data:
				#print(z['account'])
				if z.get('account',None)==parent and z['parent_account']!=parent:
					print("before",z['jun_2022'])
					z['jun_2022']=z['jun_2022']-open_diff_june_22
					z['sep_2022']=z['sep_2022']-open_diff_sep_22
					z['dec_2022']=z['dec_2022']-open_diff_dec_22
					z['mar_2023']=z['mar_2023']-open_diff_mar_23
					z['total']=z['jun_2022']+z['sep_2022']+z['dec_2022']+z['mar_2023']
					print("after in opening",z['jun_2022'])
					break
	for y in range(len(data)):
		if data[y].get('account_name') == 'Income':
			print('adding for account income',data[y].get('jun_2022'))
			data[y]['jun_2022'] =data[y]['jun_2022']-close_diff_june_22
			data[y]['sep_2022'] =data[y]['sep_2022']-close_diff_sep_22
			data[y]['dec_2022'] =data[y]['dec_2022']-close_diff_dec_22
			data[y]['mar_2023'] =data[y]['mar_2023']-close_diff_mar_23
			break
	for y in range(len(data)):
		if data[y].get('account_name') == 'Expenses':
			print('adding of account expense',data[y].get('jun_2022'))
			data[y]['jun_2022'] =data[y]['jun_2022']-open_diff_june_22
			data[y]['sep_2022'] =data[y]['sep_2022']-open_diff_sep_22
			data[y]['dec_2022'] =data[y]['dec_2022']-open_diff_dec_22
			data[y]['mar_2023'] =data[y]['mar_2023']-open_diff_mar_23
			break
	for y in range(len(data)):
		if data[y].get('account_name') == 'Total Income (Credit)':
			data[y]['jun_2022'] =data[y]['jun_2022']-close_diff_june_22
			data[y]['sep_2022'] =data[y]['sep_2022']-close_diff_sep_22
			data[y]['dec_2022'] =data[y]['dec_2022']-close_diff_dec_22
			data[y]['mar_2023'] =data[y]['mar_2023']-close_diff_mar_23
			data[y]['total']=data[y]['jun_2022']+data[y]['sep_2022']+data[y]['dec_2022']+data[y]['mar_2023']
			break
	for y in range(len(data)):
		if data[y].get('account_name') == 'Total Expense (Debit)':
			print('adding of account Total Expense (Debit)',data[y].get('jun_2022'))
			data[y]['jun_2022'] =data[y]['jun_2022']-open_diff_june_22
			data[y]['sep_2022'] =data[y]['sep_2022']-open_diff_sep_22
			data[y]['dec_2022'] =data[y]['dec_2022']-open_diff_dec_22
			data[y]['mar_2023'] =data[y]['mar_2023']-open_diff_mar_23
			data[y]['total']=data[y]['jun_2022']+data[y]['sep_2022']+data[y]['dec_2022']+data[y]['mar_2023']
			break
	print("final data",data)
	currency = filters.presentation_currency or frappe.get_cached_value(
		"Company", filters.company, "default_currency"
	)
	report_summary = get_report_summary(
		period_list, filters.periodicity, income, expense, net_profit_loss, currency, filters
	)
	print("data",data)
	return columns, data, None, chart, report_summary


def get_report_summary(
	period_list, periodicity, income, expense, net_profit_loss, currency, filters, consolidated=False
):
	net_income, net_expense, net_profit = 0.0, 0.0, 0.0

	# from consolidated financial statement
	if filters.get("accumulated_in_group_company"):
		period_list = get_filtered_list_for_consolidated_report(filters, period_list)

	for period in period_list:
		key = period if consolidated else period.key
		if income:
			net_income += income[-2].get(key)
		if expense:
			net_expense += expense[-2].get(key)
		if net_profit_loss:
			net_profit += net_profit_loss.get(key)

	if len(period_list) == 1 and periodicity == "Yearly":
		profit_label = _("Profit This Year")
		income_label = _("Total Income This Year")
		expense_label = _("Total Expense This Year")
	else:
		profit_label = _("Net Profit")
		income_label = _("Total Income")
		expense_label = _("Total Expense")

	return [
		{"value": net_income, "label": income_label, "datatype": "Currency", "currency": currency},
		{"type": "separator", "value": "-"},
		{"value": net_expense, "label": expense_label, "datatype": "Currency", "currency": currency},
		{"type": "separator", "value": "=", "color": "blue"},
		{
			"value": net_profit,
			"indicator": "Green" if net_profit > 0 else "Red",
			"label": profit_label,
			"datatype": "Currency",
			"currency": currency,
		},
	]


def get_net_profit_loss(income, expense, period_list, company, currency=None, consolidated=False):
	total = 0
	net_profit_loss = {
		"account_name": "'" + _("Profit for the year") + "'",
		"account": "'" + _("Profit for the year") + "'",
		"warn_if_negative": True,
		"currency": currency or frappe.get_cached_value("Company", company, "default_currency"),
	}

	has_value = False

	for period in period_list:
		key = period if consolidated else period.key
		total_income = flt(income[-2][key], 3) if income else 0
		total_expense = flt(expense[-2][key], 3) if expense else 0

		net_profit_loss[key] = total_income - total_expense

		if net_profit_loss[key]:
			has_value = True

		total += flt(net_profit_loss[key])
		net_profit_loss["total"] = total

	if has_value:
		return net_profit_loss

def get_net_profit_loss_test(income_test, expense_test, period_list_test, company, currency=None, consolidated=False):
	total = 0
	net_profit_loss = {
		"account_name": "'" + _("Profit for the year") + "'",
		"account": "'" + _("Profit for the year") + "'",
		"warn_if_negative": True,
		"currency": currency or frappe.get_cached_value("Company", company, "default_currency"),
	}

	has_value = False
	print("period_list_test",period_list_test)
	for period in period_list_test:
		key = period if consolidated else period.key
		total_income = flt(income_test[-2][key], 3) if income_test else 0
		total_expense = flt(expense_test[-2][key], 3) if expense_test else 0

		net_profit_loss[key] = total_income - total_expense

		if net_profit_loss[key]:
			has_value = True

		total += flt(net_profit_loss[key])
		net_profit_loss["total"] = total

	if has_value:
		return net_profit_loss

def get_chart_data(filters, columns, income, expense, net_profit_loss):
	labels = [d.get("label") for d in columns[2:]]

	income_data, expense_data, net_profit = [], [], []

	for p in columns[2:]:
		if income:
			income_data.append(income[-2].get(p.get("fieldname")))
		if expense:
			expense_data.append(expense[-2].get(p.get("fieldname")))
		if net_profit_loss:
			net_profit.append(net_profit_loss.get(p.get("fieldname")))

	datasets = []
	if income_data:
		datasets.append({"name": _("Income"), "values": income_data})
	if expense_data:
		datasets.append({"name": _("Expense"), "values": expense_data})
	if net_profit:
		datasets.append({"name": _("Net Profit/Loss"), "values": net_profit})

	chart = {"data": {"labels": labels, "datasets": datasets}}

	if not filters.accumulated_values:
		chart["type"] = "bar"
	else:
		chart["type"] = "line"

	chart["fieldtype"] = "Currency"

	return chart