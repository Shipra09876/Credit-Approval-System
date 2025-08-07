from django.contrib import admin
from .models import *

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display=['customer_id','first_name','last_name','phone_number','monthly_salary','age','approved_limit','current_debt']
    list_filter=['customer_id','first_name','last_name','monthly_salary']
    search_fields=['customer_id','monthly_salary']
    readonly_fields=['approved_limit','current_debt']

@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display=['c_id','loan_id','loan_amount','tenure','interest_rate','monthly_installment','EMIs_paid_on_time','status','start_date','end_date']
    list_display=['c_id','loan_amount','interest_rate','monthly_installment','status','start_date','end_date']
    
