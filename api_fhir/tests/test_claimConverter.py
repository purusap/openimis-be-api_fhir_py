import os
from unittest import mock

from api_fhir.converters.claimConverter import ClaimConverter
from api_fhir.models import FHIRBaseObject
from api_fhir.tests import ClaimTestMixin


class ClaimConverterTestCase(ClaimTestMixin):

    __TEST_CLAIM_JSON_PATH = "/test/test_claim.json"

    def set_up(self):
        super(ClaimConverterTestCase, self).set_up()
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self._test_claim_json_representation = open(dir_path + self.__TEST_CLAIM_JSON_PATH).read()

    def test_to_fhir_obj(self):
        imis_claim = self.create_test_imis_instance()
        fhir_claim = ClaimConverter.to_fhir_obj(imis_claim)
        self.verify_fhir_instance(fhir_claim)

    @mock.patch('location.models.HealthFacility.objects')
    @mock.patch('claim.models.ClaimAdmin.objects')
    @mock.patch('claim.models.ClaimDiagnosisCode.objects')
    @mock.patch('insuree.models.Insuree.objects')
    def test_to_imis_obj(self, mock_insuree, mock_cdc, mock_ca, mock_hf):
        self.set_up()
        mock_insuree.filter().first.return_value = self._TEST_INSUREE
        mock_cdc.get.return_value = self._TEST_DIAGNOSIS_CODE
        mock_ca.filter().first.return_value = self._TEST_CLAIM_ADMIN
        mock_hf.filter().first.return_value = self._TEST_HF

        fhir_claim = self.create_test_fhir_instance()
        imis_claim = ClaimConverter.to_imis_obj(fhir_claim, None)
        self.verify_imis_instance(imis_claim)

    def test_fhir_object_to_json_request(self):
        self.set_up()
        fhir_obj = self.create_test_fhir_instance()
        actual_representation = fhir_obj.dumps(format_='json')
        self.assertEqual(self._test_claim_json_representation, actual_representation)

    def test_create_object_from_json(self):
        self.set_up()
        fhir_claim = FHIRBaseObject.loads(self._test_claim_json_representation, 'json')
        self.verify_fhir_instance(fhir_claim)
