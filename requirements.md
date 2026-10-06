# Requirements

## User Story

**Jira:** KAN-1 â€” Search flight  
**Type:** Story | **Priority:** Medium | **Status (at capture):** To Do

As a user,  
I want to search for available flights by entering source, destination, and travel date,  
So that I can view matching flight options.

## Clarifications (Q&A summary)

Human approved proceeding with the following sensible defaults for all open clarifying questions:

1. **Scope:** Out of scope â€” booking, payment, seat selection, real airline APIs. In scope â€” search against dummy/mock flights only.
2. **Result fields per flight:** airline, flight number, departure city, arrival city, departure time, arrival time, duration, number of stops, price (display).
3. **City input:** Free text with case-insensitive matching against dummy data city names.
4. **Matching:** Case-insensitive exact match on departure city + arrival city + travel date; reject when departure city equals arrival city with a clear validation error; zero matches â†’ appropriate empty message.
5. **Passengers:** Integer, minimum 1, maximum 9; display-only for this story (does not filter inventory or change listed price).
6. **Dates:** Required; block past dates relative to server/local â€œtodayâ€; use HTML date input / ISO `YYYY-MM-DD`.
7. **Auth:** Anonymous public search â€” no login.
8. **Empty/error UX:** Validation messages for missing required fields, invalid passengers, past date, same cities; â€œNo flights foundâ€ (or equivalent) when search succeeds with zero matches.
9. **Delivery:** Python web application; Playwright E2E in Verify; framework choice deferred to Architecture.

## Functional Requirements

1. The system shall provide a public (unauthenticated) web page for flight search.
2. The search form shall accept: departure city (required), arrival city (required), travel date (required, `YYYY-MM-DD`), and number of passengers (required integer, 1â€“9).
3. The user shall be able to submit the form via a **Search Flights** control.
4. On valid submit, the system shall query an in-app **dummy/mock** flight dataset (not a live airline API).
5. Matching shall be case-insensitive exact equality on departure city name, arrival city name, and travel date.
6. When departure city and arrival city are the same (after trim / case-insensitive compare), the system shall not search and shall show a clear validation error.
7. Past travel dates (before local/server â€œtodayâ€) shall be rejected with a clear validation error.
8. Missing required fields or passenger count outside 1â€“9 shall produce clear validation errors without performing a search.
9. When a valid search returns one or more matches, the system shall display a list; each row/card shall include: airline, flight number, departure city, arrival city, departure time, arrival time, duration, number of stops, and price (display only).
10. When a valid search returns zero matches, the system shall show an empty-state message equivalent to â€œNo flights found.â€
11. Passenger count shall be shown in the UI context as entered but shall not filter inventory or alter listed prices in this story.

## Non-Functional Requirements

1. **Delivery stack:** Implement as a **Python web application**; specific framework (e.g. Flask/FastAPI/Django) is chosen in Architecture.
2. **Verification:** Stage 7 shall include **Playwright** E2E coverage of the primary search UI flows (happy path, validation errors, no-results).
3. **Security:** No API keys, tokens, passwords, or other secrets in source, tests, UI, or documentation; `api-conf.properties` must not be committed.
4. **Reliability / errors:** Invalid input and empty results fail gracefully with clear user-visible messages (no stack traces or secret leakage).
5. **Usability:** Form labels and error/empty messages are understandable without prior training.
6. **Observability (minimal):** Application errors related to unexpected failures are logged safely (no secrets); success path logging is optional for MVP.
7. **Performance (MVP):** A single search against the in-memory/file dummy dataset completes within 2 seconds under normal local/dev load.

## Acceptance Criteria

- [ ] Anonymous user can open the flight search page without logging in.
- [ ] User can enter departure city, arrival city, travel date (`YYYY-MM-DD`), and passengers (1â€“9), then click **Search Flights**.
- [ ] Valid matching dummy flights are listed with: airline, flight number, departure city, arrival city, departure time, arrival time, duration, stops, price.
- [ ] Case-insensitive city matching works (e.g. `delhi` matches `Delhi` in dummy data).
- [ ] Same departure and arrival city shows a validation error and no result list.
- [ ] Past travel date shows a validation error and no result list.
- [ ] Missing required fields or passengers outside 1â€“9 show validation errors and no result list.
- [ ] Valid search with zero matches shows â€œNo flights foundâ€ (or equivalent).
- [ ] No real airline/booking/payment integrations are used; data is dummy/mock only.
- [ ] No secrets appear in application output or committed docs.
- [ ] Delivery is a Python web app; Playwright E2E scripts will cover primary flows in Verify.

## Out of Scope

- Flight booking, payment, seat selection, check-in, cancellations, or itinerary management
- Real airline, GDS, or third-party flight APIs
- User registration, login, roles, or personalized saved searches
- Multi-city, round-trip, or return-date search (one-way single date only)
- Inventory/pricing logic driven by passenger count
- Admin UI for managing the dummy flight catalog (static/mock data is sufficient)
- Non-Python delivery stacks (unless explicitly re-approved)

## Open Questions

None for Stage 1. Framework choice and dummy-data storage shape are deferred to Architecture (Stage 2).
