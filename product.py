#This file is part of sale_customer_product module for Tryton.  The COPYRIGHT
#file at the top level of this repository contains the full copyright
#notices and license terms.
import datetime
from trytond.model import ModelView, ModelSQL, fields
from trytond.pyson import Eval, If
from trytond.pool import Pool, PoolMeta
from trytond.transaction import Transaction
from trytond import backend

__all__ = ['Template']
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
    def default_product_customer_only():
        return False
