from collections import OrderedDict
from decimal import *
import csv
import datetime
import os

from peewee import *


db = SqliteDatabase('inventory.db')


class Product(Model):
    product_id = AutoField()
    product_name = TextField(unique=True)
    product_quantity = IntegerField(default=0)
    product_price = IntegerField(default=0)
    date_updated = DateField(default=datetime.datetime.now)

    class Meta:
        database = db


class init():
    db.connect()
    db.create_tables([Product], safe=True)


def get_existing_inventory():
    file = None
    if os.path.exists('backup.csv'):
        file = 'backup.csv'
    else:
        file = 'inventory.csv'
    with open(file, newline='') as file:
        inventory_reader = csv.DictReader(file, delimiter=',')
        inventory = list(inventory_reader)
        for item in inventory:
            try:
                Product.create(
                    product_name = item['product_name'],
                    product_quantity = int(item['product_quantity']),
                    product_price = int(Decimal(item['product_price'].
                        replace('$','')) * 100),
                    date_updated = datetime.datetime.strptime(
                        item['date_updated'], '%m/%d/%Y'))
            except IntegrityError:
                existing_item = Product.get(product_name = item['product_name'])
                if existing_item.date_updated < datetime.datetime.strptime(
                    item['date_updated'], '%m/%d/%Y').date():
                    existing_item.product_quantity = int(
                        item['product_quantity'])
                    existing_item.product_price = int(Decimal(
                        item['product_price'].replace('$', '')) * 100)
                    existing_item.date_updated = datetime.datetime.strptime(
                        item['date_updated'], '%m/%d/%Y')
                    existing_item.save()


def view_details():
    '''View a single product's inventory'''
    while True:
        try:
            selected_id = input(
                'Please enter the Product ID (1...{}) or "Q" to quit:  '.
                    format(Product.select().count())).upper()
            if selected_id == 'Q':
                os.system('cls' if os.name == 'nt' else 'clear')
                break
            else:
                selected_id = int(selected_id)
            if selected_id > Product.select().count() or selected_id < 1:
                raise ValueError
        except ValueError:
            print('Invalid ID, try again...')
        else:
            os.system('cls' if os.name == 'nt' else 'clear')
            item = Product.select().where(Product.product_id==selected_id).get()
            item_price = Decimal(item.product_price / 100)
            print('ID: {}\nName: {}\nQuantity: {}\nPrice: ${:,.2f}\n'.
                format(item.product_id,
                       item.product_name,
                       item.product_quantity,
                       item_price))


def add_new_product():
    '''Add a new product to the database'''
    os.system('cls' if os.name == 'nt' else 'clear')
    while True:
        item_name = input('Please enter the item name: ').strip()
        if item_name == '':
            print('Item must have a name.')
        else:
            break
    while True:
        try:
            item_quantity = int(input(
                'Please enter the item quantity (no commas): '))
            if item_quantity < 0 or item_quantity > 999999:
                raise ValueError
        except ValueError:
            print('Invalid Entry')
            print('Acceptable range is 0 - 999999, whole numbers only.')
        else:
            break
    while True:
        try:
            item_price = input('Please enter the item price (no commas): $')
            if item_price == '':
                item_price = 0
            if not float(item_price):
                raise ValueError
        except ValueError:
            print('Please enter a valid price.')
        else:
            break
    item_updated = datetime.datetime.today()

    try:
        Product.create(
            product_name = item_name,
            product_quantity = item_quantity,
            product_price = int(Decimal(item_price.replace('$','')) * 100),
            date_updated = item_updated)
    except IntegrityError:
        existing_item = Product.get(product_name = item_name)
        if existing_item.date_updated < item_updated.date():
            existing_item.product_quantity = item_quantity
            existing_item.product_price = int(Decimal(
                item_price.replace('$', '')) * 100)
            existing_item.date_updated = item_updated
            existing_item.save()
    os.system('cls' if os.name == 'nt' else 'clear')


def backup():
    '''Make a backup of the entire inventory'''
    with open('backup.csv', 'w') as csvfile:
        field_names = ['product_name',
                       'product_price',
                       'product_quantity',
                       'date_updated']
        writer = csv.DictWriter(csvfile, fieldnames=field_names)
        writer.writeheader()
        for item in Product:
            writer.writerow({
                'product_name' : item.product_name,
                'product_price' : item.product_price,
                'product_quantity' : item.product_quantity,
                'date_updated' : item.date_updated.strftime('%m/%d/%Y')
            })


def quit():
    '''Quit Application'''
    print('\nHave a great day!\n')


def begin_user_interface():
    while True:
        print('''
########################
     Inventory Menu
########################
        ''')
        for key, value in menu.items():
            print('{}) {}'.format(key, value.__doc__))
        user_choice = input('\nPlease choose from above:  ').upper()
        if user_choice in menu:
            os.system('cls' if os.name == 'nt' else 'clear')
            menu[user_choice]()
            if user_choice == 'Q':
                break
        else:
            input('\nNot a valid option. Press ENTER or RETURN to continue...')
            os.system('cls' if os.name == 'nt' else 'clear')


menu = OrderedDict([
    ('V', view_details),
    ('A', add_new_product),
    ('B', backup),
    ('Q', quit)
])


if __name__ == '__main__':
    os.system('cls' if os.name == 'nt' else 'clear')
    init()
    get_existing_inventory()
    begin_user_interface()
