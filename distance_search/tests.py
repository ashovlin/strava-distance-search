from django.test import TestCase
from . import views


class ActivityTests(TestCase):
    """Tests for our handling of Strava activities"""

    def prep_minimal_activity(self):
        """Prepares an activity dict with the fields we assume are always included from Strava"""
        activity = {}
        activity['start_date_local'] = "2020-02-07T"
        activity['map'] = {'summary_polyline': ''}
        activity['distance'] = 0
        activity['moving_time'] = 0
        return activity

    def test_pace_formatted_properly_for_exact_minute(self):
        """Tests that 10:00/mi pace is formated with both zeros as seconds"""
        activity = self.prep_minimal_activity()
        activity['distance'] = 1609
        activity['moving_time'] = 600

        activity = views.prep_activity_for_display(activity)

        self.assertEqual(activity['pace'], "10:00")

    def test_pace_formatted_properly_for_single_seconds(self):
        """Tests that 9:09/mi pace is formated with padded seconds"""
        activity = self.prep_minimal_activity()
        activity['distance'] = 1609
        activity['moving_time'] = 549

        activity = views.prep_activity_for_display(activity)

        self.assertEqual(activity['pace'], "9:09")

    def test_filter_only_runs(self):
        """Tests that we're only displaying runs (for now)"""
        activity = self.prep_minimal_activity()
        activity['type'] = 'Swim'

        self.assertFalse(views.should_display_activity(activity))
 
    def test_filter_has_map(self):
        """Tests that we filter out runs without a map (i.e. treadmill)"""
        activity = self.prep_minimal_activity()
        activity['type'] = 'Run'
        activity['polyline'] = ''

        self.assertFalse(views.should_display_activity(activity))
