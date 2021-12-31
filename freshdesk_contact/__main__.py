#!/usr/bin/env python

import sys

from freshdesk_contact.contact import Contact, logger


def main(username: str, subdomain: str) -> None:
    contact = Contact(username, subdomain)
    contact.create_update_contact()


if __name__ == '__main__':
    if len(sys.argv) < 3:
        sys.exit(logger.error(
            'Missing command-line argument(s). '
            'Make sure that input is in format: python -m freshdesk_contact <github_username> <freshdesk_subdomain>'))
    sys.exit(main(sys.argv[1], sys.argv[2]))
