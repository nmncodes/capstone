from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

import logging
import json

logger = logging.getLogger(__name__)


# Login
@csrf_exempt
def login_user(request):
    data = json.loads(request.body)

    username = data['userName']
    password = data['password']

    user = authenticate(username=username, password=password)

    response_data = {"userName": username}

    if user is not None:
        login(request, user)
        response_data = {
            "userName": username,
            "status": "Authenticated"
        }

    return JsonResponse(response_data)


# Logout
@csrf_exempt
def logout_request(request):
    logout(request)
    return JsonResponse({"userName": ""})


# Register
@csrf_exempt
def registration(request):

    data = json.loads(request.body)

    username = data['userName']
    password = data['password']
    first_name = data['firstName']
    last_name = data['lastName']
    email = data['email']

    username_exist = False

    try:
        User.objects.get(username=username)
        username_exist = True
    except User.DoesNotExist:
        logger.debug(f"{username} is a new user")

    if not username_exist:
        user = User.objects.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            password=password,
            email=email
        )

        login(request, user)

        return JsonResponse({
            "userName": username,
            "status": "Authenticated"
        })

    return JsonResponse({
        "userName": username,
        "error": "Already Registered"
    })


# Future dealership views
# def get_dealerships(request):
#     pass

# def get_dealer_reviews(request, dealer_id):
#     pass

# def get_dealer_details(request, dealer_id):
#     pass

# def add_review(request):
#     pass