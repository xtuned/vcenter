#!/usr/bin/env python
import json
from dotenv import load_dotenv
from os import getenv
from maintenance import VCenterMaintenance, console

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
    versions = [version.__dict__ for version in versions]
    if len(versions) > 0:
        console.print("Found updates ...", style="green")
        console.print_json(data=versions, indent=4, default=str)
    else:
        console.print("There are no updates at this time. Check again soon")


if __name__ == "__main__":
    main()
