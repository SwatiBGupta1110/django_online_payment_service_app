from rest_framework import serializers
from convert_currency_api.models import Rate
# from transactions.models import Amount
# from transactions.models import MoneyTransfer

class RateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Rate
        fields = ('__all__')

# class AmountSerializer(serializers.ModelSerializer):
#
#     class Meta:
#         model = Amount
#         fields = ('__all__')
#
#
# class MoneyTransferSerializer(serializers.ModelSerializer):
#
#     class Meta:
#         model = MoneyTransfer
#         fields = ('__all__')