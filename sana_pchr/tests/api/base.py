from django.test import TestCase, Client
from django.http.response import HttpResponse
from freezegun import freeze_time
import os
import json
import subprocess


# This is my quick hack job of the Ruby approvals gem
# It makes API testing a snap


class VerifiableResponse(HttpResponse):
    _blacklisted_keys = {
        "uuid": "<UUID>",
        "token": "<token>"
    }

    def create(plainResponse, testCase):
        plainResponse.__class__ = VerifiableResponse  # Wheeee
        plainResponse.testCase = testCase
        return plainResponse

    def sanitize(data):
        if hasattr(data, "keys"):
            for key, replacement in VerifiableResponse._blacklisted_keys.items():
                if key in data.keys():
                    data[key] = replacement

        if hasattr(data, "items"):
            for k, subitem in data.items():
                VerifiableResponse.sanitize(subitem)

        if isinstance(data, list):
            for subitem in data:
                VerifiableResponse.sanitize(subitem)

        return data

    def verify(self, status_code, postfix=None, raw=False):
        self.testCase.assertEqual(status_code, self.status_code,
                                  "Expected status code %d not received (response: %s)" % (status_code, self.content))

        approvals_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "approvals")
        approvals_file_root = os.path.join(approvals_dir, self.testCase.id().replace("%s." % __package__, ""))
        if postfix:
            approvals_file_root = "%s_%s" % (approvals_file_root, postfix)
        filetype = "json"
        if raw:
            filetype = "raw"
        approvals_reference_file = approvals_file_root + ".approved.%s" % filetype
        approvals_received_file = approvals_file_root + ".received.%s" % filetype

        if not os.path.exists(approvals_dir):
            os.mkdir(approvals_dir)

        received = self.content

        if not raw:
            received = received.decode("utf-8")

            try:
                received = json.loads(received)
                received = VerifiableResponse.sanitize(received)
            except ValueError:
                pass  # The return isn't JSON - we tried

        fail = False
        missing = False
        if not os.path.exists(approvals_reference_file):
            missing = True
        else:
            reference = open(approvals_reference_file, "rb").read()
            if not raw:
                reference = json.loads(reference.decode("utf-8"))

            if reference != received:
                fail = True

        if fail or missing:
            if not raw:
                received = json.dumps(received, sort_keys=True, indent=2)
            open(approvals_received_file, "wb").write(
                    received.encode("utf-8") if hasattr(received, "encode") else received)
        if fail:
            diff_proc = subprocess.Popen(["diff", approvals_reference_file, approvals_received_file],
                                         stdout=subprocess.PIPE)
            diff_result, err = diff_proc.communicate()
            raise AssertionError(
                    "Approvals file %s mismatch\n%s" % (approvals_reference_file, diff_result.decode("utf-8")))
        if missing:
            raise AssertionError("Approvals file %s missing." % (approvals_reference_file))
        if not fail and not missing:
            if os.path.exists(approvals_received_file):
                os.remove(approvals_received_file)


class ApprovalsClient(Client):
    def request(self, *args, **kwargs):
        return VerifiableResponse.create(super(ApprovalsClient, self).request(*args, **kwargs), self.testCase)


# The built in django client has an annoying lack of magic - or, at least, it's well hidden
class JSONClient(ApprovalsClient):
    def prepare_data(self, data):
        try:
            return "application/json", json.dumps(data)
        except:
            return "application/octet-stream", data

    def post(self, *args, **kwargs):
        probable_mime_type = "application/json"
        args = list(args)
        if len(args) >= 2:
            probable_mime_type, args[1] = self.prepare_data(args[1])
        elif "data" in kwargs:
            probable_mime_type, kwargs["data"] = self.prepare_data(kwargs["data"])
        if probable_mime_type and "content_type" not in kwargs:
            kwargs["content_type"] = probable_mime_type
        return super(JSONClient, self).post(*args, **kwargs)


class BaseTestCase(TestCase):
    def setUp(self):
        super(BaseTestCase, self).setUp()
        self._frozen_time = freeze_time("Jan 2 2003 12:34:56.7890")
        self._frozen_time.start()

    def tearDown(self):
        self._frozen_time.stop()

    def _pre_setup(self):
        super(BaseTestCase, self)._pre_setup()
        self.client = JSONClient()
        self.client.testCase = self


def disable_transport_encryption(fcn):
    def wrapped(*args, **kwargs):
        from sana_pchr import settings_base
        settings_base.TRANSPORT_ENCRYPTION = False
        try:
            return fcn(*args, **kwargs)
        finally:
            settings_base.TRANSPORT_ENCRYPTION = True

    return wrapped
