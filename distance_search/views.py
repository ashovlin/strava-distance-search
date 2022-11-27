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

def privacy(request):
    return render(request, 'privacy.html')
    
def activities_json(request):
    if request.user.is_authenticated:

        try:
            access_token = SocialToken.objects.get(account__user=request.user, account__provider='strava')
        except SocialToken.DoesNotExist:
            return JsonResponse({'error': "Unable to load access token", 'activities': None}, safe=False)

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
            activity = prep_activity_for_display(activity)
        
            if should_display_activity(activity):
                output.append(activity)
    return output

def prep_activity_for_display(activity):
    """Adds some fields and/or formatting that we use for display to a Strava activity"""

    # Convert Y-m-d to display format
    local_date_part = activity['start_date_local'].split('T')[0]
    local_date = datetime.strptime(local_date_part, "%Y-%m-%d")
    activity['date'] = local_date.strftime('%b %d, %Y')

    activity['polyline'] = activity['map']['summary_polyline']

    # Covert meters to miles
    activity['distance'] = round(activity['distance'] * 0.000621371, 2)

    # Calculate minutes:seconds per mile
    seconds_per_mile = activity['moving_time'] / activity['distance']
    minutes = int(seconds_per_mile // 60)
    seconds = round(seconds_per_mile % 60)
    activity['pace'] = str(minutes) + ":" + str(seconds).zfill(2)

    return activity

def should_display_activity(activity):
    """Determines whether we should display should be displayed (pending distance filters)"""

    if activity['type'] != "Run": # other activities aren't supported yet
        return False

    if not activity['polyline']: # discards treadmill runs
        return False

    return True

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
