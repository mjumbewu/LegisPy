It is totally 3:24 AM and I am at SXSW lacking some essential facilities, but I
am going to get this pumped out before the morning.

=======
LegisPy
=======

*LegisPy* is a friendly wrapper around the SOAP API for Granicus' Legistar leegislation management system.

Inspired by the API work of @zachwills, a talented developer, and a friend, as
well as the Ruby-language Granicus API.

*LegisPy* is built on top of the excellent `SUDS <https://fedorahosted.org/suds/>`_ client for SOAP services.

Getting Started
===============

The first thing you need to get started with this API is an API key.  Getting one of those is easy.  Contact `Granicus <http://www.granicus.com/form/Contact.html>`_ and let them know you're interested in working with their data.

After you have an API key, you'll have to get permission to access your city's or county's data.  I think this is because there's no separation between the read and write API (though there should be).  Contact Granicus to get information on how to get access to your city's data.  Tell them I sent you ;-).  And, while you're at it, tell them to separate read and write APIs.

Usage
=====

::

    >>> from legistar import Legistar
    >>>
    >>> api = Legistar('12345678-90AB-CDEF-1234-567890ABCDEF')
    >>> government = api.governments()[0]
    >>> api.use(government)
    >>>
    >>> actions = api.actions()
    >>> print [action.name for action in actions]
    [RECONSIDERED, VETO OVERRIDDEN, ADOPTED, ADOPTED & REFERRED, ADOPTED BY
    STANDING VOTE, AMENDED, blank, CALLED OUT OF COMMITTEE, Cancellation of
    Scheduled Public Hearing, DISAPPROVED, FAILED, FAVORABLY RECOMMENDED - RULES
    SUSPENDED; CONSIDERATION AT END OF CALENDAR, FAVORABLY RECOMMENDED AND
    ADOPTED, FAVORABLY RECOMMENDED; CONSIDERATION AT END OF CALENDAR, FAVORABLY
    RECOMMENDED; CONSIDERATION AT NEXT STATED COUNCIL MEETING, HEARING HELD,
    HEARING NOTICES SENT, Introduced, ...]


If you know the GUID of the government that you'd like to access beforehand,
you can pass it to the api on creation::

    >>> api = Legistar('12345678-90AB-CDEF-1234-567890ABCDEF',
    ...                gov_guid="12345678-90AB-CDEF-1234-567890ABCDEF")

The attributes available on an object are readily discoverable through
introspection::

    >>> action = actions[0]
    >>> dir(action)
    [..., 'active_tense_flag', 'e_number_flag', 'final_flag', 'guid', 'key',
    'lock_flag', 'name', 'target_flag']

You can also find the attributes from the object's string representation::

    >>> action
    (Action){
       ActionKey = "15"
       ActionGUID = "565669E9-EE98-4C75-8E73-D838EDE1810C"
       ActionName = "RECONSIDERED"
       ActionFinalFlag = "0"
       ActionTargetFlag = "0"
       ActionActiveTenseFlag = "0"
       ActionENumberFlag = "0"
       ActionLockFlag = "0"
     }

Any attributes in the string representation will be converted to snake case
from camel case.  For example, the ``action`` printed above will have attributes
``key``, ``guid``, ``name``, ``final_flag``, and so on.
