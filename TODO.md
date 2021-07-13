# Todo

## Endpoints
- [X] GET ``/api``

- [X] GET ``/api/config``

- [X] GET ``/api/discovery_info``

- [ ] GET ``/api/events``

- [X] GET ``/api/services``

- [ ] GET ``/api/history/period/<timestamp>``

- [ ] GET ``/api/logbook/<timestamp>``

- [X] GET ``/api/states``

- [X] GET ``/api/states/<entity_id>``

- [X] GET ``/api/error_log``

- [ ] POST ``/api/events/<event_type>``

- [X] POST ``/api/services/<domain>/<service>``

- [X] POST ``/api/config/core/check_config``

- [X] POST ``/api/states/<entity_id>``

# Features
- [ ] Add caching to Entity.get_state (to make it fetch state automatically)

- [ ] Create AsyncClient for integration in async applications and libraries
