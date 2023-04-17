# from django.shortcuts import render
#
# def approve_or_reject_request(request):
#     if request.method == 'POST':
#         amount = request.POST.get('amount')
#         action = request.POST.get('action')
#         # handle the approve or reject action here
#         # for example, you can update the status of the request in the database
#
#     return render(request, 'template.html', context)

"""
In the HTML template, you can create a form for each request with a hidden
input field containing the ID of the request. When the user clicks the "Approve"
or "Reject" button, the form is submitted with the corresponding action and the ID of the request.

To display the status of each request, you can add a column to the table in the
template with the status of the request (approved, rejected, or pending). You can retrieve the status of each request from the database and display it in the table. If you want to indicate whether the request was approved or rejected by the user, you can add a column to the table with the action taken by the user (approved or rejected). This information can also be stored in the database.







"""