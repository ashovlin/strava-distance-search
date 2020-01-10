from django.views.generic import TemplateView
from django.shortcuts import render
from allauth.socialaccount.models import SocialToken
import requests
from datetime import datetime
from django.http import JsonResponse
from django.utils import timezone

def Home(request):
    context = {}
    if request.user.is_authenticated:
        return render(request, 'home.html', context)
    else:
        return render(request, 'index.html', context)


def activities_json(request):
    if request.user.is_authenticated:
        access_token = SocialToken.objects.get(account__user=request.user, account__provider='strava')
        activities = load_activities(access_token)
        if access_token.expires_at <= timezone.now():
            return JsonResponse({'error': "Token is Expired", 'activities': None}, safe=False)
        
        return JsonResponse({'error': "", 'activities': activities}, safe=False)
    else:
        return JsonResponse({'error': "Not logged in", 'activities': None}, safe=False)

def load_activities(access_token):

    if access_token.expires_at <= timezone.now():
        print("TODO - need to refresh token")

    endpoint = 'https://www.strava.com/api/v3/athlete/activities'
    headers = {"Authorization": "Bearer " + access_token.token}
    response = requests.get(endpoint, params={'per_page': 10}, headers=headers)

    output = []
    if response.status_code == 200:
        for activity in response.json():
            new_activity = {}
            new_activity['name'] = activity['name']
            new_activity['date'] = datetime.strptime(activity['start_date_local'].split('T')[0], "%Y-%M-%d").date()
            new_activity['distance'] = round(activity['distance'] / 1609, 2)
            output.append(new_activity)
    return output
