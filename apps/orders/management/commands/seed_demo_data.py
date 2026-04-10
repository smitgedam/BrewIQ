"""
Management command: seed_demo_data
Usage: python manage.py seed_demo_data

Creates:
  - Superuser admin / admin123
  - Staff for each role
  - Menu categories + items
  - 10 cafe tables
  - Sample ingredients + links
  - A default GST rate (5%)
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from decimal import Decimal


class Command(BaseCommand):
    help = 'Seed the database with demo data for BrewIQ'

    def handle(self, *args, **options):
        self.stdout.write('🌱 Seeding BrewIQ demo data...\n')

        self._create_superuser()
        self._create_staff()
        self._create_menu()
        self._create_tables()
        self._create_ingredients()
        self._create_gst()

        self.stdout.write(self.style.SUCCESS('\n✅ Demo data seeded successfully!'))
        self.stdout.write('   Admin login → username: admin  password: admin123\n')

    # ── Superuser ────────────────────────────────────────────────────────────
    def _create_superuser(self):
        if not User.objects.filter(username='admin').exists():
            user = User.objects.create_superuser('admin', 'admin@brewiq.com', 'admin123',
                                                  first_name='Admin', last_name='User')
            from apps.accounts.models import StaffProfile
            StaffProfile.objects.create(user=user, role='ADMIN', phone='9999999999')
            self.stdout.write('  ✓ Superuser  admin / admin123')
        else:
            self.stdout.write('  · Superuser already exists')

    # ── Staff ────────────────────────────────────────────────────────────────
    def _create_staff(self):
        from apps.accounts.models import StaffProfile
        staff_data = [
            ('manager1', 'Priya',   'Sharma',  'MANAGER',  '9876543210'),
            ('cashier1', 'Rahul',   'Gupta',   'CASHIER',  '9876543211'),
            ('chef1',    'Sanjay',  'Patel',   'CHEF',     '9876543212'),
        ]
        for username, first, last, role, phone in staff_data:
            if not User.objects.filter(username=username).exists():
                u = User.objects.create_user(username, f'{username}@brewiq.com', 'staff123',
                                              first_name=first, last_name=last)
                StaffProfile.objects.create(user=u, role=role, phone=phone)
                self.stdout.write(f'  ✓ {role:<10} {username} / staff123')

    # ── Menu ─────────────────────────────────────────────────────────────────
    def _create_menu(self):
        from apps.menu.models import Category, MenuItem
        categories = [
            ('Hot Beverages', 1, [
                ('Espresso',          'Rich double-shot espresso',                      80,  True),
                ('Cappuccino',        'Espresso with steamed milk foam',               120,  True),
                ('Cafe Latte',        'Espresso with lots of steamed milk',            130,  True),
                ('Masala Chai',       'Traditional spiced Indian tea',                  60,  True),
                ('Filter Coffee',     'South Indian drip coffee with milk',             70,  True),
            ]),
            ('Cold Beverages', 2, [
                ('Cold Coffee',       'Blended iced coffee with cream',               140,  True),
                ('Iced Latte',        'Espresso over ice with cold milk',              150,  True),
                ('Mango Smoothie',    'Fresh mango blended with yoghurt',             120,  True),
                ('Lemonade',          'Fresh-squeezed lemon with mint',                80,  True),
            ]),
            ('Snacks', 3, [
                ('Veg Sandwich',      'Grilled sandwich with veggies & cheese',       110,  True),
                ('Paneer Toast',      'Spiced paneer on multigrain toast',            130,  True),
                ('Chocolate Muffin',  'Warm double-chocolate muffin',                  90,  True),
                ('Croissant',         'Buttery plain croissant',                        80,  True),
                ('Samosa (2 pcs)',    'Crispy potato-filled samosas',                   60,  True),
            ]),
            ('Meals', 4, [
                ('Veg Pasta',         'Penne in creamy tomato sauce',                 180, False),
                ('Club Sandwich',     'Triple-decker with fries',                     200, False),
                ('Paneer Wrap',       'Grilled paneer in a whole-wheat wrap',         170,  True),
            ]),
        ]
        for cat_name, order, items in categories:
            cat, _ = Category.objects.get_or_create(
                name=cat_name,
                defaults={'display_order': order, 'is_active': True}
            )
            for name, desc, price, is_veg in items:
                MenuItem.objects.get_or_create(
                    name=name,
                    defaults={
                        'category': cat,
                        'description': desc,
                        'base_price': Decimal(str(price)),
                        'current_price': Decimal(str(price)),
                        'is_available': True,
                        'is_vegetarian': is_veg,
                        'prep_time_minutes': 5,
                    }
                )
        self.stdout.write('  ✓ Menu categories & items')

    # ── Tables ───────────────────────────────────────────────────────────────
    def _create_tables(self):
        from apps.orders.models import CafeTable
        for num in range(1, 11):
            CafeTable.objects.get_or_create(number=num, defaults={'capacity': 4})
        self.stdout.write('  ✓ 10 cafe tables (T1–T10)')

    # ── Ingredients ──────────────────────────────────────────────────────────
    def _create_ingredients(self):
        from apps.inventory.models import Ingredient, MenuItemIngredient
        from apps.menu.models import MenuItem

        ingredients = [
            ('Espresso Beans',   'grams',  2000, 500,  Decimal('1.50')),
            ('Full-Fat Milk',    'ml',    10000, 2000, Decimal('0.07')),
            ('Sugar',            'grams',  3000, 500,  Decimal('0.05')),
            ('Chai Masala',      'grams',   500,  100, Decimal('0.80')),
            ('Mango Pulp',       'ml',     2000,  500, Decimal('0.25')),
            ('Bread',            'pieces',   40,   10, Decimal('5.00')),
            ('Paneer',           'grams',  1000,  200, Decimal('0.40')),
            ('Pasta',            'grams',  2000,  400, Decimal('0.30')),
        ]
        ing_map = {}
        for name, unit, stock, threshold, cost in ingredients:
            ing, _ = Ingredient.objects.get_or_create(
                name=name,
                defaults={'unit': unit, 'current_stock': stock,
                          'low_stock_threshold': threshold, 'cost_per_unit': cost}
            )
            ing_map[name] = ing

        # Link ingredients to menu items
        links = [
            ('Espresso',       'Espresso Beans', Decimal('18')),
            ('Espresso',       'Sugar',          Decimal('5')),
            ('Cappuccino',     'Espresso Beans', Decimal('18')),
            ('Cappuccino',     'Full-Fat Milk',  Decimal('150')),
            ('Cafe Latte',     'Espresso Beans', Decimal('18')),
            ('Cafe Latte',     'Full-Fat Milk',  Decimal('250')),
            ('Masala Chai',    'Full-Fat Milk',  Decimal('200')),
            ('Masala Chai',    'Chai Masala',    Decimal('3')),
            ('Cold Coffee',    'Espresso Beans', Decimal('20')),
            ('Cold Coffee',    'Full-Fat Milk',  Decimal('200')),
            ('Mango Smoothie', 'Mango Pulp',     Decimal('150')),
            ('Mango Smoothie', 'Full-Fat Milk',  Decimal('100')),
            ('Veg Sandwich',   'Bread',          Decimal('2')),
            ('Paneer Toast',   'Bread',          Decimal('2')),
            ('Paneer Toast',   'Paneer',         Decimal('80')),
            ('Veg Pasta',      'Pasta',          Decimal('150')),
            ('Paneer Wrap',    'Paneer',         Decimal('100')),
        ]
        for item_name, ing_name, qty in links:
            try:
                item = MenuItem.objects.get(name=item_name)
                ing  = ing_map.get(ing_name)
                if item and ing:
                    MenuItemIngredient.objects.get_or_create(
                        menu_item=item, ingredient=ing,
                        defaults={'quantity_used': qty}
                    )
            except MenuItem.DoesNotExist:
                pass

        self.stdout.write('  ✓ Ingredients & menu-item links')

    # ── GST ──────────────────────────────────────────────────────────────────
    def _create_gst(self):
        from apps.billing.models import GSTRate
        GSTRate.objects.get_or_create(
            name='Standard GST',
            defaults={'rate': Decimal('5.00'), 'is_default': True}
        )
        self.stdout.write('  ✓ Default GST rate (5%)')
