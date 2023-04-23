from rest_framework import serializers
from convert_currency_api.models import Rate
# from transactions.models import Amount
# from transactions.models import MoneyTransfer

"""
RateSerializer serializes all the fields in the Rate model.
"""
class RateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Rate
        fields = ('__all__')
