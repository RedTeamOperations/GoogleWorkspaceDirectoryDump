import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import optparse
import csv

SCOPES = ['https://www.googleapis.com/auth/directory.readonly', 'https://www.googleapis.com/auth/cloud-identity.groups.readonly']
import sys


def credentialgen(OauthCredentialsPath):
    CredentialsPath = OauthCredentialsPath
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CredentialsPath, SCOPES)
            creds = flow.run_local_server(port=8080)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds


def userdump(creds):
    file = open('usersdump.csv', 'w', newline='')
    writer = csv.writer(file)
    writer.writerow(["SN", "User Name", "Email Address"])
    SN = 1
    try:
        service = build('people', 'v1', credentials=creds)
        src = 'DIRECTORY_SOURCE_TYPE_DOMAIN_PROFILE'
        results = service.people().listDirectoryPeople(readMask='names,emailAddresses,organizations',sources=src,pageSize=100).execute()
        directory_people = results.get('people', [])
        next_page = results.get('nextPageToken')
        for data in directory_people:
            Name = data['names']
            EmailAddress = data['emailAddresses']
            #OrgName = data['organizations']
            for name in Name:
                sname = name['displayName']
            for email in EmailAddress:
                semail = email['value']
            writer.writerow([SN, sname, semail])
            SN = SN+ 1

        if next_page is not None:
            while next_page:
                results = service.people().listDirectoryPeople(readMask='names,emailAddresses,organizations',sources=src, pageSize=100).execute()
                directory_people = results.get('people', [])
                next_page = results.get('nextPageToken')
                for data in directory_people:
                    Name = data['names']
                    EmailAddress = data['emailAddresses']
                    # OrgName = data['organizations']
                    for name in Name:
                        sname = name['displayName']
                    for email in EmailAddress:
                        semail = email['value']
                    writer.writerow([SN, sname, semail])
                    SN = SN + 1
        else:
            pass

    except HttpError as err:
        print(err)


def groupdump(org_id,creds):
    file = open('groupsdump.csv', 'w', newline='')
    writer = csv.writer(file)
    writer.writerow(["SN", "Group Name", "Email Address", "Role"])
    SN = 1
    service = build('cloudidentity', 'v1', credentials=creds)
    param = 'customers/'+org_id
    try:
        response = service.groups().list(parent=param).execute()
        groups = response['groups']
        for group in groups:
            group_id = group['name']
            group_name = group['displayName']
            # List memberships
            response = service.groups().memberships().list(parent=group_id).execute()
            membership = response['memberships']
            for member in membership:
                email_ids = member['preferredMemberKey']
                roles = member['roles']
                for role in roles:
                    writer.writerow([SN, group_name, email_ids['id'],role['name']])
                    SN = SN + 1

    except Exception as e:
        print(e)


def main():
    cmd_options = {}
    parser = optparse.OptionParser(description='GCP Access Token Reuse', usage="Usage: %prog [options] GCPOrgID OauthCredentialFilePath", version="%prog 1.0")
    parser.add_option('-U', '--user', action="store_true", dest='user_dump', help="Users Information Dump")
    parser.add_option('-G', '--group', action="store_true", dest='group_dump', help="Groups Information Dump")
    parser.add_option('--org-id', action="store", dest='org_id', help="Organization ID")
    parser.add_option('--oauth-filepath', action="store", dest='oauth_filepath', help="OAuth Credential File Path")
    cmd_options = parser.parse_args()[0]

    if cmd_options.user_dump and cmd_options.group_dump:
        cred = credentialgen(cmd_options.oauth_filepath)
        userdump(cred)
        groupdump(cmd_options.org_id, cred)
    elif not cmd_options.user_dump and not cmd_options.group_dump:
        print("Choose At least One Option -U for Users Info Dump or -G for Groups Info Dump")
    elif cmd_options.group_dump:
        if cmd_options.org_id and cmd_options.oauth_filepath:
            cred = credentialgen(cmd_options.oauth_filepath)
            groupdump(cmd_options.org_id,cred)
        elif cmd_options.oauth_filepath and not cmd_options.org_id:
            print("Specify --org-id OrganizationID")
        else:
            print("Specify --oauth-filepath Oauth-FilePath")
            sys.exit()
    elif cmd_options.user_dump:
        if cmd_options.oauth_filepath:
            cred = credentialgen(cmd_options.oauth_filepath)
            userdump(cred)
        else:
            print("Specify --oauth-filepath Oauth-FilePath")
            sys.exit()
    else:
        pass


if __name__ == '__main__':
    main()
