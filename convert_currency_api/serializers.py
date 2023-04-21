from rest_framework import serializers
from convert_currency_api.models import Rate
# from transactions.models import Amount
# from transactions.models import MoneyTransfer

class RateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Rate
        fields = ('__all__')
