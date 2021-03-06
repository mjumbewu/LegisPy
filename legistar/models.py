import re


def camel_to_snake(camel):
    """Convert key from camelcase to snakecase."""
    snake = camel

    snake = re.sub(ur'([A-Z]+)([A-Z][a-z])', ur'\1_\2', snake)
    snake = re.sub(ur'([a-z])([A-Z])', ur'\1_\2', snake)
    snake = snake.lower()

    return snake


class SoapyObjectProxy (object):

    def __init__(self, api, soapy_obj, soapy_prefix=None):
        self._api = api
        self._soapy_obj = soapy_obj
        self._init_attributes(soapy_obj, soapy_prefix)

    def _init_attributes(self, soapy_obj, soapy_prefix):
        soapy_prefix = soapy_prefix or self.__class__.__name__
        for key, val in soapy_obj:
            key = re.sub(ur'^' + soapy_prefix, u'', key)
            key = camel_to_snake(key)
            setattr(self, key, val)

    def __unicode__(self):
        return unicode(self._soapy_obj)

    def __repr__(self):
        return unicode(self)


class Action (SoapyObjectProxy):
    pass


class ActionText (SoapyObjectProxy):
    pass


class AttendanceType (SoapyObjectProxy):
    pass


class Body (SoapyObjectProxy):
    def meetings(self):
        soapy_meetings = self._api._get_gov_data('MeetingGetAllForBody', BodyGUID=self.guid)
        return self._api._rinse(soapy_meetings.Meeting, proxy=Meeting)

    def next_meeting_date(self):
        soapy_date = self._api._get_gov_data('BodyGetNextMeetingDate', BodyGUID=self.guid)
        return self._api._rinse(soapy_date)


class Government (SoapyObjectProxy):
    pass


class Item (SoapyObjectProxy):
    pass


class Meeting (SoapyObjectProxy):
    def progress(self):
        soapy_progress = self._api._get_gov_data('MeetingGetProgress', MeetingGUID=self.guid)
        return self._api._rinse(soapy_progress)

    def items(self):
        soapy_items = self._api._get_gov_data('MeetingItemGetAll', MeetingGUID=self.guid)
        return self._api._rinse(soapy_items.MeetingItem)

    def items_with_votes(self):
        soapy_items = self._api._get_gov_data('MeetingItemGetAllWithVotes', MeetingGUID=self.guid,
            options={'UseVote2': False, 'Language': 'LanguageAll', 'FormatGUID': 'No'})
        return self._api._rinse(soapy_items.MeetingItem, proxy=Item)

    def items_without_notes(self):
        soapy_items = self._api._get_gov_data('MeetingItemGetAllWithoutNotes', MeetingGUID=self.guid)
        return self._api._rinse(soapy_items.MeetingItem, proxy=Item)

    def attendance(self):
        soapy_attendance = self._api._get_gov_data('MeetingItemGetAttendance', MeetingGUID=self.guid)
        return self._api._rinse(soapy_attendance)
