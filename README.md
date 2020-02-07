# strava-distance-search
Search for your Strava activities within a distance range:
![GIF of main UI](https://alexshovlin.com/images/sds.gif)

## Running Locally
1. `pipenv shell`
2. `pipenv install`
3. Set a Django secret key to use locally in `dev_vars.sh`, then `source dev_vars.sh`
4. `python manage.py migrate` if necessary
5. In Django admin create a 'Social Application' record with your Strava application's client ID and secret key (see [django-allauth docs](https://django-allauth.readthedocs.io/en/latest/installation.html#post-installation) for more)
6. `python manage.py runserver`

## Tests and Coverage
1. `coverage run --source='.' manage.py test distance_search`
2. `coverage report`
