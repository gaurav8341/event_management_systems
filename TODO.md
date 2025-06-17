# TODOs for Event Management System

## 1. Timezone Management
- [x] Store all event times in UTC.
- [x] Accept timezone as a query parameter and convert times in API responses.
- [x] Accept timezone in event creation and convert to UTC.

## 2. Database Constraints
- [ ] Add a unique constraint on (event_id, email) at the database level for Attendee.

## 3. Input Validation & Error Handling
- [ ] Improve error messages for all endpoints.
- [ ] Add robust input validation (e.g., start_time < end_time, max_capacity > 0).

## 4. Pagination
- [ ] Improve attendee list endpoint to return pagination metadata (total count, skip, limit).

## 5. Unit Tests
- [ ] Write unit tests for all endpoints using pytest.

## 6. Documentation
- [ ] Add descriptions, examples, and tags to endpoints for better auto-generated docs.

## 7. Deployment & Environment
- [ ] Add configuration for different environments (dev, prod).
- [ ] Add Dockerfile or deployment scripts if needed.

## 8. Security
- [ ] Add basic authentication/authorization if required.
