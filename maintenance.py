"""
A Simple script to help with VCenter related operations
"""
import json
import requests
import time
from com.vmware.cis_client import Session
from vmware.vapi.lib import connect
from vmware.vapi.stdlib.client.factories import StubConfigurationFactory
from vmware.vapi.security.client.security_context_filter import LegacySecurityContextFilter
from vmware.vapi.security.user_password import create_user_password_security_context
from vmware.vapi.security.session import create_session_security_context
from com.vmware.appliance.update_client import Pending, Policy, Staged
from com.vmware.appliance_client import Update, LocalAccounts


def get_stub_factory_config(url, username, password):
    """
    Get stub factory config
    :param url:  dns/ip
    :param username: vcenter username
    :param password: vcenter password
    :return: stub factory config
    """
    session = requests.session()
    session.verify = False
    requests.packages.urllib3.disable_warnings()

    # set the api url
    api_url = f"https://{url}/api"
    security_context = create_user_password_security_context(username, password)
    connector = connect.get_requests_connector(session=session, url=api_url, provider_filter_chain=[
        LegacySecurityContextFilter(
            security_context=security_context)])
    session_service = Session(StubConfigurationFactory.new_std_configuration(connector))
    session_id = session_service.create()
    security_context = create_session_security_context(session_id)
    connector = connect.get_requests_connector(session=session, url=api_url, provider_filter_chain=[
        LegacySecurityContextFilter(
            security_context=security_context)])
    stub_config = StubConfigurationFactory.new_std_configuration(connector)
    return stub_config


class VCenterMaintenance:
    """
    Class to encapsulate daily vcenter operations. In development
    """

    def __init__(self, url, username, password):
        self.username = username
        self.password = password
        self.url = url
        stub_config = get_stub_factory_config(self.url, self.username, self.password)
        self.pending_client = Pending(stub_config)
        self.policy_client = Policy(stub_config)
        self.staged_client = Staged(stub_config)
        self.appliance_client = Update(stub_config)
        self.user_client = LocalAccounts(stub_config)
        self.user_data = {
            "vmdir.password": self.password
        }

    def get_updates(self):
        """
        Function to check if there are available updates. Note this is using default LOCAL and ONLINE source
        :return: list
        """
        source_type = self.pending_client.SourceType.LOCAL_AND_ONLINE
        versions = self.pending_client.list(source_type)
        return [json.dumps(version.__dict__, default=str) for version in versions]

    def get_version(self):
        """
        Function to check if there are available updates. Note this is using default LOCAL and ONLINE source
        :return: list
        """
        source_type = self.pending_client.SourceType.LOCAL_AND_ONLINE
        versions = self.pending_client.list(source_type)
        return [item.version for item in versions]

    def run_precheck(self, version):
        """
        This function runs precheck on the version to be updated
        :param version: patch version
        :return: status of precheck
        """
        return self.pending_client.precheck(version)

    def get_version_info(self, version):
        """
        Get detail info of the patch version
        :param version:
        :return: details of patch version
        """
        return self.pending_client.get(version)

    def validate(self, version):
        """
        Validate version before staging
        :param version: patch version
        :return: validation status
        """
        return self.pending_client.validate(version=version, user_data=self.user_data)

    def stage_update(self, version):
        """
        Stage selected version
        :param version: patch version
        """
        print(f"Staging {version} for update")
        self.pending_client.stage(version=version)
        stage_info = self.appliance_client.get()

        # check staging tasks
        while stage_info.task.status == "RUNNING":
            time.sleep(30)
            print("\nStaging Status:", stage_info.task.status)
            stage_info = self.appliance_client.get()
        if stage_info.task.status == "FAILED":
            print("Staging Step failed")
            return

    def list_users(self):
        """
        List vcenter local users
        :return: list: users
        """
        return self.user_client.list()

    def get_user(self, username):
        """
        Return details about a user
        :param username: user to return
        :return: user details
        """
        return self.user_client.get(username)

    def update_user(self, username):
        """
        Update a user property
        :param username:
        """
        user_config = self.user_client.UpdateConfig(password_expires=False)
        self.user_client.update(username, config=user_config)

    def install_update(self, version):
        """
        Install the staged version
        :param version: patch version
        """
        self.pending_client.install(version=version, user_data=self.user_data)

        # TODO check installation status
        # print("Installing the update")
        # install_status = self.appliance_client.get()
        # while install_status.task.status == "RUNNING":
        #     install_status = self.appliance_client.get()
