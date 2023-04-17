# from django.shortcuts import render
# from django.contrib.auth.decorators import login_required
#
# @login_required
# def approval_table(request):
#     user_email = request.user.email
#     beneficiaries = [
#         {"name": "Beneficiary 1", "amount": 1000},
#         {"name": "Beneficiary 2", "amount": 2500},
#     ]  # Replace with data fetched from database using user_email
#
#     context = {
#         "user_email": user_email,
#         "beneficiaries": beneficiaries,
#     }
#     return render(request, "approval_table.html", context)

"""

In this example, we're using Django's built-in @login_required decorator
to ensure that the view is only accessible to authenticated users. The user_email variable is
then set to the authenticated user's email address using the request.user.email property.

We've also defined a list of beneficiaries with dummy data, but you can
 replace this with data fetched from your database using the user_email variable.

Finally, we're passing the user_email and beneficiaries variables to the template context
using a dictionary, and rendering the approval_table.html template with the context using the render function. You'll need to create the approval_table.html template file and use the
user_email and beneficiaries variables to dynamically generate the table.

"""