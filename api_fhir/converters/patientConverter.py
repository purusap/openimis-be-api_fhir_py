from insuree.models import Insuree, Gender

from api_fhir.configurations import Stu3IdentifierConfig, GeneralConfiguration, Stu3MaritalConfig
from api_fhir.converters import BaseFHIRConverter
from api_fhir.models import Patient, HumanName, NameUse, AdministrativeGender, ContactPointSystem, ContactPointUse, \
    ImisMaritalStatus

from api_fhir.models.address import AddressUse, AddressType
from api_fhir.utils import TimeUtils


class PatientConverter(BaseFHIRConverter):
    @classmethod
    def to_fhir_obj(cls, imis_insuree):
        fhir_patient = Patient()
        cls.build_human_names(fhir_patient, imis_insuree)
        cls.build_fhir_identifiers(fhir_patient, imis_insuree)
        cls.build_fhir_birth_date(fhir_patient, imis_insuree)
        cls.build_fhir_gender(fhir_patient, imis_insuree)
        cls.build_fhir_marital_status(fhir_patient, imis_insuree)
        cls.build_fhir_telecom(fhir_patient, imis_insuree)
        cls.build_fhir_addresses(fhir_patient, imis_insuree)
        return fhir_patient

    @classmethod
    def to_imis_obj(cls, fhir_patient, audit_user_id):
        errors = []
        imis_insuree = cls.createDefaultInsuree(audit_user_id)
        # TODO the familyid isn't covered because that value is missing in the model
        # TODO the photoId isn't covered because that value is missing in the model
        # TODO the typeofid isn't covered because that value is missing in the model
        cls.build_imis_names(imis_insuree, fhir_patient, errors)
        cls.build_imis_identifiers(imis_insuree, fhir_patient)
        cls.build_imis_birth_date(imis_insuree, fhir_patient, errors)
        cls.build_imis_gender(imis_insuree, fhir_patient)
        cls.build_imis_marital(imis_insuree, fhir_patient)
        cls.build_imis_contacts(imis_insuree, fhir_patient)
        cls.build_imis_addresses(imis_insuree, fhir_patient)
        cls.check_errors(errors)
        return imis_insuree

    @classmethod
    def createDefaultInsuree(cls, audit_user_id):
        imis_insuree = Insuree()
        imis_insuree.head = GeneralConfiguration.get_default_value_of_patient_head_attribute()
        imis_insuree.card_issued = GeneralConfiguration.get_default_value_of_patient_card_issued_attribute()
        imis_insuree.validity_from = TimeUtils.now()
        imis_insuree.audit_user_id = audit_user_id
        return imis_insuree

    @classmethod
    def build_human_names(cls, fhirPatient, imisInsuree):
        # last name
        name = HumanName()
        name.use = NameUse.USUAL.value
        name.family = imisInsuree.last_name
        name.given = [imisInsuree.other_names]
        fhirPatient.name = [name.__dict__]

    @classmethod
    def build_imis_names(cls, imis_insuree, fhir_patient, errors):
        if not cls.valid_condition(fhir_patient.get('name') is None, 'Missing patient `name` attribute', errors):
            for name in fhir_patient.get('name'):
                if name['use'] == NameUse.USUAL.value:
                    imis_insuree.last_name = name['family']
                    if name.get('given') is not None and len(name.get('given')) > 0:
                        imis_insuree.other_names = name['given'][0]
                    break
            cls.valid_condition(imis_insuree.last_name is None, 'Missing patient family name', errors)
            cls.valid_condition(imis_insuree.other_names is None, 'Missing patient given name', errors)

    @classmethod
    def build_fhir_identifiers(cls, fhir_patient, imis_insuree):
        identifiers = []
        cls.build_fhir_id_identifier(identifiers, imis_insuree)
        cls.build_fhir_chfid_identifier(identifiers, imis_insuree)
        cls.build_fhir_passport_identifier(identifiers, imis_insuree)
        fhir_patient.identifier = identifiers

    @classmethod
    def build_imis_identifiers(cls, imis_insuree, fhir_patient):
        if fhir_patient.get('identifier') is not None:
            for identifier in fhir_patient.get('identifier'):
                identifier_type = identifier.get("type")
                if identifier_type:
                    coding_list = identifier_type.get('coding')
                    if coding_list:
                        first_code = cls.get_first_coding_from_codeable_concept(identifier_type)
                        if first_code.get("system") == Stu3IdentifierConfig.get_fhir_identifier_type_system():
                            code = first_code.get("code")
                            value = identifier.get("value")
                            if value and code == Stu3IdentifierConfig.get_fhir_chfid_type_code():
                                imis_insuree.chf_id = value
                            if value and code == Stu3IdentifierConfig.get_fhir_passport_type_code():
                                imis_insuree.passport = value

    @classmethod
    def build_fhir_chfid_identifier(cls, identifiers, imis_insuree):
        if imis_insuree.chf_id is not None:
            identifier = cls.build_fhir_identifier(imis_insuree.chf_id,
                                                   Stu3IdentifierConfig.get_fhir_identifier_type_system(),
                                                   Stu3IdentifierConfig.get_fhir_chfid_type_code())
            identifiers.append(identifier.__dict__)

    @classmethod
    def build_fhir_passport_identifier(cls, identifiers, imis_insuree):
        if hasattr(imis_insuree, "typeofid") and imis_insuree.typeofid is not None:
            pass  # TODO typeofid isn't provided, this section should contain logic used to create passport field based on typeofid
        elif imis_insuree.passport is not None:
            identifier = cls.build_fhir_identifier(imis_insuree.passport,
                                                   Stu3IdentifierConfig.get_fhir_identifier_type_system(),
                                                   Stu3IdentifierConfig.get_fhir_passport_type_code())
            identifiers.append(identifier.__dict__)

    @classmethod
    def build_fhir_birth_date(cls, fhir_patient, imis_insuree):
        fhir_patient.birthDate = imis_insuree.dob.isoformat()

    @classmethod
    def build_imis_birth_date(cls, imis_insuree, fhir_patient, errors):
        if not cls.valid_condition(fhir_patient.get('birthDate') is None,
                                   'Missing patient `birthDate` attribute', errors):
            dob = TimeUtils.str_to_date(fhir_patient.get('birthDate'))
            imis_insuree.dob = dob

    @classmethod
    def build_fhir_gender(cls, fhir_patient, imis_insuree):
        if hasattr(imis_insuree, "gender") and imis_insuree.gender is not None:
            code = imis_insuree.gender.code
            if code == GeneralConfiguration.get_male_gender_code():
                fhir_patient.gender = AdministrativeGender.MALE.value
            elif code == GeneralConfiguration.get_female_gender_code():
                fhir_patient.gender = AdministrativeGender.FEMALE.value
            elif code == GeneralConfiguration.get_other_gender_code():
                fhir_patient.gender = AdministrativeGender.OTHER.value
        else:
            fhir_patient.gender = AdministrativeGender.UNKNOWN.value

    @classmethod
    def build_imis_gender(cls, imis_insuree, fhir_patient):
        if fhir_patient.get("gender") is not None:
            gender = fhir_patient.get("gender")
            imis_gender_code = None
            if gender == AdministrativeGender.MALE.value:
                imis_gender_code = GeneralConfiguration.get_male_gender_code()
            elif gender == AdministrativeGender.FEMALE.value:
                imis_gender_code = GeneralConfiguration.get_female_gender_code()
            elif gender == AdministrativeGender.FEMALE.value:
                imis_gender_code = GeneralConfiguration.get_other_gender_code()
            if imis_gender_code is not None:
                imis_insuree.gender = Gender.objects.get(pk=imis_gender_code)

    @classmethod
    def build_fhir_marital_status(cls, fhir_patient, imis_insuree):
        if imis_insuree.marital is not None:
            if imis_insuree.marital == ImisMaritalStatus.MARRIED.value:
                fhir_patient.maritalStatus = \
                    cls.build_codeable_concept(Stu3MaritalConfig.get_fhir_married_code(),
                                               Stu3MaritalConfig.get_fhir_marital_status_system()).__dict__
            elif imis_insuree.marital == ImisMaritalStatus.SINGLE.value:
                fhir_patient.maritalStatus = \
                    cls.build_codeable_concept(Stu3MaritalConfig.get_fhir_never_married_code(),
                                               Stu3MaritalConfig.get_fhir_marital_status_system()).__dict__
            elif imis_insuree.marital == ImisMaritalStatus.DIVORCED.value:
                fhir_patient.maritalStatus = \
                    cls.build_codeable_concept(Stu3MaritalConfig.get_fhir_divorced_code(),
                                               Stu3MaritalConfig.get_fhir_marital_status_system()).__dict__
            elif imis_insuree.marital == ImisMaritalStatus.WIDOWED.value:
                fhir_patient.maritalStatus = \
                    cls.build_codeable_concept(Stu3MaritalConfig.get_fhir_widowed_code(),
                                               Stu3MaritalConfig.get_fhir_marital_status_system()).__dict__
            elif imis_insuree.marital == ImisMaritalStatus.NOT_SPECIFIED.value:
                fhir_patient.maritalStatus = \
                    cls.build_codeable_concept(Stu3MaritalConfig.get_fhir_unknown_marital_status_code(),
                                               Stu3MaritalConfig.get_fhir_marital_status_system()).__dict__

    @classmethod
    def build_imis_marital(cls, imis_insuree, fhir_patient):
        if fhir_patient.get("maritalStatus") is not None:
            maritalStatus = fhir_patient.get("maritalStatus")
            for maritialCoding in maritalStatus.get('coding'):
                if maritialCoding.get("system") == Stu3MaritalConfig.get_fhir_marital_status_system():
                    code = maritialCoding.get("code")
                    if code == Stu3MaritalConfig.get_fhir_married_code():
                        imis_insuree.marital = ImisMaritalStatus.MARRIED.value
                    elif code == Stu3MaritalConfig.get_fhir_never_married_code():
                        imis_insuree.marital = ImisMaritalStatus.SINGLE.value
                    elif code == Stu3MaritalConfig.get_fhir_divorced_code():
                        imis_insuree.marital = ImisMaritalStatus.DIVORCED.value
                    elif code == Stu3MaritalConfig.get_fhir_widowed_code():
                        imis_insuree.marital = ImisMaritalStatus.WIDOWED.value
                    elif code == Stu3MaritalConfig.get_fhir_unknown_marital_status_code():
                        imis_insuree.marital = ImisMaritalStatus.NOT_SPECIFIED.value

    @classmethod
    def build_fhir_telecom(cls, fhir_patient, imis_insuree):
        telecom = []
        if imis_insuree.phone is not None:
            phone = cls.build_fhir_contact_point(imis_insuree.phone, ContactPointSystem.PHONE.value,
                                             ContactPointUse.HOME.value)
            telecom.append(phone.__dict__)
        if imis_insuree.email is not None:
            email = cls.build_fhir_contact_point(imis_insuree.email, ContactPointSystem.EMAIL.value,
                                             ContactPointUse.HOME.value)
            telecom.append(email.__dict__)
        fhir_patient.telecom = telecom

    @classmethod
    def build_imis_contacts(cls, imis_insuree, fhir_patient):
        if fhir_patient.get('telecom') is not None:
            for contact_point in fhir_patient.get('telecom'):
                if contact_point.get("system") == ContactPointSystem.PHONE.value:
                    imis_insuree.phone = contact_point.get("value")
                elif contact_point.get("system") == ContactPointSystem.EMAIL.value:
                    imis_insuree.email = contact_point.get("value")

    @classmethod
    def build_fhir_addresses(cls, fhir_patient, imis_insuree):
        addresses = []
        if imis_insuree.current_address is not None:
            current_address = cls.build_fhir_address(imis_insuree.current_address, AddressUse.HOME.value,
                                                     AddressType.PHYSICAL.value)
            addresses.append(current_address.__dict__)
        if imis_insuree.geolocation is not None:
            geolocation = cls.build_fhir_address(imis_insuree.geolocation, AddressUse.HOME.value,
                                                 AddressType.BOTH.value)
            addresses.append(geolocation.__dict__)
        fhir_patient.address = addresses

    @classmethod
    def build_imis_addresses(cls, imis_insuree, fhir_patient):
        if fhir_patient.get('address') is not None:
            for address in fhir_patient.get('address'):
                if address.get("type") == AddressType.PHYSICAL.value:
                    imis_insuree.current_address = address.get("text")
                elif address.get("type") == AddressType.BOTH.value:
                    imis_insuree.geolocation = address.get("text")

    class Meta:
        app_label = 'api_fhir'
