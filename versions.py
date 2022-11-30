#!/usr/bin/env python

from dotenv import load_dotenv
from os import getenv
from maintenance import VCenterMaintenance

# load env
load_dotenv()

vc_username = getenv("USERNAME")
vc_password = getenv("PASSWORD")
vc_url = getenv("VC_URL")


def main():
    # init the class
    vcenter = VCenterMaintenance(vc_url, vc_username, vc_password)
    # get available versions
    versions = vcenter.get_updates()
    print(versions)


if __name__ == "__main__":
    main()
