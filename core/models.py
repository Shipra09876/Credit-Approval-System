from django.db import models
import uuid
from phonenumber_field.modelfields import PhoneNumberField
from django.utils import timezone

class Customer(models.Model):
    customer_id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    first_name=models.CharField(max_length=100)
    last_name=models.CharField(max_length=100)
    phone_number=PhoneNumberField(region='IN')
    monthly_salary=models.FloatField()
    age=models.IntegerField()
    approved_limit=models.FloatField(blank=True)
    current_debt=models.FloatField(default=0.0)
    credit_score = models.IntegerField(null=True, blank=True)


    def save(self,*args,**kwargs):
        self.approved_limit=self.monthly_salary*36
        super().save(*args,**kwargs)

        
    def update_curr_debt(self):
        active_loan=self.loans.filter(status='active')
        self.current_debt=sum([loan.remaining_bal() for loan in active_loan])
        self.save()

    def __str__(self):
        return f"{self.first_name} - {self.last_name}-{self.monthly_salary} - {self.approved_limit}"

class Loan(models.Model):
    c_id=models.ForeignKey(Customer,on_delete=models.CASCADE,related_name='loans')
    loan_id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    loan_amount=models.FloatField()
    tenure=models.IntegerField()
    interest_rate=models.FloatField()
    monthly_installment=models.IntegerField()
    EMIs_paid_on_time=models.IntegerField(default=0)
    status_choices=[
        ('past','Past'),
        ('active','Active')
    ]
    status=models.CharField(max_length=100,choices=status_choices,default='active')
    start_date=models.DateField()
    end_date=models.DateField()

    def remaining_bal(self):
        return (self.tenure-self.EMIs_paid_on_time)*self.monthly_installment

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.c_id.update_curr_debt()

    def __str__(self):
        return f"{self.c_id}-{self.loan_amount}-{self.status}"