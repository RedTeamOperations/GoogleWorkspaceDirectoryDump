# Google Workspace Directory Dump Tool

Script written in Python3 which dumps the user/group from the Google Workspace. This tool can be used to map the group member relationship which can aid further cyber operations.

![This is an image](gw.jpg)


# Install Dependencies: 

pip3 install google.auth google-auth-oauthlib

pip3 install --upgrade google-api-python-client


# Usage : 

Usage: Python3 WorkspaceDirectoryDump.py [options] GCPOrgID OauthCredentialFilePath

Example : Python3 WorkspaceDirectoryDump.py -U --oauth-filepath client_secret_xyz-8abcd.apps.googleusercontent.com.json

GCP Access Token Reuse

Options:
  --version             show program's version number and exit

  -h, --help            show this help message and exit

  -U, --user            Users Information Dump

  -G, --group           Groups Information Dump

  --org-id=ORG_ID       Organization ID

  --oauth-filepath=OAUTH_FILEPATH  OAuth Credential File Path

  
# Little Tweaks
  
  Organization ID is required only if "Group" data needs to be dumped
  
  
