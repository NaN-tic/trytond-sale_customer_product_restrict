import unittest
from decimal import Decimal

from proteus import Model
from trytond.exceptions import UserError
from trytond.modules.account.tests.tools import (create_chart,
                                                 create_fiscalyear,
                                                 get_accounts)
from trytond.modules.account_invoice.tests.tools import (
    create_payment_term, set_fiscalyear_invoice_sequences)
from trytond.modules.company.tests.tools import create_company, get_company
from trytond.tests.test_tryton import drop_db
from trytond.tests.tools import activate_modules


class Test(unittest.TestCase):

    def setUp(self):
        drop_db()
        super().setUp()

    def tearDown(self):
        drop_db()
        super().tearDown()

    def test(self):

        # Activate sale_customer_product_restrict
        config = activate_modules('sale_customer_product_restrict')

        # Create company
        _ = create_company()
        company = get_company()

        # Create sale user
        User = Model.get('res.user')
        Group = Model.get('res.group')
        sale_user = User()
        sale_user.name = 'Sale'
        sale_user.login = 'sale'
        sale_group, = Group.find([('name', '=', 'Sales')])
        sale_user.groups.append(sale_group)
        sale_user.save()

        # Create stock user
        stock_user = User()
        stock_user.name = 'Stock'
        stock_user.login = 'stock'
        stock_group, = Group.find([('name', '=', 'Stock')])
        stock_user.groups.append(stock_group)
        stock_user.save()

        # Create account user
        account_user = User()
        account_user.name = 'Account'
        account_user.login = 'account'
        account_group, = Group.find([('name', '=', 'Account')])
        account_user.groups.append(account_group)
        account_user.save()

        # Create fiscal year
        fiscalyear = set_fiscalyear_invoice_sequences(
            create_fiscalyear(company))
        fiscalyear.click('create_period')

        # Create chart of accounts
        _ = create_chart(company)
        accounts = get_accounts(company)
        revenue = accounts['revenue']
        expense = accounts['expense']

        # Create parties
        Party = Model.get('party.party')
        supplier = Party(name='Supplier')
        supplier.save()
        customer = Party(name='Customer')
        customer.save()
        customer2 = Party(name='Customer2')
        customer2.save()

        # Create account category
        ProductCategory = Model.get('product.category')
        account_category = ProductCategory(name="Account Category")
        account_category.accounting = True
        account_category.account_expense = expense
        account_category.account_revenue = revenue
        account_category.save()

        # Create Restricted product
        ProductUom = Model.get('product.uom')
        unit, = ProductUom.find([('name', '=', 'Unit')])
        ProductTemplate = Model.get('product.template')
        Product = Model.get('product.product')
        template = ProductTemplate()
        template.name = 'product'
        template.default_uom = unit
        template.type = 'goods'
        template.salable = True
        template.list_price = Decimal('10')
        template.cost_price_method = 'fixed'
        template.account_category = account_category
        template.product_customer_only = True
        template.save()
        product, = template.products

        # Create UnRestricted product
        product2 = Product()
        template2 = ProductTemplate()
        template2.name = 'product'
        template2.default_uom = unit
        template2.type = 'goods'
        template2.salable = True
        template2.list_price = Decimal('10')
        template2.cost_price = Decimal('5')
        template2.cost_price_method = 'fixed'
        template2.product_customer_only = False
        template2.account_category = account_category
        template2.save()
        product2.template = template2
        product2.save()

        # Create Customer Product
        CustomerProduct = Model.get('sale.product_customer')
        cp = CustomerProduct()
        cp.party = customer
        cp.product = template
        cp.name = 'Customer 1 Product'
        cp.code = '1111'
        cp.save()

        # Create payment term
        payment_term = create_payment_term()
        payment_term.save()

        # Create an Inventory
        config.user = stock_user.id
        Inventory = Model.get('stock.inventory')
        InventoryLine = Model.get('stock.inventory.line')
        Location = Model.get('stock.location')
        storage, = Location.find([
            ('code', '=', 'STO'),
        ])
        inventory = Inventory()
        inventory.location = storage
        inventory.save()
        inventory_line = InventoryLine(product=product, inventory=inventory)
        inventory_line.quantity = 100.0
        inventory_line.expected_quantity = 0.0
        inventory.save()
        inventory_line.save()
        Inventory.confirm([inventory.id], config.context)
        self.assertEqual(inventory.state, 'done')

        # Sale Restricted product to allowed Customer
        config.user = sale_user.id
        Sale = Model.get('sale.sale')
        SaleLine = Model.get('sale.line')
        sale = Sale()
        sale.party = customer
        sale.payment_term = payment_term
        sale.invoice_method = 'order'
        sale_line = SaleLine()
        sale.lines.append(sale_line)
        sale_line.product = product
        sale_line.quantity = 2.0
        sale.save()
        sale.click('quote')
        sale.click('confirm')
        self.assertEqual(sale.state, 'processing')
        sale.reload()

        # Sale Restricted product to disallowed Customer
        config.user = sale_user.id
        Sale = Model.get('sale.sale')
        SaleLine = Model.get('sale.line')
        sale = Sale()
        sale.party = customer2
        sale.payment_term = payment_term
        sale.invoice_method = 'order'
        sale_line = SaleLine()
        sale.lines.append(sale_line)
        sale_line.product = product
        sale_line.quantity = 2.0
        sale.save()
        sale.click('quote')

        with self.assertRaises(UserError):
            sale.click('confirm')

        # Sale Restricted and not restricted product to allowed Customer
        config.user = sale_user.id
        Sale = Model.get('sale.sale')
        SaleLine = Model.get('sale.line')
        sale = Sale()
        sale.party = customer
        sale.payment_term = payment_term
        sale.invoice_method = 'order'
        sale_line = SaleLine()
        sale.lines.append(sale_line)
        sale_line.product = product
        sale_line.quantity = 2.0
        sale_line = SaleLine()
        sale.lines.append(sale_line)
        sale_line.product = product2
        sale_line.quantity = 2.0
        sale.save()
        sale.click('quote')
        sale.click('confirm')
        self.assertEqual(sale.state, 'processing')
        sale.reload()

        # Sale not restricted product to Unallowed Customer
        config.user = sale_user.id
        Sale = Model.get('sale.sale')
        SaleLine = Model.get('sale.line')
        sale = Sale()
        sale.party = customer
        sale.payment_term = payment_term
        sale.invoice_method = 'order'
        sale_line = SaleLine()
        sale.lines.append(sale_line)
        sale_line.product = product2
        sale_line.quantity = 2.0
        sale_line = SaleLine()
        sale.lines.append(sale_line)
        sale_line.product = product2
        sale_line.quantity = 2.0
        sale.save()
        sale.click('quote')
        sale.click('confirm')
        self.assertEqual(sale.state, 'processing')
        sale.reload()
