from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .restapis import get_request, analyze_review_sentiments, post_review
from .models import CarMake, CarModel
from .populate import initiate

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


def get_cars(request):
    count = CarMake.objects.filter().count()

    if count == 0:
        initiate()

    car_models = CarModel.objects.select_related('car_make')

    cars = []

    for car_model in car_models:
        cars.append({
            "CarModel": car_model.name,
            "CarMake": car_model.car_make.name
        })

    return JsonResponse({"CarModels": cars})


def get_dealerships(request, state="All"):
    if state == "All":
        endpoint = "/fetchDealers"
    else:
        endpoint = "/fetchDealers/" + state

    dealerships = get_request(endpoint)

    return JsonResponse({
        "status": 200,
        "dealers": dealerships
    })

def get_dealer_reviews(request, dealer_id):

    endpoint = "/fetchReviews/dealer/" + str(dealer_id)

    reviews = get_request(endpoint)

    if reviews:

        for review in reviews:

            sentiment_response = analyze_review_sentiments(
                review.get("review", "")
            )

            if sentiment_response:
                review["sentiment"] = sentiment_response.get(
                    "sentiment", "neutral"
                )
            else:
                review["sentiment"] = "neutral"

    return JsonResponse({
        "status": 200,
        "reviews": reviews
    })

def get_dealer_details(request, dealer_id):
    endpoint = "/fetchDealer/" + str(dealer_id)

    dealer = get_request(endpoint)

    return JsonResponse({
        "status": 200,
        "dealer": dealer
    })

def add_review(request):

    if request.user.is_anonymous == False:

        data = json.loads(request.body)

        try:
            response = post_review(data)

            print(response)

            return JsonResponse({
                "status": 200
            })

        except:
            return JsonResponse({
                "status": 401,
                "message": "Error in posting review, 401 error"
            })

    else:

        return JsonResponse({
            "status": 403,
            "message": "Unauthorized"
        })