class SoapyObjectProxy (object):

    def __init__(self, api, soapy_obj):
        self._api = api
        self._soapy_obj = soapy_obj

    def __getattr__(self, name):
        return getattr(self._soapy_obj, name)

    def __unicode__(self):
        return unicode(self._soapy_obj)

    def __repr__(self):
        return unicode(self)


class Body (SoapyObjectProxy):

    @property
    def guid(self):
        return self.BodyGUID

    def meetings(self):
        soapy_meetings = self._api._get_gov_data('MeetingGetAllForBody', BodyGUID=self.guid)
        return self._api._rinse(soapy_meetings.Meeting)
