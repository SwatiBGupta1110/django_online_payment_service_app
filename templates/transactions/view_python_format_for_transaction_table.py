# from django.shortcuts import render
# from myapp.models import Transaction
#
# def transactions(request):
#     transactions = Transaction.objects.all()
#     context = {'transactions': transactions}
#     return render(request, 'transactions.html', context)
"""

In this template, the {% for transaction in transactions %}
 loop iterates through a list of transactions, and for each transaction, 
 it generates a row in the HTML table with the transaction's data. 
 The {{ transaction.username }}, {{ transaction.amount }}, {{ transaction.type }}, 
 and {{ transaction.date }} variables are replaced with the actual values for each transaction.

In your Django view function, you can pass a list of transaction objects to
 the template as a context variable, like this:

Here, Transaction.objects.all() fetches all the transaction objects from the database, 
and passes them to the transactions.html template as the 
transactions context variable. The template uses this variable to generate the HTML table.
"""