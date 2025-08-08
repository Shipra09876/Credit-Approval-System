from django.urls import path , include
from .views import *

urlpatterns=[
    path("register/",Register.as_view(),name="register"),
    path("check_eligibility/",CheckEligibility.as_view(),name="Check-eligibilty"),
    path("create_loan/",CreateLoanView.as_view(),name="create-loan"),
    path("view-loan/<str:loan_id>/",LoanDetailView.as_view(),name="Loan-details"),
    path("view-loan/<str:customer_id>/",ViewCustomerLoans.as_view(),name="view-customer-loans"),


]