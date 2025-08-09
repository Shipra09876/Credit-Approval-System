#  Credit Loan Approval System  

This is a Django-based Credit Approval System that allows uploading customer data, processing it asynchronously with Celery, managing loans, checking loan eligibility, and viewing details using REST APIs with Swagger documentation

## DEMO Video Link 
```bash 
  drive.google.com/file/d/10TXJq97RkB5B81juhbgjo4NST2HT2hF-/view
```

## 🐳 Run with Docker

### Prerequisites

- Docker Desktop installed and running
- Docker Compose installed (`docker compose` command should work)
  
### 🚀 Steps to Run the App

 **Clone the Repository**
   ```bash
   git clone https://github.com/your-username/your-repo-name.git
   cd your-repo-name
   ```

## Build and Start the Containers
   ```bash
    docker compose up --build
   ```

## Visit the Application
 ```bash
    Open your browser and go to: http://localhost:8000

 ```

### Enviornment setup 
```bash
    python3 -m venv venv
```

### Backend project setup 
```bash
    django-admin startproject project_name .
    cd project_name
    python manage.py startapp app_name
    python manage.py makemigrations
    python manage.py migrate
    python manage.py createsuperuser
    python manage.py runserver
```
### Backend Installation 
```bash
    pip install django djangorestframework   
    pip install psycopg2-binary
    pip install django-cors-headers
    pip install python-decouple drf-yasg

```
    
## Environment Variables

To run this project, you will need to add the following environment variables to your .env file


### Database (PostgreSQL)
```bash
DB_USER=postgresql
```

### CORS
``` bash
    ALLOWED_HOSTS=localhost,127.0.0.1:8000
```

### Cache (optional)
```bash
    REDIS_URL=redis://127.0.0.1:6379/0
```
## Features

✅ Customer data upload via Excel

✅ Asynchronous background processing using Celery + Redis

✅ RESTful APIs to manage customers and loans

✅ Swagger documentation for easy API testing

✅ PostgreSQL as the database

✅ Dockerized development environment

✅ Admin panel for managing models

✅ pgAdmin for DB inspection


## API Reference

#### Register

```bash 
  POST  http://localhost:8000/register/
```

| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `first_name` | `string` | **Required**  |
| `last name` | `string` | **Required**  |
| `age` | `int` | **Required**  |
| `monthly income` | `int` | **Required**  |
| `phone number` | `phone number` | **Required**  |


#### check eligibility

```bash
  POST /check-eligibility/
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `customer_id`      | `uuid` | **Required**. Id of item to fetch |
| `loan_amount`     | `float` | **Required**. |
| `interest_rate`      | `float` | **Required** |
| `tenure`      | `int` | **Required**.|


#### create loan

```bash
  POST /create-loan/
```
| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `customer_id`      | `uuid` | **Required**. Id of item to fetch |
| `loan_amount`     | `float` | **Required**. |
| `interest_rate`      | `float` | **Required** |
| `tenure`      | `int` | **Required**.|

#### view loan via loan_id

```bash
  GET /view-loan/loan_id/
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `loan_id`    | 'uuid' | **Required** |

#### view loan via customer_id

```bash
  GET /view-loan/customer_id/
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `customer_id`    | 'uuid' | **Required** |

#### Swagger api 

```bash
   http://localhost:8000/swagger/
```

## Admin Panel
``` bash
    http://localhost:8000/admin
```

## pgAdmin: 
```bash 
    http://localhost:5050 (login: admin@admin.com / admin)
```

## Tech Stack 
- Backend	: Django, Django REST Framework (DRF), UUID, Django Caching
- Database	: Postgresql 
- API Docs	: drf-yasg (Swagger),postman 
- Caching	: Redis 
- UUIDs	    : For unique Book and Review IDs 
- Background Task : Celery

## 🐳 Docker Services
```bash 
    Service	|Port |	Description
    web	|8000 |	Django app
    db	|5432 |	PostgreSQL DB
    pgadmin	|5050 |	GUI for PostgreSQL
    redis	| 6379 |Celery broker
```


# Hi, I'm Shipra Gupta! 👋


## 🚀 About Me
I'm a full stack developer...


## 🔗 Links
[![linkedin](https://img.shields.io/badge/linkedin-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/shipra-guptaa/)

