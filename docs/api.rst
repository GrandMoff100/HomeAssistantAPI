Code Reference
***************

Client
--------

.. autoclass:: homeassistant_api.Client
   :members:
   :inherited-members:


Data Models
------------

.. automodule:: homeassistant_api.models

   .. autopydantic_model:: Domain

   .. autopydantic_model:: Service

   .. autopydantic_model:: Group

   .. autopydantic_model:: Entity

   .. autopydantic_model:: History

   .. autopydantic_model:: LogbookEntry

   .. autopydantic_model:: State

   .. autopydantic_model:: Event



.. automodule:: homeassistant_api._async.models

   .. autopydantic_model:: AsyncDomain

   .. autopydantic_model:: AsyncService

   .. autopydantic_model:: AsyncGroup

   .. autopydantic_model:: AsyncEntity

   .. autopydantic_model:: AsyncEvent


Processing
-----------


.. autoclass:: homeassistant_api.processing.Processing
   :members:


Exceptions
-----------

.. automodule:: homeassistant_api.errors
   :members:

