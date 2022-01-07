## Description

This command line Python program uses the [GitHub Rest API](https://docs.github.com/en/rest) 
and the [Freshdesk API](https://developers.freshdesk.com/api/) to retrieve the data of a GitHub User
and create a new Freshdesk Contact (if such contact doesn't exist), or update an existing contact.

Currently the program doesn't distinguish between GitHub users that are persons and organizations. 
Fetching a user with the GitHub API can return a person or an organization, and a Freshdesk contact is created anyway.

The following GitHub User fields are being transferred to the Freshdesk Contact upon creation:

> id -> unique_external_id  
bio, blog, html_url -> description  
email -> email  
location -> address  
name/login -> name  
twitter_username -> twitter_id  

**Note:** `name` is a mandatory field in a Freshdesk contact, hence if it is null in GitHub, we use `login`.  
For the `description` contact field, we try to combine the GitHub user bio, their blog, and their Github profile's URL.

***
## Install and run the application

Download the `freshdesk_contact` package as a zip file and unzip it.  
Alternatively, use `git clone git@github.com:natla/freshdesk-contact.git`.

### Requirements

- The program needs Python version >= **V3.6** to run successfully.  

    If necessary, create a fresh Python 3 virtual environment and activate it. For example:  

        python3 -m venv <venv_name> 
        source <venv_name>/bin/activate

- For authentication purposes, you need a GitHub personal access token and a Freshdesk API key.  

    If you don't have a GitHub personal access token, refer to the [Creating a personal access token guide](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token).  
    For a guide how to create a Freshdesk API key, refer to the [Authentication article](https://developers.freshdesk.com/api/#getting-started).

   Once you have these tokens, define them as environment variables in a `.env` file 
   that should be placed in the main `freshdesk-contact` directory. Example file content:
   
        GITHUB_TOKEN=ghp_9L0IX0NdXXXXXXXXXXXXXXXXXXXXX
        FRESHDESK_TOKEN=BPzlZTHXXXXXXXXXX
        

- Navigate to the `freshdesk-contact` directory. From inside that directory, install the required third-party dependencies from `requirements.txt`:  

        python -m pip install -r requirements.txt

### How to run the application

 
**Important:** You must provide two command-line arguments when executing the program:
 - The GitHub login (username) of the user that you want to create a Freshdesk contact for,
 - your Freshdesk subdomain.

Navigate to the `freshdesk-contact` directory. 

From inside that directory, execute the application from the command line following this specific format:

    python -m freshdesk_contact <github_username> <freshdesk_subdomain>

For example:

    python -m freshdesk_contact 'natla' 'newaccount12345'


**Note:** Any errors, as well as debug messages, will be logged in `freshdesk-contact/contact.log`. Please refer to that file if anything seems to go wrong.

### How to run the unit tests

    python -m tests

***
## Application improvements wishlist

- Make it possible to upload an avatar image to Freshdesk, using the GitHub avatar URL.

- Distinguish between contacts of persons and organizations. Probably use two concrete factories that register an abstract interface.

- If a GitHub user belongs to a company (organization), create a contact of that company and link it to the user through the `company_id` field.

- Add a Scheduler (cron job) to the application that updates a contact's information
at a certain time interval.

- Figure out how to integrate the deletion of a contact into the main flow of the program.

- Add more unit tests (for example, the deletion of a contact is not currently being tested).
