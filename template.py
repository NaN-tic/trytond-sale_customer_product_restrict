#This file is part of sale_customer_product module for Tryton.  The COPYRIGHT
#file at the top level of this repository contains the full copyright
#notices and license terms.

import datetime

from trytond.model import ModelView, ModelSQL, fields
from trytond.pyson import Eval, If
from trytond.pool import Pool, PoolMeta
from trytond.transaction import Transaction
from trytond import backend

__all__ = ['Template', 'SaleLine', 'Sale']
__metaclass__ = PoolMeta


class Template:
    __name__ = "product.template"

    product_customer_only = fields.Boolean('Sale Restricted',
        states={
            'readonly': ~Eval('active', True),
            'invisible': (~Eval('salable', False)
                | ~Eval('context', {}).get('company')),
            }, depends=['active', 'salable'])

    @staticmethod
    def default_customer_only():
        return False


class Sale:
    __name__ = 'sale.sale'

    def check_restricted_products(self):
        Line = Pool().get('sale.line')
        for line in self.lines:
            line.check_restricted_products()

    @classmethod
    def validate(cls, sales):
        super(Sale, cls).validate(sales)
        for sale in sales:
            sale.check_restricted_products()


class SaleLine:
    __name__ = 'sale.line'

    @classmethod
    def validate(cls, lines):
        super(SaleLine, cls).validate(lines)
        for line in lines:
            line.check_restricted_products()

    @classmethod
    def __setup__(cls):
        super(SaleLine, cls).__setup__()
        cls._error_messages.update({
                'restricted_product': ('Product %s is restricted'),
                })

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

