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
        self._gov_guid = self._get_guid(government)

    def _get_guid(self, obj):
        if isinstance(obj, basestring):
            return obj
        else:
            return obj.guid

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
        >>> api.actions()
        """
        soapy_actions = self._get_gov_data('ActionGetAll')
        return self._rinse(soapy_actions.Action, models.Action)

#  ActionTextGetAll
    def action_text(self):
        """
        Get the MadLib-like text snippets for different action types.

        ActionText
        ----------
        ActionTextGUID = "F7B15003-244A-4AB6-B55C-7829CD162CB6"
        ActionTextName = "CONSENT ROLLCALL"
        ActionTextResultFailedText = "failed"
        ActionTextVoteConsentRollCall = " by consent roll call"
        ActionTextNoVoteStartPhrase = "This [FILE_TYPE] was"
        ActionTextNoVoteActionName = " [ACTION_NAME]"
        ActionTextNoVoteReferred = "to the [TARGET_BODY]"
        ActionTextNoVoteDueDate = "due back on [DUE_DATE]"
        ActionTextVoteStartPhrase = "This"
        ActionTextVoteFileType = " that this [FILE_TYPE] be [ACTION_NAME] "
        ActionTextVoteReference = " to the [TARGET_BODY] "
        ActionTextVoteDueDate = " due back on [DUE_DATE]"

        """
        soapy_text = self._get_gov_data('ActionTextGetAll')
        return self._rinse(soapy_text.ActionText, models.ActionText)

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
        soapy_types = self._get_gov_data('AttendanceTypeGetAll')
        return self._rinse(soapy_types.AttendanceType, models.AttendanceType)

#  BodyGetAll
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
        soapy_bodies = self._get_gov_data('BodyGetAll')
        return self._rinse(soapy_bodies.Body, proxy=models.Body)

#  BodyGetAllThatMeet
    def bodies_that_meet(self):
        """
        Get a list of all the bodies that have meetings(?).
        NOTE: All I ever get is an empty list.
        """
        soapy_bodies = self._get_gov_data('BodyGetAllThatMeet')
        return self._rinse(soapy_bodies.Body, proxy=models.Body)

#  BodyGetAllWithMeetings
    def bodies_with_meetings(self):
        """
        Get a list of all the bodies that have upcoming meetings(?).
        """
        soapy_bodies = self._get_gov_data('BodyGetAllWithMeetings')
        return self._rinse(soapy_bodies.Body, proxy=models.Body)

#  BodyGetOne
    def body(self, guid):
        soapy_body = self._get_gov_data('BodyGetOne', BodyGUID=guid)
        return self._rinse(soapy_body, proxy=models.Body)

#  GetDateTime
    def datetime(self):
        """
        Get the date and time on the server.
        """
        soapy_dt = self._get_data('GetDateTime')
        return self._rinse(soapy_dt)

#  GetServerName
    def server_name(self):
        """
        Get the name of the server
        """
        soapy_name = self._get_data('GetServerName')
        return self._rinse(soapy_name)

#  GetVersion
    def version(self):
        """
        Get the version of the API
        """
        soapy_version = self._get_data('GetVersion')
        return self._rinse(soapy_version)

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
        soapy_governments = self._get_data('GovernmentGetAll')
        return self._rinse(soapy_governments.Government, models.Government)

#  GovernmentGetOne
    def government(self, guid):
        """
        Get the government that corresponds to the given GUID.
        """
        soapy_government = self._get_data('GovernmentGetOne', GovernmentGUID=guid)
        return self._rinse(soapy_government, models.Government)

#  GovernmentGetSetting

#  ItemGetNextNumber
    def next_item_number(self, type_guid):
        """
        Given an item-type id ...
        NOTE: Not sure what exactly this gives you.
        """
        soapy_number = self._get_gov_data('ItemGetNextNumber', TypeGUID=type_guid)
        return self._rinse(soapy_number)

#  ItemGetOne
    def item(self, fileid, guid):
        soapy_item = self._get_gov_data('ItemGetOne', ItemID=fileid, ItemGUID=guid)
        return self._rinse(soapy_item, proxy=models.Item)

#  ItemGetYears
    def item_years(self):
        soapy_years = self._get_gov_data('ItemGetYears')
        return [unicode(i.item_year) for i in self._rinse(soapy_years.Item)]

#  (ItemIncrementNumber)
#  ItemSearch
    def items(self):
        crit = ''
        soapy_items = self._get_gov_data('ItemSearch', ItemSearchCriteria=crit) #, ItemSearchCriteria=dict(SearchText='streets', ItemDate='', ItemTypeGUID='', IncludeName=True, IncludeTitle=True, IncludeItemsWithFinalActionDate=True))
        return self._rinse(soapy_items.Item, proxy=models.Item)

#  ItemTypeGetAll
    def item_types(self):
        soapy_item_types = self._get_gov_data('ItemTypeGetAll')
        return self._rinse(soapy_item_types.ItemType)

#  (ItemUpdateOne)

#  MeetingAcceptData
#  MeetingGetAllForBody (see Body.meetings)
#  MeetingGetOne
    def meeting(self, guid):
        soapy_meeting = self._get_gov_data('MeetingGetOne', MeetingGUID=guid)
        return self._rinse(soapy_meeting, proxy=models.Meeting)

#  MeetingGetProgress (see Meeting.progress)
#  MeetingGetYears
    def meeting_years(self):
        """
        Get a list of years for meetings for the current government.

        Meeting
        ----------
        - MeetingYear

        """
        soapy_meeting_years = self._get_gov_data('MeetingGetYears')
        return [unicode(m.meeting_year)
                for m in self._rinse(soapy_meeting_years.Meeting)]

#  MeetingItemCreateRelationships
#  MeetingItemDelete
#  MeetingItemDeleteRelationships
#  MeetingItemDuplicate
#    Duplicates an item for the purpose of recording multiple actions.
#  MeetingItemGetAll (see Meeting.items)
#  MeetingItemGetAllForOutline
#  MeetingItemGetAllWithVotes
#  MeetingItemGetAllWithoutNotes (see Meeting.items_without_notes)
#  MeetingItemGetAttendance (see Meeting.attendance)
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

        return self._rinse(soapy_meetings.Meeting, proxy=models.Meeting)

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
    def text(self, fileid, version=None):
        soapy_text = self._get_gov_data('TextGetOne', ItemID=fileid, ItemVersion=version)
        return self._rinse(soapy_text)

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
        Construct a SOAP request that requires a GovernmentGUID.  Shorthand for:

            client.service.<command_name>(
                PartnerGUID=self.api_key,
                GovernmentGUID=self.gov_guid,
                Options|<opts_name>=<options>,
                **kwargs
            )
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
        kwargs_copy = kwargs.copy()

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

        for soap_opt_name, soap_opt_kwargs in kwargs_copy.items():
            if isinstance(soap_opt_kwargs, dict):
                soap_obj = self.client.factory.create(soap_opt_name)
                for key, val in soap_opt_kwargs.items():
                    setattr(soap_obj, key, val)
                kwargs[soap_opt_name] = soap_obj

        soapy_data = getattr(self.client.service, command_name)(
            PartnerGUID=self.api_key,
            **kwargs
        )

        return soapy_data

    def _rinse(self, soapy_obj, proxy=models.SoapyObjectProxy):
        if soapy_obj is None:
            return

        elif isinstance(soapy_obj, list):
            soapy_list = soapy_obj or []
            return [proxy(self, soapy_elem)
                    for soapy_elem in soapy_list]

        elif isinstance(soapy_obj, suds.sax.text.Text):
            return unicode(soapy_obj)

        else:
            return proxy(self, soapy_obj)

    def __download_wsdl(self):
        url = 'http://betasdk.legistar.com/main.asmx?WSDL'
        request = requests.get(url)

        self._wsdl = request.text
        with open(self.wsdl_filename, 'w') as f:
            f.write(self._wsdl)
