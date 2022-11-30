#!/usr/bin/env python

from dotenv import load_dotenv
from os import getenv
from maintenance import VCenterMaintenance

# load env
load_dotenv()

# grab connection details
vc_username = getenv("USERNAME")
vc_password = getenv("PASSWORD")
vc_url = getenv("VC_URL")


def main():
    # initials the class
    vcenter = VCenterMaintenance(vc_url, vc_username, vc_password)
    # set root user password not to expire
    vcenter.update_user("root")


if __name__ == "__main__":
    main()
