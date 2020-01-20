from datetime import datetime, timedelta
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from allauth.socialaccount.models import SocialToken, SocialApp
import requests

def Home(request):
    context = {}
    if request.user.is_authenticated:
        return render(request, 'home.html', context)
    else:
        return render(request, 'index.html', context)


def activities_json(request):
    if request.user.is_authenticated:
        access_token = SocialToken.objects.get(account__user=request.user, account__provider='strava')

        if access_token.expires_at <= timezone.now():
            refresh_token(access_token)

            if access_token.expires_at <= timezone.now():
                return JsonResponse({'error': "Unable to refresh access token", 'activities': None}, safe=False)

        activities = load_activities(access_token)
        return JsonResponse({'error': "", 'activities': activities}, safe=False)

    return JsonResponse({'error': "Unknown Error", 'activities': None}, safe=False)

def load_activities(access_token):

    if access_token.expires_at <= timezone.now():
        return

    endpoint = 'https://www.strava.com/api/v3/athlete/activities'
    headers = {"Authorization": "Bearer " + access_token.token}
    response = requests.get(endpoint, params={'per_page': 100}, headers=headers)

    output = []
    if response.status_code == 200:
        for activity in response.json():
            new_activity = {}   # Only send the fields we use
            new_activity['id'] = activity['id']
            new_activity['name'] = activity['name']
            new_activity['date'] = datetime.strptime(activity['start_date_local'].split('T')[0], "%Y-%m-%d").strftime('%b %d, %Y')
            new_activity['start_latitude'] = activity['start_latitude']
            new_activity['start_longitude'] = activity['start_longitude']
            new_activity['polyline'] = activity['map']['summary_polyline']
            new_activity['distance'] = round(activity['distance'] / 1609, 2)
            seconds_per_mile = activity['moving_time'] / new_activity['distance']
            new_activity['pace'] = str(int(seconds_per_mile // 60)) + ":" + str(int(seconds_per_mile % 60))
            
            if new_activity['polyline']:
                output.append(new_activity)
    return output

def refresh_token(access_token):
    """Refreshes a user's Strava access token"""
    strava = SocialApp.objects.get(provider='strava')

    if not strava:
        raise Exception("Unable to load strava secrets while refreshing token")

    params = {'client_id': strava.client_id, 'client_secret': strava.secret, 'grant_type': 'refresh_token', 'refresh_token': access_token.token_secret}
    response = requests.post("https://www.strava.com/oauth/token", data=params)

    if response.status_code != 200:
        Exception("Unexpected code while refreshing token: %d" % response.status_code)

    response = response.json()
    access_token.token = response['access_token']
    access_token.expires_at = timezone.now() + timedelta(seconds=response['expires_in'])
    access_token.token_secret = response['refresh_token']
    access_token.save()
