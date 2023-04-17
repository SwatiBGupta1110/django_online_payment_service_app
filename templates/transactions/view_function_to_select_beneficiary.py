# from django.shortcuts import render
# from django.contrib.auth.decorators import login_required
# from .models import Beneficiary
#
# @login_required
# def select_beneficiary(request):
#     user = request.user
#     beneficiaries = Beneficiary.objects.filter(user=user)
#     context = {
#         'beneficiaries': beneficiaries
#     }
#     return render(request, 'select_beneficiary.html', context)

"""
In this example, we assume that you have a Beneficiary model that has a foreign key to the User model.
 The select_beneficiary view function retrieves all the beneficiaries for the logged-in user and passes them to the select_beneficiary.html template.

In your HTML template, you can use Django's template language to iterate over 
the beneficiaries and generate the <option> elements for the <select> element. Here's an example:

"""
##############################Latest one #####################

# from django.shortcuts import render
#
# def handle_request(request):
#     if request.method == 'POST':
#         # Get the beneficiary and amount from the POST request
#         beneficiary = request.POST.get('beneficiary')
#         amount = request.POST.get('amount')
#         # Do something with the beneficiary and amount, such as saving to a database
#         # ...
#         # Render a success page or redirect to another page
#         return render(request, 'success.html')
#     else:
#         # Render the form page
#         return render(request, 'request.html')


"""
This view function assumes that you have two templates: request.html and success.html. 
The request.html template would contain the form HTML you provided, and the success.html template 
would contain a success message or any other content you want to show after the request is successfully handled. 
Make sure to update the template names to match your actual template names.
"""