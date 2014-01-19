#This file is part of sale_customer_product module for Tryton.  The COPYRIGHT
#file at the top level of this repository contains the full copyright
#notices and license terms.

import datetime

from trytond.model import ModelView, ModelSQL, fields
from trytond.pyson import Eval, If
from trytond.pool import Pool, PoolMeta
from trytond.transaction import Transaction
from trytond import backend

__all__ = ['SaleLine', 'Sale']
__metaclass__ = PoolMeta


class Sale:
    __name__ = 'sale.sale'

    @classmethod
    def validate(cls, sales):
        super(Sale, cls).validate(sales)
        for sale in sales:
            sale.check_restricted_products()

    def check_restricted_products(self):
        Line = Pool().get('sale.line')
        for line in self.lines:
            line.check_restricted_products()


class SaleLine:
    __name__ = 'sale.line'

    @classmethod
    def __setup__(cls):
        super(SaleLine, cls).__setup__()
        cls._error_messages.update({
                'restricted_product': ('Product %s is restricted to some '
                    'customers only.'),
                })

    @classmethod
    def validate(cls, lines):
        super(SaleLine, cls).validate(lines)
        for line in lines:
            line.check_restricted_products()

    def check_restricted_products(self):
        if not self.product or not self.product.product_customer_only:
            return
        ProductCustomer = Pool().get('sale.product_customer')
        products = ProductCustomer.search([
                ('product', '=', self.product.template.id),
                ('party', '=', self.sale.party)])
        if not products:
            self.raise_user_error('restricted_product',
                (self.product.rec_name,))
