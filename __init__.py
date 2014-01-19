#The COPYRIGHT file at the top level of this repository contains the full
#copyright notices and license terms.

from trytond.pool import Pool
from .product import *
from .sale import *

def register():
    Pool.register(
        Template,
        Sale,
        SaleLine,
        module='sale_customer_product_restrict', type_='model')
