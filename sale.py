#This file is part of sale_customer_product module for Tryton.  The COPYRIGHT
#file at the top level of this repository contains the full copyright
#notices and license terms.
from trytond.pool import Pool, PoolMeta
from trytond.i18n import gettext
from trytond.exceptions import UserError

__all__ = ['SaleLine', 'Sale']


class Sale(metaclass=PoolMeta):
    __name__ = 'sale.sale'

    @classmethod
    def validate(cls, sales):
        super(Sale, cls).validate(sales)
        for sale in sales:
            sale.check_restricted_products()

    def check_restricted_products(self):
        for line in self.lines:
            line.check_restricted_products()


class SaleLine(metaclass=PoolMeta):
    __name__ = 'sale.line'


    @classmethod
    def validate(cls, lines):
        super(SaleLine, cls).validate(lines)
        for line in lines:
            line.check_restricted_products()

    def check_restricted_products(self):
        if not self.product or not self.product.template.product_customer_only:
            return
        ProductCustomer = Pool().get('sale.product_customer')
        products = ProductCustomer.search([
                ('product', '=', self.product.template.id),
                ('party', '=', self.sale.party)])
        if not products:
            raise UserError(gettext(
                'sale_customer_product_restrict.restricted_product',
                product=self.product.rec_name))
