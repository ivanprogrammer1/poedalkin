from bs4 import BeautifulSoup
import requests
import json
from django.core.management.base import BaseCommand
from catalog.models import Product, Category, CollectionProduct, ProductImage, AttributeName, AttributeValue, Attribute
from django.core.files.base import ContentFile
import os

BASIC_URL = "https://xn--80abbzadjtkj5g.xn--p1ai"

categories = [
    {
        "title": "Пицца",
        "link": "https://xn--80abbzadjtkj5g.xn--p1ai/menu/pizza"
    },
    {
        "title": "Роллы",
        "link": "https://xn--80abbzadjtkj5g.xn--p1ai/menu/rolly"
    },
    {
        "title": "Вок",
        "link": "https://xn--80abbzadjtkj5g.xn--p1ai/menu/vok"
    },
    {
        "title": "Салаты",
        "link": "https://xn--80abbzadjtkj5g.xn--p1ai/menu/salaty"
    },
    {
        "title": "Супы",
        "link": "https://xn--80abbzadjtkj5g.xn--p1ai/menu/supy"
    },
    {
        "title": "Закуски",
        "link": "https://xn--80abbzadjtkj5g.xn--p1ai/menu/goryachie-zakuski"
    },
    {
        "title": "Пасты",
        "link": "https://xn--80abbzadjtkj5g.xn--p1ai/menu/pasta"
    },
    {
        "title": "Десерты",
        "link": "https://xn--80abbzadjtkj5g.xn--p1ai/menu/deserty"
    },
    {
        "title": "Напитки",
        "link": "https://xn--80abbzadjtkj5g.xn--p1ai/menu/napitki"
    },
    {
        "title": "Соусы",
        "link": "https://xn--80abbzadjtkj5g.xn--p1ai/menu/sousi"
    },
    {
        "title": "Детское",
        "link": "https://xn--80abbzadjtkj5g.xn--p1ai/menu/detskoe-menu"
    }
]

restaraunt_id = "2dec7b3d-b12a-4e27-8c61-53607d26f817"

class Command(BaseCommand):

    def handle(self, *args, **options):
        for item in categories:

            title = item["title"]
            href = item["link"]

            html_doc = requests.get(href).content
            soup = BeautifulSoup(html_doc, 'html.parser')

            list = soup.select_one(".product-list")

            items = list.select(".productBox")

            category = Category.objects.filter(title=title).first()
            if(not category):
                category = Category(title=title)
                
            category.active = True
            category.save()

            for item in items:
                prod_link = BASIC_URL + item.select_one(".title > a").attrs["href"]
                try:
                    self.parse_product(prod_link, category)
                except:
                    raise

    def parse_product(self, href, category):

        uglevody = AttributeName.objects.get(slug="uglevody")
        kalorii = AttributeName.objects.get(slug="kalorii")
        zhiry = AttributeName.objects.get(slug="zhiry")
        belki = AttributeName.objects.get(slug="belki")

        html_doc = requests.get(href).content
        soup = BeautifulSoup(html_doc, 'html.parser')
        prod_id = soup.select_one("menu-constructor").attrs["constructor-id"]

        product_api = BASIC_URL + "/api/json/menu/constructor/" + prod_id + "?restaurant=" + restaraunt_id
        print(product_api)

        json_obj = requests.get(product_api).json()

        answer_obj = json_obj["answer"]

        basic_name = str(answer_obj["Name"])
        parse_id = str(answer_obj["ID"])
        small_description = str(answer_obj.get("Description", ""))
        default_price = float(answer_obj["Price"])

        uglevody_value = float(answer_obj["CarbohydrateAmount"])
        kalorii_value = float(answer_obj["EnergyAmount"])
        zhiry_value = float(answer_obj["FatAmount"])
        belki_value = float(answer_obj["ProteinsAmount"])

        photo_name, photo_content = self.download_image(BASIC_URL + answer_obj["OriginalImage"]["Path"])

        options = answer_obj["Options"]

        if(len(options.keys()) == 0):

            product = Product.objects.filter(id_parse=parse_id).first()

            if(not product):
                product = Product(id_parse=parse_id)

            product.title = basic_name
            product.small_description = small_description
            product.price = default_price
            product.category = category
            product.active = True
            product.save()
            
            self.set_digit_attribute(uglevody, uglevody_value, product)
            self.set_digit_attribute(kalorii, kalorii_value, product)
            self.set_digit_attribute(zhiry, zhiry_value, product)
            self.set_digit_attribute(belki, belki_value, product)

            if(product.gallery.all()):
                for imageObj in product.gallery.all():
                    imageObj.image.delete()
                    imageObj.delete()

            imageObj = ProductImage(
                product=product,
                main_image=True
            )

            imageObj.image.save(photo_name, photo_content)
            imageObj.save()

        else:
            collection = CollectionProduct.objects.filter(title=basic_name).first()

            if(not collection):
                collection = CollectionProduct(title=basic_name)

            collection.save()

            if(collection.image):
                collection.image.delete()

            collection.image.save(photo_name, photo_content, save=True)

            collection.small_description = small_description
            collection.save()

            for _, categoryOption in options.items():

                for option in categoryOption:

                    option_name = option['Title']
                    option_id = option['ID']
                    option_small_description = option.get('Description', "")
                    option_price = float(option['Price'])

                    option_uglevody_value = float(option["CarbohydrateAmount"])
                    option_kalorii_value = float(option["EnergyAmount"])
                    option_zhiry_value = float(option["FatAmount"])
                    option_belki_value = float(option["ProteinsAmount"])

                    option_obj = Product.objects.filter(id_parse=option_id).first()
                    
                    if(not option_obj):
                        option_obj = Product(id_parse=option_id)

                    option_name = " ".join(basic_name.split()) + " " + " ".join(option_name.split()) + " " + " ".join(option_small_description.split())

                    option_obj.title = option_name
                    option_obj.small_description = option_small_description
                    option_obj.price = option_price
                    option_obj.collection = collection
                    option_obj.active = True
                    option_obj.category = category
                    option_obj.save()

                    self.set_digit_attribute(uglevody, option_uglevody_value, option_obj)
                    self.set_digit_attribute(kalorii, option_kalorii_value, option_obj)
                    self.set_digit_attribute(zhiry, option_zhiry_value, option_obj)
                    self.set_digit_attribute(belki, option_belki_value, option_obj)

    def download_image(self, link):
        photo = requests.get(link).content
        return os.path.basename(link), ContentFile(photo)

    def set_digit_attribute(self, nameValue, value, product):
        valueObj, _ = AttributeValue.objects.get_or_create(digitValue=value, type_value=AttributeValue.DIGIT)
        _, created = Attribute.objects.get_or_create(
            attribute_name=nameValue,
            attribute_value=valueObj,
            product=product
        )
