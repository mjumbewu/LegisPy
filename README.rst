=======
LegisPy
=======

*LegisPy* aims to be a friendly wrapper around the SOAP API for Granicus'
Legistar legislation management system, the description of which is available
at http://sdk.legistar.com/main.asmx (the `betasdk` branch is for
http://betasdk.legistar.com/main.asmx).

Inspired by the API work of @zachwills, a talented developer and a friend.

*LegisPy* is built on top of the excellent `SUDS
<https://fedorahosted.org/suds/>`_ client for SOAP services.

Getting Started
===============

The first thing you need to get started with this API is an API key. You'll have
to get permission to access your city's or county's data. I think this is
because there's no separation between the read and write API (though there
should be). Contact Granicus to get information on how to get access to your
city's data. Getting one of those may involve a few steps:

* Contacting someone at your local clerk's office and asking for permission
* Asking someone on your local council or legislative body (see the LETTERS.rst
  file)
* Contacting Granicus_ through their site, or through the dev-list_, and
  forwarding along a statement of permission (they're nice guys). And, while
  you're at it, tell them to separate read and write APIs so that all of this
  isn't necessary.

.. _Granicus: http://www.granicus.com/form/Contact.html
.. _dev-list: https://groups.google.com/forum/?fromgroups#!forum/granicus-developers


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
