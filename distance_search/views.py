from django.views.generic import TemplateView
from django.shortcuts import render
from allauth.socialaccount.models import SocialToken
import requests
from django.http import JsonResponse

def Home(request):
    context = {}

    if request.user.is_authenticated:
        access_token = SocialToken.objects.get(account__user=request.user, account__provider='strava')
        context['activities'] = load_activities(access_token)
        return render(request, 'home.html', context)
    else:
        return render(request, 'index.html', context)

def load_activities(access_token):
    endpoint = 'https://www.strava.com/api/v3/athlete/activities'
    headers = {"Authorization": "Bearer " + access_token.token}
    response = requests.get(endpoint, headers=headers)
    return response.json()

def activities_json(request,distance):
    print(distance)
    if request.user.is_authenticated:
        access_token = SocialToken.objects.get(account__user=request.user, account__provider='strava')
        return JsonResponse(load_activities(access_token),safe=False)
    else:
        return JsonResponse("")