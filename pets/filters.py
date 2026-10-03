import django_filters as df

from .models import Pet


class PetFilter(df.FilterSet):
    name = df.CharFilter(lookup_expr="icontains")
    breed = df.CharFilter(lookup_expr="icontains")
    location = df.CharFilter(lookup_expr="icontains")
    animal_type = df.CharFilter(lookup_expr="iexact")
    gender = df.CharFilter(lookup_expr="iexact")
    status = df.CharFilter(lookup_expr="iexact")

    class Meta:
        model = Pet
        fields = ["name", "breed", "location", "animal_type", "gender", "status"]
