from django.db.models import Q
from catalog.models.attributes import Attribute, AttributeName, AttributeValue

class ProductFilter():

    def __init__(self, products, filters_data={}):
        self.queryset = products
        self.filters_data = filters_data

    #Фильтры, которые содержатся в полях
    FIELD_FILTERS = [
        {
            "name": "price",
            "type": AttributeName.RANGE
        },
        {
            "name": "category_id",
            "type": "",
            "value": "category__id"
        }
    ]

    @staticmethod
    def is_field_filter(key):
        for field_obj in ProductFilter.FIELD_FILTERS:
            if(key == field_obj["name"]):
                return True
        return False

    @staticmethod
    def get_field_value(key):
        for field_obj in ProductFilter.FIELD_FILTERS:
            if(key == field_obj["name"]):
                return field_obj.get("value", "")
        return ""

    @staticmethod
    def get_field_type(key):
        for field_obj in ProductFilter.FIELD_FILTERS:
            if(key == field_obj["name"]):
                return field_obj["type"]
        return ""

    def get_filters(self):

        if(not self.queryset.exists()):
            return []

        attributes_qs = Attribute.objects.filter(product__pk__in=self.queryset)

        attr_names = AttributeName.objects.filter(pk__in=attributes_qs.values_list("attribute_name", flat=True).distinct())

        attributes = []

        for attr_name in attr_names:

            attr_values = AttributeValue.objects.filter(pk__in=attributes_qs.filter(attribute_name=attr_name).values_list("attribute_value", flat=True))

            if(attr_name.type_show == AttributeName.RANGE):
                max_value = float("-inf")
                min_value = float("inf")

                for val in attr_values:

                    if(val.get_value() > max_value):
                        max_value = val.get_value()

                    if(val.get_value() < min_value):
                        min_value = val.get_value()

                if(max_value == min_value or max_value == float("-inf") or min_value == float("inf")):
                    continue

            attributes.append({
                "slug": attr_name.slug,
                "title": attr_name.title,
                "values": [
                    {"name": val.get_value(), "slug": val.get_slug() } for val in attr_values
                ],
                "type": attr_name.type_show
            })

        min_price = 0

        max_price = self.queryset.order_by("-price").first().price        

        if(max_price != min_price):
            attributes.append({
                "slug": "price",
                "title": "Цена",
                "values": [{
                    "name": min_price,
                    "slug": min_price
                },
                {
                    "name": max_price,
                    "slug": max_price
                }],
                "type": "range"
            })

        return attributes

    def filter_queryset(self):

        """
            Фильтры приходят в виде python json объекта
            {
                "slug": <Слаг, по-которому ищем атрибут>,
                "value": Приходящее значение, может приходить в нескольких форматах:
                Обычное значение: <Значение>;
                Означает, что значение в диапазоне <Число>-<Число>;
                Означает, что выбирается между значениями <Значение>~<Значение>~...
            }
            Фильтры могут быть обычными - те, которые создаются через админку 
            и
            специальными - которые содержатся в виде отдельного поля (например, цена).
        """

        new_queryset = self.queryset

        for slug in self.filters_data:
            unred_value = self.filters_data[slug]

            if(not slug or not unred_value):
                raise Exception("Не содержится имени или значения фильтра")

            if(self.is_field_filter(slug)):
                if(self.get_field_type(slug) == AttributeName.RANGE):
                    min_value = 0
                    max_value = 0

                    if("-" in unred_value):
                        min_value = float(unred_value.split("-")[0])
                        max_value = float(unred_value.split("-")[1])
                    else:
                        min_value = float(unred_value)
                        max_value = float(unred_value)

                    new_queryset = new_queryset.filter(Q(
                        **{
                            slug + "__gte": min_value,
                            slug + "__lte": max_value 
                        }
                    ))

                else:

                    new_queryset = new_queryset.filter(Q(
                        **{
                            self.get_field_value(slug): unred_value
                        }
                    ))

            else:
                attribute_name = AttributeName.objects.filter(slug=slug).first()

                if(not attribute_name):
                    raise Exception("Фильтра " + slug + " не существует")

                if(attribute_name.type_show == AttributeName.DICT):
                    values = unred_value.split("~")
                    new_queryset = new_queryset.filter(
                        Q(
                            attributes__attribute_name__pk=attribute_name.pk,
                            attributes__attribute_value__slug__in=values
                        )
                    )

                elif(attribute_name.type_show == AttributeName.RADIO):
                    new_queryset = new_queryset.filter(
                        Q(
                            attributes__attribute_name__pk=attribute_name.pk,
                            attributes__attribute_value__slug=unred_value
                        )
                    )

                elif(attribute_name.type_show == AttributeName.RANGE):
                    min_value = 0
                    max_value = 0

                    if("-" in unred_value):
                        min_value = float(unred_value.split("-")[0])
                        max_value = float(unred_value.split("-")[1])
                    else:
                        min_value = float(unred_value)
                        max_value = float(unred_value)

                    new_queryset = new_queryset.filter(
                        Q(
                            Q(attributes__attribute_name__slug=slug)
                            &
                            Q(
                                Q(attributes__attribute_value__digitValue__gte=min_value)
                                &
                                Q(attributes__attribute_value__digitValue__lte=max_value)
                            )
                        )
                    )

        return new_queryset.distinct()