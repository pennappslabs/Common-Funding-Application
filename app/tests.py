import json

from django.test import TestCase
from unittest import skip
from django.core import mail

from django.contrib.auth.models import User
from .models import CFAUser, Event, Grant
from templatetags import helpers


def create_funder():
    funder = User.objects.create_user(username='spec',
                                      email='spec@upenn.edu',
                                      password='we<3money$$$')
    cfau = funder.get_profile()
    cfau.user_type = 'F'
    cfau.save()
    return funder


class CFAUserTest(TestCase):
    fixtures = ['cfausers.json']

    def test_is_funder(self):
        cuser = CFAUser.objects.get(pk=1)
        self.assertTrue(cuser.is_funder)

    def test_is_requester(self):
        cuser = CFAUser.objects.get(pk=11)
        self.assertTrue(cuser.is_requester)


class TestViews(TestCase):
    def test_index(self):
        """Test to see that index redirects to login page

        TODO: In the future, index page should be the login page
        """
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 302)

    def test_login_page(self):
        resp = self.client.get('/accounts/login/')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('form' in resp.context)
        self.assertContains(resp, 'Login')


class TestLoginViews(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='philo',
                                             email='philo@upenn.edu',
                                             password='we<3literature')

    def test_index(self):
        self.client.login(username='philo', password='we<3literature')
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Current Applications')

    def test_index_not_logged_in(self):
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 302)

    def test_logout(self):
        self.client.login(username='philo', password='we<3literature')
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 200)
        self.client.logout()
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 302)


class TestEvents(TestCase):
    fixtures = ['events.json']

    def setUp(self):
        self.user = User.objects.create_user(username='philo',
                                             email='philo@upenn.edu',
                                             password='we<3literature')
        self.client.login(username='philo', password='we<3literature')

    def test_index(self):
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Current Applications')
        self.assertContains(resp, 'Penn Labs Team')
        self.assertContains(resp, 'SUBMITTED')

    def test_index_remove_event(self):
        Event.objects.get(pk=1).delete()
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Current Applications')
        self.assertContains(resp, "You do not have any current applications.")
        resp = self.client.get('/1/')
        self.assertEqual(resp.status_code, 404)

    def test_edit_event(self):
        resp = self.client.get('/1/edit/')
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Houston Hall')

    def test_edit_event_location(self):
        with open('app/fixtures/event_edit.json', 'r') as f:
            resp = self.client.post('/1/edit/', json.load(f))
        self.assertEqual(resp.status_code, 302)
        resp = self.client.get('/1/edit/')
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'First Round')

    def test_event_is_old(self):
        # Push event into the past, currently 2050-01-01
        event = Event.objects.get(pk=1)
        event.date = '2000-01-01'
        event.save()
        # Ensure event isn't on the current applications page
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Current Applications')
        self.assertContains(resp, "You do not have any current applications.")
        # Ensure event still exists
        resp = self.client.get('/1/')
        self.assertEqual(resp.status_code, 200)
        # Ensure event is on the old applications page
        resp = self.client.get('/old/')
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Past Applications')
        self.assertContains(resp, 'Test Event')


class TestFunder(TestCase):
    fixtures = ['events.json']

    def setUp(self):
        self.user = User.objects.create_user(username='philo',
                                             email='philo@upenn.edu',
                                             password='we<3literature')
        self.funder = create_funder()
        self.client.login(username='spec', password='we<3money$$$')
        self.event = Event.objects.get(pk=1)

    def test_funder_is_funder(self):
        self.assertTrue(self.funder.get_profile().is_funder)
        self.assertTrue(self.user.get_profile().is_requester)

    @skip("Currently all funders have access to all applications")
    def test_event_no_funder_no_access(self):
        resp = self.client.get('/1/')
        self.assertEqual(resp.status_code, 302)

    def test_event_has_funder_has_access(self):
        self.event.applied_funders.add(self.funder.get_profile())
        resp = self.client.get('/1/')
        self.assertEqual(resp.status_code, 200)


class TestShare(TestCase):
    fixtures = ['events.json']
    key = "a96055ddf995cce98469884fa202d3c40032e039"

    def setUp(self):
        self.user = User.objects.create_user(username='philo',
                                             email='philo@upenn.edu',
                                             password='we<3literature')
        self.event = Event.objects.get(pk=1)

    def test_event_secret_key(self):
        self.assertEqual(self.event.secret_key, TestShare.key)

    def test_event_share_link_no_access(self):
        resp = self.client.get('/1/')
        self.assertEqual(resp.status_code, 302)

    def test_event_access_with_login(self):
        self.client.login(username='philo', password='we<3literature')
        resp = self.client.get('/1/')
        self.assertEqual(resp.status_code, 200)

    def test_event_access_with_key(self):
        resp = self.client.get('/1/?key=' + TestShare.key)
        self.assertEqual(resp.status_code, 200)


class TestEmail(TestCase):
    fixtures = ['events.json']

    def setUp(self):
        self.user = User.objects.create_user(username='philo',
                                             email='philo@upenn.edu',
                                             password='we<3literature')

    def test_notify_requester(self):
        event = Event.objects.get(pk=1)
        event.notify_requester_for_followups()
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject,
                         'Followup Questions for Test Event')


class TestEmailFunders(TestCase):
    fixtures = ['events.json']

    def setUp(self):
        self.user = User.objects.create_user(username='philo',
                                             email='philo@upenn.edu',
                                             password='we<3literature')
        self.funder = create_funder()
        self.event = Event.objects.get(pk=1)
        self.event.applied_funders.add(self.funder.get_profile())

    def test_notify_funders(self):
        self.event.notify_funders()
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject,
                         '[Test Event] Event Application Changed')


class TestItemGrant(TestCase):
    fixtures = ['events.json']

    @staticmethod
    def create_item(event):
        return event.item_set.create(name="Free Software",
                                     quantity=10,
                                     price_per_unit=100,
                                     funding_already_received=0,
                                     category="Honoraria/Services",
                                     revenue=0)

    def setUp(self):
        self.funder = create_funder()
        self.event = Event.objects.get(pk=1)

    def test_total_amounts_not_funded(self):
        TestItemGrant.create_item(self.event)
        self.assertEqual(self.event.amounts, {})
        self.assertEqual(self.event.total_funds_granted, 0)

    def test_create_grant(self):
        item = TestItemGrant.create_item(self.event)
        grant = Grant.objects.create(funder=self.funder.get_profile(),
                                     item=item,
                                     amount=50)
        grant.save()
        item.grant_set.add(grant)
        item.save()
        self.assertEqual(self.event.total_funds_granted, 50)


class TestHelpers(TestCase):
    fixtures = ['events.json']

    def setUp(self):
        self.funder = create_funder()
        self.event = Event.objects.get(pk=1)
        self.item = TestItemGrant.create_item(self.event)
        grant = Grant.objects.create(funder=self.funder.get_profile(),
                                     item=self.item,
                                     amount=50)
        grant.save()
        self.item.grant_set.add(grant)
        self.item.save()

    def test_funders_grant_data_to_item_no_grant(self):
        self.item.grant_set.all().delete()
        self.item.save()
        item_tuple = helpers.funders_grant_data_to_item(
            None, self.item, self.funder.id)
        self.assertEqual((None, self.item.id), item_tuple)

    def test_funders_grant_data_to_item(self):
        item_tuple = helpers.funders_grant_data_to_item(
            None, self.item, self.funder.id)
        self.assertEqual((50, self.item.id), item_tuple)

    def test_funder_item_data(self):
        result = helpers.funder_item_data(None, self.item, [self.funder])
        # funder data - funder id, amount = 50, grant id = 1
        expected = (self.item, [(self.funder.id, 50, 1)])
        self.assertEqual(expected, result)

    def test_get_or_none_exists(self):
        self.assertEqual(self.event, helpers.get_or_none(Event, pk=1))

    def test_get_or_none_does_not_exist(self):
        self.assertEqual(None, helpers.get_or_none(Event, pk=2))