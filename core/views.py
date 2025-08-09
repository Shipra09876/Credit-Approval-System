from django.shortcuts import render
from .models import *
import math
from rest_framework.response import Response
from rest_framework import status
from rest_framework import authentication
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny,IsAuthenticated
from django.shortcuts import get_object_or_404
from asgiref.sync import async_to_sync
import logging
from rest_framework import permissions
from rest_framework.renderers import JSONRenderer
import uuid
from .serializer import *
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework import permissions,renderers
import uuid
from django.utils import timezone
from django.db.models import Sum
from django.db.models.functions import ExtractYear
from datetime import timedelta
import logging

class Register(APIView):
    permission_classes=[AllowAny]
    renderer_classes=[JSONRenderer]

    @swagger_auto_schema(
        operation_description="Register Loan",
        request_body=CustomerSerializer,
        responses={201: openapi.Response(
            description="Customer Registered",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'customer_id': openapi.Schema(type=openapi.TYPE_STRING),
                    'first_name': openapi.Schema(type=openapi.TYPE_STRING),
                    'age': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'monthly_salary': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'approved_limit': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'phone_number': openapi.Schema(type=openapi.TYPE_NUMBER),
                }
            )
        )}
    )


    def post(self,request):

        data=request.data.copy()
        try:
            monthly_salary=int(data.get('monthly_salary'))
            data['monthly_salary']=monthly_salary

            data['approved_limit']=round(monthly_salary*36,-5)

            serializer=CustomerSerializer(data=data)
            if serializer.is_valid():
                customer=serializer.save()

                return Response({
                    "customer_id":customer.customer_id,
                    "name":f"{customer.first_name} {customer.last_name}",
                    "age":customer.age,
                    "monthly_salary":customer.monthly_salary,
                    "approved_limit":customer.approved_limit,
                    "phone_number":str(customer.phone_number),
                },status=status.HTTP_201_CREATED)

            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)},status=status.HTTP_400_BAD_REQUEST)

class CheckEligibility(APIView):
    permission_classes = [AllowAny]
    renderer_classes = [JSONRenderer]

    @swagger_auto_schema(
    operation_description="Check eligibility of a customer for a loan",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['customer_id', 'loan_amount', 'interest_rate', 'tenure'],
        properties={
            'customer_id': openapi.Schema(type=openapi.TYPE_STRING),
            'loan_amount': openapi.Schema(type=openapi.TYPE_NUMBER),
            'interest_rate': openapi.Schema(type=openapi.TYPE_NUMBER),
            'tenure': openapi.Schema(type=openapi.TYPE_INTEGER),
        },
    ),
    responses={200: openapi.Response(
        description="Eligibility Result",
        schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'customer_id': openapi.Schema(type=openapi.TYPE_STRING),
                'approval': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                'interest_rate': openapi.Schema(type=openapi.TYPE_NUMBER),
                'corrected_interest_rate': openapi.Schema(type=openapi.TYPE_NUMBER),
                'tenure': openapi.Schema(type=openapi.TYPE_INTEGER),
                'monthly_installment': openapi.Schema(type=openapi.TYPE_NUMBER),
                'EMI paid on time': openapi.Schema(type=openapi.TYPE_INTEGER),
            }
        )
    )})

    def post(self, request):
        customer_id = request.data.get('customer_id')
        loan_amount = float(request.data.get('loan_amount', 0))
        interest_rate = float(request.data.get('interest_rate', 0))
        tenure = int(request.data.get('tenure', 0))

        try:
            customer_uuid = uuid.UUID(customer_id)
            customer = Customer.objects.get(customer_id=customer_uuid)
        except (ValueError, Customer.DoesNotExist):
            return Response({"error": "Customer not found"}, status=status.HTTP_400_BAD_REQUEST)

        loans = Loan.objects.filter(c_id=customer)

        # Correct lowercase status matching
        paid_on_time = loans.filter(status="past").aggregate(
            total=Sum("EMIs_paid_on_time")
        )["total"] or 0

        no_of_loans = loans.count()

        loans_this_year = loans.annotate(
            start_year=ExtractYear('start_date')
        ).filter(start_year=timezone.now().year).count()

        total_approved_volume = loans.filter(
            status__in=["past", "active"]
        ).aggregate(total=Sum("loan_amount"))["total"] or 0

        current_loans = loans.filter(status="active").aggregate(
            total=Sum("loan_amount")
        )["total"] or 0

        credit_score = 100

        # Credit score deductions
        credit_score -= max(0, (no_of_loans - paid_on_time) * 5)
        if no_of_loans > 5:
            credit_score -= (no_of_loans - 5) * 2
        if loans_this_year > 2:
            credit_score -= (loans_this_year - 2) * 3
        if total_approved_volume < 50000:
            credit_score -= 5
        if current_loans > customer.approved_limit:
            credit_score = 0

        # Determine approval & interest correction
        approval = False
        corrected_interest_rate = interest_rate

        if credit_score > 50:
            approval = True
        elif 30 < credit_score <= 50:
            corrected_interest_rate = max(corrected_interest_rate, 12)
            approval = True
        elif 10 < credit_score <= 30:
            corrected_interest_rate = max(corrected_interest_rate, 16)
            approval = True
        else:
            approval = False

        # Calculate EMI
        corrected_total_amount = loan_amount * (1 + (corrected_interest_rate * tenure / 1200))
        monthly_installment = corrected_total_amount / tenure

        current_emi_sum = loans.filter(status="active").aggregate(
            total=Sum("monthly_installment")
        )["total"] or 0

        if current_emi_sum + monthly_installment > 0.5 * customer.monthly_salary:
            approval = False
        
        if approval:
            start_date = timezone.now().date()
            end_date = start_date + timedelta(days=30 * tenure)

            Loan.objects.create(
                c_id=customer,
                loan_amount=loan_amount,
                tenure=tenure,
                interest_rate=corrected_interest_rate,
                monthly_installment=round(monthly_installment, 2),
                EMIs_paid_on_time=paid_on_time,
                start_date=start_date,
                end_date=end_date,
                status="active",
            )

        return Response({
            "customer_id": str(customer.customer_id),
            "approval": approval,
            "interest_rate": interest_rate,
            "corrected_interest_rate": corrected_interest_rate,
            "tenure": tenure,
            "monthly_installment": round(monthly_installment, 2),
            "EMI paid on time":paid_on_time,
        }, status=status.HTTP_200_OK)

class CreateLoanView(APIView):
    permission_classes=[AllowAny]
    renderer_classes=[JSONRenderer]

    @swagger_auto_schema(
    operation_description="Create and approve a new loan for a customer",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['customer_id', 'loan_amount', 'interest_rate', 'tenure'],
        properties={
            'customer_id': openapi.Schema(type=openapi.TYPE_STRING),
            'loan_amount': openapi.Schema(type=openapi.TYPE_NUMBER),
            'interest_rate': openapi.Schema(type=openapi.TYPE_NUMBER),
            'tenure': openapi.Schema(type=openapi.TYPE_INTEGER),
        },
    ),
    responses={
        201: openapi.Response(
            description="Loan Created",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'loan_id': openapi.Schema(type=openapi.TYPE_STRING),
                    'customer_id': openapi.Schema(type=openapi.TYPE_STRING),
                    'loan_approved': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                    'monthly_installment': openapi.Schema(type=openapi.TYPE_NUMBER),
                }
            )
        ),
        400: "Bad Request",
        404: "Customer Not Found",
    })

    def post(self, request):
        try:
            customer_id = request.data.get('customer_id')
            loan_amount = request.data.get('loan_amount')
            interest_rate = request.data.get('interest_rate')
            tenure = request.data.get('tenure')

            # Fetch customer
            customer = Customer.objects.get(customer_id=customer_id)

            corrected_interest_rate = interest_rate

            if customer.credit_score is not None:
                if customer.credit_score >= 750:
                    corrected_interest_rate = max(interest_rate - 1, 0.0)
                elif customer.credit_score <= 500:
                    corrected_interest_rate = interest_rate + 1


            monthly_installment = (
                loan_amount * (1 + (corrected_interest_rate * tenure / 100)) / tenure
            )

            existing_loans = Loan.objects.filter(c_id=customer, status='active')
            current_emi_sum = sum([loan.monthly_installment for loan in existing_loans])

            if current_emi_sum + monthly_installment > 0.5 * customer.monthly_salary:
                return Response({
                    "loan_id": None,
                    "customer_id": customer_id,
                    "loan_approved": False,
                    "message": "Loan cannot be approved due to high EMI burden",
                    "monthly_installment": round(monthly_installment, 2)
                }, status=status.HTTP_200_OK)

            # Save loan
            start_date = timezone.now().date()
            end_date = start_date + timedelta(days=30 * tenure)
            loan = Loan.objects.create(
                c_id=customer,
                loan_amount=loan_amount,
                tenure=tenure,
                interest_rate=corrected_interest_rate,
                monthly_installment=round(monthly_installment, 2),
                start_date=start_date,
                end_date=end_date,
                status="active"
            )

            return Response({
                "loan_id": loan.loan_id,
                "customer_id": customer_id,
                "loan_approved": True,
                "message": "Loan approved successfully",
                "monthly_installment": round(monthly_installment, 2)
            }, status=status.HTTP_201_CREATED)

        except Customer.DoesNotExist:
            return Response({
                "loan_id": None,
                "customer_id": customer_id,
                "loan_approved": False,
                "message": "Customer not found",
                "monthly_installment": None
            }, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({
                "loan_id": None,
                "customer_id": customer_id,
                "loan_approved": False,
                "message": str(e),
                "monthly_installment": None
            }, status=status.HTTP_400_BAD_REQUEST)

class LoanDetailView(APIView):
    permission_classes=[AllowAny]
    renderer_classes=[JSONRenderer]

    @swagger_auto_schema(
    operation_description="Get loan details by loan_id",
    manual_parameters=[
        openapi.Parameter(
            'loan_id', openapi.IN_PATH, description="Loan ID", type=openapi.TYPE_STRING
        )
    ],
    responses={
        200: openapi.Response(description="Loan Details", schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'loan_id': openapi.Schema(type=openapi.TYPE_STRING),
                'loan_amount': openapi.Schema(type=openapi.TYPE_NUMBER),
                'interest_rate': openapi.Schema(type=openapi.TYPE_NUMBER),
                'monthly_installment': openapi.Schema(type=openapi.TYPE_NUMBER),
                'repayments_left': openapi.Schema(type=openapi.TYPE_INTEGER),
                'tenure': openapi.Schema(type=openapi.TYPE_INTEGER),
                'status': openapi.Schema(type=openapi.TYPE_STRING),
                'start_date': openapi.Schema(type=openapi.TYPE_STRING, format='date'),
                'end_date': openapi.Schema(type=openapi.TYPE_STRING, format='date'),
            }
        )),
        404: "Loan Not Found"
    })

    def get(self, request, loan_id):
        try:
            loan = Loan.objects.get(pk=loan_id)
            serializer = LoanSerializer(loan)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Loan.DoesNotExist:
            return Response({"detail": "Loan not found"}, status=status.HTTP_404_NOT_FOUND)

class ViewCustomerLoans(APIView):
    permission_classes = [AllowAny]
    renderer_classes = [JSONRenderer]

    @swagger_auto_schema(
    operation_description="Get all loans for a customer by customer_id",
    manual_parameters=[
        openapi.Parameter(
            'customer_id', openapi.IN_PATH, description="Customer ID", type=openapi.TYPE_STRING
        )
    ],
    responses={
        200: openapi.Response(description="List of Loans", schema=openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'loan_id': openapi.Schema(type=openapi.TYPE_STRING),
                    'loan_amount': openapi.Schema(type=openapi.TYPE_NUMBER),
                    'interest_rate': openapi.Schema(type=openapi.TYPE_NUMBER),
                    'monthly_installment': openapi.Schema(type=openapi.TYPE_NUMBER),
                    'repayments_left': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'tenure': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'status': openapi.Schema(type=openapi.TYPE_STRING),
                    'start_date': openapi.Schema(type=openapi.TYPE_STRING, format='date'),
                    'end_date': openapi.Schema(type=openapi.TYPE_STRING, format='date'),
                }
            )
        )),
        404: "Loan Not Found"
    })
    def get(self, request, customer_id):
        loans = Loan.objects.filter(c_id__customer_id=customer_id)
        if not loans.exists():
            return Response({'detail': 'Loan not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = LoanSerializer(loans, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

