#This file is part of sale_customer_product module for Tryton.  The COPYRIGHT
#file at the top level of this repository contains the full copyright
#notices and license terms.
from trytond.model import fields
from trytond.pyson import Eval
from trytond.pool import PoolMeta

__all__ = ['Template']


class Template(metaclass=PoolMeta):
    __name__ = "product.template"
    product_customer_only = fields.Boolean('Sale Restricted',
        states={
            'readonly': ~Eval('active', True),
            'invisible': (~Eval('salable', False)
                | ~Eval('context', {}).get('company')),
            }, depends=['active', 'salable'])

    @staticmethod
    def default_product_customer_only():
        return False
