import sys

class BaseConfiguration(object):

    @classmethod
    def build_configuration(cls, cfg):
        raise NotImplementedError('`build_configuration()` must be implemented.')

    @classmethod
    def get_config(cls):
        module_name = "api_fhir"
        return sys.modules[module_name]


class IdentifierConfiguration(BaseConfiguration):

    @classmethod
    def build_configuration(cls, cfg):
        raise NotImplementedError('`build_configuration()` must be implemented.')

    @classmethod
    def get_fhir_identifier_type_system(cls):
        raise NotImplementedError('`get_fhir_identifier_type_system()` must be implemented.')

    @classmethod
    def get_fhir_id_type_code(cls):
        raise NotImplementedError('`get_fhir_id_type_code()` must be implemented.')

    @classmethod
    def get_fhir_chfid_type_code(cls):
        raise NotImplementedError('`get_fhir_chfid_type_code()` must be implemented.')

    @classmethod
    def get_fhir_passport_type_code(cls):
        raise NotImplementedError('`get_fhir_passport_type_code()` must be implemented.')

    @classmethod
    def get_fhir_facility_id_type(cls):
        raise NotImplementedError('`get_fhir_facility_id_type()` must be implemented.')


class LocationConfiguration(BaseConfiguration):

    @classmethod
    def build_configuration(cls, cfg):
        raise NotImplementedError('`build_configuration()` must be implemented.')

    @classmethod
    def get_fhir_location_role_type_system(cls):
        raise NotImplementedError('`get_fhir_location_role_type_system()` must be implemented.')

    @classmethod
    def get_fhir_code_for_hospital(cls):
        raise NotImplementedError('`get_fhir_code_for_hospital()` must be implemented.')

    @classmethod
    def get_fhir_code_for_dispensary(cls):
        raise NotImplementedError('`get_fhir_code_for_dispensary()` must be implemented.')

    @classmethod
    def get_fhir_code_for_health_center(cls):
        raise NotImplementedError('`get_fhir_code_for_health_center()` must be implemented.')


class MaritalConfiguration(BaseConfiguration):

    @classmethod
    def build_configuration(cls, cfg):
        raise NotImplementedError('`build_configuration()` must be implemented.')

    @classmethod
    def get_fhir_marital_status_system(cls):
        raise NotImplementedError('`get_fhir_marital_status_system()` must be implemented.')

    @classmethod
    def get_fhir_married_code(cls):
        raise NotImplementedError('`get_fhir_married_code()` must be implemented.')

    @classmethod
    def get_fhir_never_married_code(cls):
        raise NotImplementedError('`get_fhir_never_married_code()` must be implemented.')

    @classmethod
    def get_fhir_divorced_code(cls):
        raise NotImplementedError('`get_fhir_divorced_code()` must be implemented.')

    @classmethod
    def get_fhir_widowed_code(cls):
        raise NotImplementedError('`get_fhir_widowed_code()` must be implemented.')

    @classmethod
    def get_fhir_unknown_marital_status_code(cls):
        raise NotImplementedError('`get_fhir_unknown_marital_status_code()` must be implemented.')


class BaseApiFhirConfiguration(BaseConfiguration):

    @classmethod
    def build_configuration(cls, cfg):
        cls.get_identifier_configuration().build_configuration(cfg)
        cls.get_location_type_configuration().build_configuration(cfg)
        cls.get_marital_type_configuration().build_configuration(cfg)

    @classmethod
    def get_identifier_configuration(cls):
        raise NotImplementedError('`get_identifier_configuration()` must be implemented.')

    @classmethod
    def get_location_type_configuration(cls):
        raise NotImplementedError('`get_location_type_configuration()` must be implemented.')

    @classmethod
    def get_marital_type_configuration(cls):
        raise NotImplementedError('`get_marital_type_configuration()` must be implemented.')


from api_fhir.configurations.generalConfiguration import GeneralConfiguration
from api_fhir.configurations.stu3IdentifierConfig import Stu3IdentifierConfig
from api_fhir.configurations.stu3LocationConfig import Stu3LocationConfig
from api_fhir.configurations.stu3MaritalConfig import Stu3MaritalConfig
from api_fhir.configurations.stu3ApiFhirConfig import Stu3ApiFhirConfig
from api_fhir.configurations.moduleConfiguration import ModuleConfiguration
