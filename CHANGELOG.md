# Changelog

**v2.0.0**
- Added Data Models
- Added Documentation
- Added functions for all endpoints

**v2.1.0**
- Added Event support

**v2.2.0**
- Implemented async support with `homeassistant_api._async.AsyncClient`

**v2.3.0**
- Bug fixes (see closed issues between releases)
- Added global request kwargs parameter to Client objects (see [docs](homeassistantapi.rtfd.io/en/latest/api.html#homeassistant_api.Client))

**v2.4.0**
- Bug fixes (see closed issues between releases)
- Added a processing framework for hooking into mimetype processing
- Fixed some issues with some ``AsyncClient`` methods

**v2.4.0.post1**
- Replaced `text/plain` with `application/octet-stream` in docs and processing module.
- Added message content to UnrecognizedStatusCodeError to help with user debugging
