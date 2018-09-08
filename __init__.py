#The COPYRIGHT file at the top level of this repository contains the full
#copyright notices and license terms.

from trytond.pool import Pool
from . import product
from . import sale

def register():
    Pool.register(
        product.Template,
        sale.Sale,
        sale.SaleLine,
        module='sale_customer_product_restrict', type_='model')
