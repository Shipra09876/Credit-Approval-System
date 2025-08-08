from celery import shared_task
import pandas as pd
from datetime import datetime

@shared_task
def import_customer_data(file_path):
    from core.models import Customer
    import pandas as pd

    df = pd.read_excel(file_path, dtype={'Phone Number': str})  

    for _, row in df.iterrows():
        try:
            salary = row['Monthly Salary']
            approved_limit = round(salary * 36, -5)

            raw_phone = str(row['Phone Number']).strip()

            if raw_phone.startswith('+'):
                phone_str = raw_phone
            else:
                raw_phone = raw_phone.lstrip('0') 
                phone_str = '+91' + raw_phone

            Customer.objects.get_or_create(
                customer_id=row['Customer ID'],
                first_name=row['First Name'],
                last_name=row['Last Name'],
                phone_number=phone_str,
                age=row['Age'],
                monthly_salary=salary,
                approved_limit=approved_limit,
            )

        except Exception as e:
            print(f"Error importing row {row['Customer ID']}: {e}")


@shared_task

def import_loan_data(file_path):
    from core.models import Customer ,Loan

    df=pd.read_excel(file_path)
    for _,row in df.iterrows():
        customer=Customer.objects.get(id=row['Customer ID'])
        status='past' if row['EMIs paid on Time']>=row['Tenure'] else 'active'

        loan=Loan.objects.get_or_create(
            cid=customer,
            loan_id=row['Loan ID'],
            loan_amount=row['Loan Amount'],
            tenure=row['Tenure'],
            interest_rate=row['Interest Rate'],
            monthly_installment=row['Monthly payment'],
            EMIs_paid_on_time=row['EMIs paid on Time'],
            status=status,
            start_date=row['Date of Approval'],
            end_date=row['End Date']
        )

    for customer in Customer.objects.all():
        active_loans=customer.loan_set.filter(status='active')
        current_debt=sum(loan.loan_amount for loan in active_loans)
        customer.current_debt=current_debt
        customer.save()



