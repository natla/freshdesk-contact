import logging.config
import pathlib

import requests
import yaml

from json import JSONDecodeError

from freshdesk_contact.constants import (
    FRESHDESK_CONTACTS_ENDPOINT,
    FRESHDESK_TOKEN,
    GITHUB_TOKEN,
    GITHUB_USER_ENDPOINT
)

PARENT_DIR = pathlib.Path(__file__).parent.parent
with open(PARENT_DIR / 'logging_config.yaml', 'rt') as file:
    config_data = yaml.safe_load(file.read())
    logging.config.dictConfig(config_data)

logger = logging.getLogger(__name__)


class Contact:

    def __init__(self, username: str, subdomain: str):
        self.username = username
        self.subdomain = FRESHDESK_CONTACTS_ENDPOINT.format(subdomain)
        self.freshdesk_auth = (FRESHDESK_TOKEN, '')
        self.github_auth = (GITHUB_TOKEN, '')

    def create_update_contact(self) -> None:
        """Create or update a contact in Freshdesk based on GitHub username.

        Retrieve the information of a GitHub User with self.username.
        If such a user doesn't exist in Freshdesk, create new contact.
        Otherwise, update the existing contact's information.
        """
        user_info = self.get_github_user_data(self.username)
        if not user_info:
            return

        # Check if contact already exists in Freshdesk.
        contact_id = self.find_freshdesk_contact(str(user_info.get('id')))

        if contact_id:
            self.update_freshdesk_contact(contact_id, user_info)
        else:
            self.create_freshdesk_contact(user_info)

    def create_freshdesk_contact(self, user_data: dict) -> None:
        """Create a new Freshdesk contact."""
        contact_info = self.github_user_to_freshdesk_contact(user_data)

        response = requests.post(
            self.subdomain,
            json=contact_info,
            auth=self.freshdesk_auth)

        if response.status_code == requests.codes.created:
            logger.debug('Freshdesk contact with id %s successfully created.', response.json().get('id'))
        else:
            self.log_response_errors(response, 'Freshdesk contact could not be successfully created')

    def update_freshdesk_contact(self, contact_id: str, user_data: dict) -> None:
        """Update an existing Freshdesk contact."""
        contact_info = self.github_user_to_freshdesk_contact(user_data)

        response = requests.put(
            f'{self.subdomain}{contact_id}',
            json=contact_info,
            auth=self.freshdesk_auth)

        if response.status_code == requests.codes.ok:
            logger.debug('Freshdesk contact with id %s successfully updated.', contact_id)
        else:
            self.log_response_errors(response, 'Freshdesk contact could not be successfully updated')

    def delete_freshdesk_contact(self) -> None:
        """Delete an existing Freshdesk contact.

        Note: This is a permanent delete of the contact, which means
        that the same contact can be later recreated without conflicts.
        """
        user_info = self.get_github_user_data(self.username)

        # Find contact id in Freshdesk.
        contact_id = user_info and self.find_freshdesk_contact(str(user_info.get('id')))
        if not contact_id:
            logger.debug('Contact of GitHub user %s does not exist in Freshdesk.', self.username)
            return

        response = requests.delete(
            f'{self.subdomain}{contact_id}/hard_delete?force=true',
            auth=self.freshdesk_auth)

        if response.status_code == requests.codes.no_content:
            logger.debug('Freshdesk contact %s successfully deleted.', contact_id)
        else:
            self.log_response_errors(response, f'Freshdesk contact {contact_id} could not be successfully deleted.')

    def find_freshdesk_contact(self, github_id: str) -> str:
        """Find a Freshdesk contact through their Github user id and return that contact's id."""
        response = requests.get(
            f'{self.subdomain}?unique_external_id={github_id}',
            auth=self.freshdesk_auth)

        if response.status_code != requests.codes.ok:
            self.log_response_errors(response, 'Freshdesk contact could not be successfully fetched')
            return ''

        return response.json()[0].get('id') if response.json() else ''

    def get_github_user_data(self, username) -> dict:
        """Fetch user with login self.username from the GitHub API and return that user's data"""

        response = requests.get(
            f'{GITHUB_USER_ENDPOINT}{username}',
            auth=self.github_auth)

        if response.status_code == requests.codes.not_found:
            self.log_response_errors(response, 'GitHub user not found')
            return {}

        return response.json()

    @staticmethod
    def github_user_to_freshdesk_contact(user_data: dict) -> dict:
        """Get Github user data and convert it to Freshdesk contact data.

        In order to create a Freshdesk contact, one of these attributes
        is mandatory: unique_external_id, email, phone, mobile or twitter_id.
        GitHub user data does not include phone and mobile, and might not include email or twitter_id.
        The user id always exists and is unique, so we provide it as a unique_external_id.
        Alternatively, we could provide the GitHub "node_id".

        Name is a mandatory field for a Freshdesk contact. If it is null
        in GitHub, we use "login" instead.
        """
        bio = f'Bio: {user_data.get("bio")}, ' if user_data.get('bio') else ''
        blog = f'Blog: {user_data.get("blog")}, ' if user_data.get('blog') else ''
        github_profile = f'Github profile: {user_data.get("html_url")}' if user_data.get('html_url') else ''

        return {
            'address': user_data.get('location'),
            'unique_external_id': str(user_data.get('id')),
            'description': f'{bio}{blog}{github_profile}',
            'email': user_data.get('email'),
            'name': user_data.get('name') or user_data.get('login'),
            'twitter_id': user_data.get('twitter_username')
        }

    @staticmethod
    def log_response_errors(response: requests.models.Response, message: str) -> None:
        """In case of a failed request, log a custom error message and the response errors, if any."""
        try:
            errors = response.json().get('errors') or response.json().get('message')
        except JSONDecodeError:
            errors = None

        logger.error(
            '%s: Status code %s %s, Errors %s',
            message,
            response.status_code,
            response.reason,
            errors)
