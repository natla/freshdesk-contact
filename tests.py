import json
import unittest

import responses

from freshdesk_contact.contact import Contact


class TestContact(unittest.TestCase):
    """Test module for the Contact class."""

    def setUp(self):
        """Set up test with mocked requests and faux users."""

        self.test_subdomain = 'test_subdomain'

        self.valid_github_user = {
            'id':  '123456789',
            'bio': None,
            'blog': 'https://batman.waynecorp.com',
            'email': 'batman@batcave.com',
            'html_url': 'https://github.com/batman',
            'location': 'Gotham city, New Jersey',
            'login': 'batman',
            'name': None,
            'twitter_username': '@batman'
        }
        self.contact_created_id = '123456'
        self.contact_created_json = {
            'id': self.contact_created_id,
            'address': 'Gotham city, New Jersey',
            'unique_external_id': '123456789',
            'description': 'Blog: https://batman.waynecorp.com, Github profile: https://github.com/batman',
            'email': 'batman@batcave.com',
            'name': 'batman',
            'twitter_id': '@batman'}
        self.contact_created = Contact(self.valid_github_user.get('login'), self.test_subdomain)

        self.invalid_github_user = {
            'id': None,
            'login': 'ckdnvldkbpwap'
        }
        self.invalid_contact = Contact(self.invalid_github_user.get('login'), self.test_subdomain)

        self.another_valid_github_user = {
            'id':  '123456798',
            'bio': None,
            'blog': None,
            'email': 'robin@batcave.com',
            'html_url': 'https://github.com/robin',
            'location': 'Gotham city, New Jersey',
            'login': 'robin',
            'name': 'Robin',
            'twitter_username': '@robin'
        }
        self.contact_not_created_id = '123467'
        self.contact_not_created_json = {
            'id': self.contact_not_created_id,
            'address': 'Gotham city, New Jersey',
            'unique_external_id': '123456798',
            'description': 'Github profile: https://github.com/robin',
            'email': 'robin@batcave.com',
            'name': 'Robin',
            'twitter_id': '@robin'}
        self.contact_not_created = Contact(self.another_valid_github_user.get('login'), self.test_subdomain)

        # Mock GET requests
        responses.add(
            responses.GET,
            f'https://api.github.com/users/{self.valid_github_user.get("login")}',
            json=self.valid_github_user,
            status=200)
        responses.add(
            responses.GET,
            f'https://api.github.com/users/{self.another_valid_github_user.get("login")}',
            json=self.another_valid_github_user,
            status=200)
        responses.add(
            responses.GET,
            f'https://api.github.com/users/{self.invalid_github_user.get("login")}',
            json={'error': 'not found'},
            status=404)

        responses.add(
            responses.GET,
            f'https://{self.test_subdomain}.freshdesk.com/api/v2/contacts/?unique_external_id={self.valid_github_user.get("id")}',
            json=[self.contact_created_json],
            status=200)
        responses.add(
            responses.GET,
            f'https://{self.test_subdomain}.freshdesk.com/api/v2/contacts/?unique_external_id={self.another_valid_github_user.get("id")}',
            json={'error': 'not found'},
            status=404)
        responses.add(
            responses.GET,
            f'https://{self.test_subdomain}.freshdesk.com/api/v2/contacts/?unique_external_id={self.invalid_github_user.get("id")}',
            json={'error': 'not found'},
            status=404)

        # Add callback to POST and PUT requests
        responses.add_callback(
            responses.POST,
            f'https://{self.test_subdomain}.freshdesk.com/api/v2/contacts/',
            callback=self.request_callback_post,
            content_type='application/json')
        responses.add_callback(
            responses.PUT,
            f'https://{self.test_subdomain}.freshdesk.com/api/v2/contacts/{self.contact_created_json.get("id")}',
            callback=self.request_callback_put,
            content_type='application/json')

    def request_callback(self, request, status):
        """Add simulated Freshdesk contact id to payload."""
        payload = json.loads(request.body)
        payload['id'] = self.contact_created_id if payload.get('name') == 'batman' else self.contact_not_created_id
        return status, {}, json.dumps(payload)

    def request_callback_post(self, request):
        """Callback for POST requests."""
        return self.request_callback(request, 201)

    def request_callback_put(self, request):
        """Callback for PUT requests."""
        return self.request_callback(request, 200)

    @responses.activate
    def test_update_contact_valid_user(self):
        """Test the update of an existing Freshdesk contact."""
        self.contact_created.create_update_contact()

        # get_github_user_data(), find_freshdesk_contact() and update_freshdesk_contact() are called
        assert len(responses.calls) == 3

        # get_github_user_data()
        assert responses.calls[0].response.url == f'https://api.github.com/users/{self.valid_github_user.get("login")}'
        assert responses.calls[0].response.status_code == 200
        assert responses.calls[0].response.json() == self.valid_github_user

        # find_freshdesk_contact()
        assert responses.calls[1].response.url == (
            f'https://test_subdomain.freshdesk.com/api/v2/contacts/?unique_external_id={self.valid_github_user.get("id")}')
        assert responses.calls[1].response.status_code == 200
        assert responses.calls[1].response.json()[0] == self.contact_created_json

        # update_freshdesk_contact() is called because the contact already exists
        assert responses.calls[2].response.url == (
            f'https://test_subdomain.freshdesk.com/api/v2/contacts/{self.contact_created_id}')
        assert responses.calls[2].response.status_code == 200
        assert responses.calls[2].response.reason == 'OK'
        assert responses.calls[2].response.json() == self.contact_created_json

    @responses.activate
    def test_create_contact_valid_user(self):
        """Test the creation of a new Freshdesk contact."""
        self.contact_not_created.create_update_contact()

        assert len(responses.calls) == 3

        # get_github_user_data()
        assert responses.calls[0].response.url == (
            f'https://api.github.com/users/{self.another_valid_github_user.get("login")}')
        assert responses.calls[0].response.status_code == 200
        assert responses.calls[0].response.json() == self.another_valid_github_user

        # find_freshdesk_contact()
        assert responses.calls[1].response.url == (
            f'https://test_subdomain.freshdesk.com/api/v2/contacts/?unique_external_id={self.another_valid_github_user.get("id")}')
        assert responses.calls[1].response.status_code == 404
        assert responses.calls[1].response.reason == 'Not Found'

        # create_freshdesk_contact() is called, since the user iss not a Freshdesk contact yet.
        assert responses.calls[2].response.url == 'https://test_subdomain.freshdesk.com/api/v2/contacts/'
        assert responses.calls[2].response.status_code == 201
        assert responses.calls[2].response.reason == 'Created'
        assert responses.calls[2].response.json() == self.contact_not_created_json

    @responses.activate
    def test_create_update_contact_invalid_user(self):
        """Test non-existing Github user."""
        self.invalid_contact.create_update_contact()

        # Only get_github_user_data() is called
        assert len(responses.calls) == 1

        assert responses.calls[0].response.url == (
            f'https://api.github.com/users/{self.invalid_github_user.get("login")}')
        assert responses.calls[0].response.status_code == 404
        assert responses.calls[0].response.reason == 'Not Found'


if __name__ == '__main__':
    unittest.main()
