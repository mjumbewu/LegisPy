"""
A Python wrapper for interacting with the Legistar API.
"""

import os.path
from collections import defaultdict
from itertools import ifilter

import requests
import suds
import suds.client
import suds.xsd.doctor
import json

from . import models

# To use the SOAP 1.2 interface, uncomment the following two lines.
#from suds.bindings import binding
#binding.envns = ('SOAP-ENV', 'http://www.w3.org/2003/05/soap-envelope')


class Legistar (object):
    wsdl_filename = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'legistar.wsdl'))

    def __init__(self, api_key, gov_guid=None, wsdl_url='file://' + wsdl_filename):
        if wsdl_url is None:
            wsdl_url = 'http://betasdk.legistar.com/main.asmx?WSDL'
        self.wsdl_url = wsdl_url
        self.api_key = api_key
        self.use(gov_guid)

    @property
    def client(self):
        if not hasattr(self, '_conn'):
            imp = suds.xsd.doctor.Import('http://www.w3.org/2001/XMLSchema')
            imp.filter.add('http://legistar.com/')
            d = suds.xsd.doctor.ImportDoctor(imp)
            self._conn = suds.client.Client(self.wsdl_url, doctor=d)
        return self._conn

    @property
    def gov_guid(self):
        return self._gov_guid

    def use(self, government):
        self._gov_guid = self._get_guid('Government', government)

    def _get_guid(self, obj_type, obj):
        if isinstance(obj, basestring):
            return obj
        else:
            return getattr(obj, obj_type + 'GUID')

    def using(self, government):
        api = Legistar(self.api_key, self.wsdl_url)
        api._conn = self._conn
        api.use_government(government)
        return api

#  ActionGetAll
    def actions(self):
        """
        Get the types of actions used by the given government.  The government
        parameter may either be a government id string or a government object
        returned from the Legistar.governments method.

        >>> api = Legistar(api_key='...')
        >>> governments = api.governments()
        >>> api.use(governments[0])
        >>> api.actions()
        """
        client = self.client
        soapy_actions = client.service.ActionGetAll(
            PartnerGUID=self.api_key,
            GovernmentGUID=self.gov_guid
        )

        return self._rinse(soapy_actions.Action)

#  ActionGetHistoryActions
#  ActionGetOne
    def action(self, action_id):
        """
        Get the action specified by the given ID.

        Action
        ------
        - ActionKey  (numeric string)
        - ActionGUID  (guid)
        - ActionName  (human-readable string)
        - ActionFinalFlag  ('1' or '0')
        - ActionTargetFlag  ('1' or '0')
        - ActionActiveTenseFlag  ('1' or '0')
        - ActionENumberFlag  ('1' or '0')
        - ActionLockFlag  ('1' or '0')

        >>> api = Legistar(api_key='...')
        >>> governments = api.governments()
        >>> api.use(governments[0])
        >>> api.action('<action_id>')
        """
        client = self.client
        soapy_action = client.service.ActionGetOne(
            PartnerGUID=self.api_key,
            GovernmentGUID=self._gov_guid,
            ActionID=action_id
        )

        return self._rinse(soapy_action)

#  ActionGetProceduralActions
#  ActionTextGetAll
#  ActionTextGetOne
#  (ActionUpdateOne)
#  AgendaDefinitionGetAll
#  (AgendaDefinitionUpdateOne)
#  (AttachmentDeleteOne)
#  AttachmentGetAll
    def attachments(self, meeting_item):
        """
        TODO: Test this after I get to meeting items.
        """
        soapy_attachments = self.client.service.AttachmentGetAll(
            PartnerGUID=self.api_key,
            GovernmentGUID=self.gov_guid,
            MeetingItemGUID=self._get_guid('MeetingItem', meeting_item)
        )

        return self._rinse(soapy_attachments)

#  AttachmentGetAllWithOptions
#  AttachmentGetOneByName
    def attachment(self, attachment_name):
        """
        TODO: Test this after I get to meeting items.
        """
        soapy_attachment = self.client.service.AttachmentGetOneByName(
            PartnerGUID=self.api_key,
            GovernmentGUID=self.gov_guid,
            AttachmentName=attachment_name
        )

        return self._rinse(soapy_attachments)

#  (AttachmentUpdateOne)
#  AttendanceTypeGetAll
    def attendance_types(self):
        """
        Get the list of meeting attendance types.

        AttendanceType
        --------------
        - AttendanceTypeGUID  (guid string)
        - AttendanceTypeName  (human-readable string)
        - AttendanceTypePluralName  (human-readable string)
        - AttendanceTypeUsedFor  (numeric string)
        - AttendanceTypeResult  (numeric string)
        - AttendanceTypeSort  (numeric string)

        """
        soapy_attendance = self.client.service.AttendanceTypeGetAll(
            PartnerGUID=self.api_key,
            GovernmentGUID=self.gov_guid,
        )

        return self._rinse(soapy_attendance.AttendanceType)

#  BodyGetAll
#  BodyGetAllThatMeet
#  BodyGetAllWithMeetings
    def bodies(self):
        """
        Get a list of all the bodies.

        Body
        ----
        - BodyGUID  (guid string)
        - BodyName  (human-readable string)
        - BodyTypeSort  (number)
        - BodyOLSUsed  (boolean)
        """
        soapy_bodies = self._get_gov_data('BodyGetAll', opts_name='BodyOptions')

        return self._rinse(soapy_bodies.Body, proxy=models.Body)

#  BodyGetCommitteeAll
#  BodyGetHistoryActionBodyAll
#  BodyGetHistoryTargetBodyAll
#  BodyGetNextMeetingDate
#  BodyGetOne
#  BodyHeaderGetAll
#  BodyHeaderUpdateOne
#  BodyTypeGetAll
#  BodyTypeGetOneByBodyID
#  BodyTypeUpdateOne
#  BodyUpdateOne

#  CodeSectionGetAll
#  CodeSectionGetAllByItemKey
#  CodeSectionGetOne
#  CodeSectionUpdateOne

#  DynamicDataDeleteByRecordID
#  DynamicDataGetAll
#  DynamicDataGetAllNoCache
#  DynamicDataUpdateCollection

#  GetCurrentCultureDateTimeFormatLongDatePattern
#  GetCurrentCultureDateTimeFormatShortDatePattern
#  GetCurrentCultureName

#  GetDataSet

#  GetDateTime

#  GetServerName

#  GetValue

#  GetVersion

#  GovernmentGetAll
    def governments(self):
        """
        Get a list of governments to which the API key affords access.

        Government
        ----------
        - GovernmentGUID
        - GovernmentName

        >>> api = Legistar(api_key='...')
        >>> api.governments()
        """
        soapy_governments = self.client.service.GovernmentGetAll(
            PartnerGUID=self.api_key
        )

        return self._rinse(soapy_governments.Government)

#  GovernmentGetExtraInfo
#  GovernmentGetGUIDFromHostName
#  GovernmentGetOne
    def government(self, gov_guid=None):
        """
        Get a government based on the guid.

        """
        if gov_guid is None:
            gov_guid = self.gov_guid

        soapy_government = self.client.service.GovernmentGetOne(
            PartnerGUID=self.api_key,
            GovernmentGUID=gov_guid
        )

        return self._rinse(soapy_government)

#  GovernmentGetSetting
#  (GovernmentUpdateOne)

#  HelpGetAll
#  HelpGetOne
#  (HelpUpdateOne)

#  HistoryRecordsByVoteType

#  IndexCategoryGetAll
#  (IndexDeleteOne)
#  IndexGetAll
#  IndexGetAllByItemKey
#  IndexGetOne
#  (IndexUpdateOne)

#  ItemCodeSectionUpdate
#  ItemCreateMany
#  ItemExtraInfoGetOne
#  ItemExtraInfoUpdateOne
#  ItemGetNextENNumber
#  ItemGetNextNumber
#  ItemGetOne
#  ItemGetOneByFileID
#  ItemGetYears
#  ItemHistoryCreate
#  ItemHistoryReferralsGetAll
#  ItemIncrementNumber
#  ItemIndexDelete
#  ItemIndexExtraUpdate
#  ItemIndexGetAllByItemKey
#  ItemIndexGetOne
#  ItemIndexUpdate
#  ItemIndexUpdateOne
#  ItemSearch
    def items(self):
        crit = ''
        soapy_items = self._get_gov_data('ItemSearch', ItemSearchCriteria=crit)

        return self._rinse(soapy_items)

#  ItemSponsorsCreate
#  ItemSponsorsGetAll
#  ItemStatusFromValidAction
#  ItemStatusFromValidActionNoStatus
#  ItemStatusGetAll
#  ItemStatusGetOne
#  ItemStatusUpdateOne
#  ItemTypeGetAll
#  ItemTypeGetOne
#  ItemTypeUpdateOne
#  ItemUpdateOne

#  LanguageTranslationGetAll
#  LanguageTranslationGetOne
#  LanguageTranslationGetOneByName
#  LanguageTranslationUpdateOne

#  LookUpGetAllByType

#  MeetingAcceptData
#  MeetingGetAllForBody
#  MeetingGetAllVoters
#  MeetingGetOne
#  MeetingGetProgress
#  MeetingGetYears
    def meeting_years(self):
        """
        Get a list of years for meetings for the current government.

        Meeting
        ----------
        - MeetingYear

        """
        soapy_meeting_years = self.client.service.MeetingGetYears(
            PartnerGUID=self.api_key,
            GovernmentGUID=self.gov_guid
        )

        return self._rinse(soapy_meeting_years.Meeting)

#  MeetingItemCreateRelationships
#  MeetingItemDelete
#  MeetingItemDeleteRelationships
#  MeetingItemDuplicate
#    Duplicates an item for the purpose of recording multiple actions.
#  MeetingItemGetAll
#  MeetingItemGetAllForOutline
#  MeetingItemGetAllWithVotes
#  MeetingItemGetAllWithoutNotes
#  MeetingItemGetAttendance
#  MeetingItemGetNotes
#  MeetingItemGetOne
#  MeetingItemGetOneByID
#  MeetingItemGetParentID
#  MeetingItemGetRollCall
#  MeetingItemGetVote
#  MeetingItemUpdateCollection
#  MeetingItemUpdateOneEx
#  MeetingLocationGetAll
#  MeetingLocationGetOne
#  MeetingSearch
    def meetings(self, SearchText=''):
        """
        Get a list of years for meetings for the current government.

        Meeting
        ----------
        - MeetingYear

        """
        criteria = self.client.factory.create('MeetingSearchCriteria')
        criteria.SearchText = SearchText

        soapy_meetings = self.client.service.MeetingSearch(
            PartnerGUID=self.api_key,
            GovernmentGUID=self.gov_guid,
            MeetingSearchCriteria=criteria
        )

        return self._rinse(soapy_meetings)

#  MeetingSearchWithSecurity
#  MeetingStatusGetAll
#  MeetingStatusGetOne
#  MeetingStatusUpdateOne
#  MeetingUpdateOneEx
#  MeetingUpdateSequenceEx
#  NameGetAll
#  NameGetOne
#  NameGetOneByUserID
#  NameUpdateOne
#  OfficeRecordGetAll
#  OfficeRecordGetAllForAdHoc
#  OfficeRecordGetCurrentPLBMembers
#  OfficeRecordGetCurrentPLBMembersWithMayorAndClerk
#  OfficeRecordGetOne
#  OfficeRecordGetOneByBodyNameAndOfficeTitle
#  PartnerGetName
#  PartnerUpdateOne
#  Ping
#  ProceduralActionGetAll
#  ReportGetAll
#  ReportUpdateOne
#  ReportsGetAllByArea
#  ReportsGetOneByKey
#  RollCallAdd
#  RollCallDeleteOne
#  RollCallGetExisting
#  RollCallUpdateEx
#  SecurityBodyRestrictionsByGroupID
#  SiteInfoGetOne
#  StandardParagraphGetAll
#  StandardParagraphGetOne
#  StandardParagraphUpdateOne
#  StreetGetAll
#  SystemColorGetAll
#  SystemColorUpdateOne
#  SystemHelpGetOne
#  SystemMessageGetAll
#  SystemMessageGetOne
#  SystemMessageUpdateOne
#  SystemSettingGetOne
#  SystemTextGetAll
#  SystemTextUpdateOne
#  TextGetOne
#  TextGetOneGUID
#  TextUpdateOne
#  ValidActionGetAll
#  ValidActionGetAllForMatter
#  ValidActionGetAllForMeeting
#  ValidActionGetOne
#  ValidActionGetStandardOne
#  VoteAndAttendanceTypeGetAll
#  VoteDeleteOne
#  VoteGetExisting
#  VoteTypeGetAll
#  VoteTypeGetOneByID
#  VoteTypeUpdateOne
#  VoteUpdateEx
    def procedural_actions(self):
        """
        (...none for Philadelphia)
        """
        soapy_actions = self.client.service.ActionGetProceduralActions(
            PartnerGUID=self.api_key,
            GovernmentGUID=self.gov_guid
        )

        return self._rinse(soapy_actions)

    def _get_gov_data(self, command_name, opts_name=None, options=None, **kwargs):
        """
        Construct a SOAP request that requires a GovernmentGUID.

        """
        return self._get_data(
            command_name,
            opts_name=opts_name,
            options=options,
            GovernmentGUID=self.gov_guid,
            **kwargs
        )

    def _get_data(self, command_name, opts_name=None, options=None, **kwargs):
        """
        Construct a SOAP request that requires a GovernmentGUID.

        """
        if opts_name is not None:
            opts = self.client.factory.create(opts_name)

            opts.Language = 'LanguageAll'
            opts.FormatGUID = 'No'

            if options is not None:
                for key, val in options.items():
                    setattr(opts, key, val)
            kwargs['Options'] = opts
        else:
            kwargs['Options'] = options

        soapy_data = getattr(self.client.service, command_name)(
            PartnerGUID=self.api_key,
            **kwargs
        )

        return soapy_data

    def _rinse(self, soapy_obj, proxy=models.SoapyObjectProxy):
        try:
            soapy_list = soapy_obj or []
            return [proxy(self, soapy_elem)
                    for soapy_elem in soapy_list]
        except TypeError:
            return soapy_obj

    def __download_wsdl(self):
        url = 'http://betasdk.legistar.com/main.asmx?WSDL'
        request = requests.get(url)

        self._wsdl = request.text
        with open(self.wsdl_filename, 'w') as f:
            f.write(self._wsdl)
