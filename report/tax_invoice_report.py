# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014-Today BrowseInfo (<http://genpex.com/>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time
import datetime
from openerp.osv import osv
from openerp.tools.translate import _
from openerp.report import report_sxw
import os
from os.path import join
from openerp.modules.module import get_module_resource



class tax_invoice_report(report_sxw.rml_parse):


    def __init__(self, cr, uid, name, context=None):
        super(tax_invoice_report, self).__init__(cr, uid, name, context=context)
        self.index = 0
        self.total_tax_amount = 0
        self.total_discount = 0
        self.amount_untaxed = 0
        self.localcontext.update({
            'time': time,
            'get_order_date':self.get_order_date,
            'get_invoice_date':self.get_invoice_date,
            'get_shipment_no':self.get_shipment_no,
            'get_index':self.get_index,
            'get_taxes':self.get_taxes,
            #'get_discount':self.get_discount,
            'get_final_discount':self.get_final_discount,
            'get_product_line':self.get_product_line,
            'get_amount_untaxed':self.get_amount_untaxed,
            'get_credit':self.get_credit,
            'get_shipping':self.get_shipping,
            })

    def get_product_line(self,invoice_line):
        invoice_line_list = []
        for line in invoice_line:
            if line.product_id.product_tmpl_id.name !='Discount':
                if line.product_id.product_tmpl_id.name !='Shipping':
                    if line.product_id.product_tmpl_id.name !='Credit':
                        print "\n\n======",line.product_id.product_tmpl_id.name
                        self.amount_untaxed += line.price_subtotal
                        invoice_line_list.append(line)
        print "invoice_line_list=======",invoice_line_list
        return invoice_line_list
                
    def get_amount_untaxed(self):
        return self.amount_untaxed
    
    def get_taxes(self,invoice_line):
        if invoice_line.invoice_line_tax_id:
            for tax in invoice_line.invoice_line_tax_id:
                tax_ratio = tax.amount
                tax_amount = invoice_line.price_subtotal * tax_ratio
                self.total_tax_amount += tax_amount
                return tax_amount
        else:
            return '0.0'
            
#    def get_discount(self,line):
#        print "\n\n=====",line.discount
#        discount_amount = ((line.price_unit * line.discount)/100)
#        print "\n\n======Tax amount=====",discount_amount
#        self.total_discount += discount_amount
#        return discount_amount

    def get_final_discount(self,invoice_line):
        total_discount = 0
        for line in invoice_line:
            if line.product_id.product_tmpl_id.name =='Discount':
                total_discount += line.price_unit
        return total_discount

    def get_credit(self,invoice_line):
        total_credit = 0
        for line in invoice_line:
            if line.product_id.product_tmpl_id.name =='Credit':
                total_credit += line.price_unit
        return total_credit

    def get_shipping(self,invoice_line):
        total_shipping = 0
        for line in invoice_line:
            if line.product_id.product_tmpl_id.name =='Shipping':
                total_shipping += line.price_unit
        return total_shipping


    def get_index(self):
        self.index += 1
        return self.index
    
    def get_shipment_no(self,origin):
        if origin:
            sp_ids= self.pool.get('stock.picking').search(self.cr, self.uid, [('origin','=',origin)])
            if sp_ids:
                for ids in sp_ids:
                    sp_obj = self.pool.get('stock.picking').browse(self.cr,self.uid,ids)
                    return sp_obj.name



    def get_order_date(self,origin):
        if origin:
            so_ids= self.pool.get('sale.order').search(self.cr, self.uid, [('name','=',origin)])
            if so_ids:
                for ids in so_ids:
                    so_obj = self.pool.get('sale.order').browse(self.cr,self.uid,ids)
                    date = str(so_obj.date_order)
                    date_split = date.split(' ')
                    date1 = datetime.datetime.strptime(date_split[0], '%Y-%m-%d')
                    date2 = date1.strftime('%d %B %Y')
                    return date2

    def get_invoice_date(self,date):
        if date:
            date1 = datetime.datetime.strptime(date, '%Y-%m-%d')
            date2 = date1.strftime('%d %B %Y')
            return date2



class test_report_template_id(osv.AbstractModel):
    _name = 'report.tax_invoice_qweb_report.tax_invoice_report_template_id'
    _inherit = 'report.abstract_report'
    _template = 'tax_invoice_qweb_report.tax_invoice_report_template_id'
    _wrapped_report_class =tax_invoice_report

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
