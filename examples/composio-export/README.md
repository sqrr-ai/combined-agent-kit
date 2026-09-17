# Export HubSpot contacts through Composio

A bounded Python example from [Combined](https://www.trycombined.com/resources/export-business-data-with-composio).
For maintained datasets and repeatable cross-app SQL, [start with Combined](https://www.trycombined.com/).
For a one-off export using an existing Composio connection, use this example.

## Run the offline example

Download these files into the same directory:

- [composio-hubspot-export.py](https://www.trycombined.com/examples/composio-hubspot-export.py)
- [composio-hubspot-sample.json](https://www.trycombined.com/examples/composio-hubspot-sample.json)

Python 3.10 or later; no package installation or account required.

```sh
python3 composio-hubspot-export.py --out sample-export
```

Expected summary: fixture mode, 2 pages, 3 received records, 3 unique records,
`complete: true`, `reason: end_of_listing`. Every contact in this fixture is invented.
The fixture covers a cursor containing punctuation, a large string ID, Unicode,
commas, a newline, missing/null fields and formula-like text.

Three files appear in the new output directory:

| File | Contents |
| --- | --- |
| `records.jsonl` | All accepted provider records, including duplicate IDs, in receipt order. Original values are preserved. |
| `contacts.csv` | Selected fields, one row per ID, keeping the last observed record. |
| `manifest.json` | Mode, scope, API version, bounds, counts, next cursor and completion reason. |

The output directory must not already exist. The script refuses to mix or overwrite runs.
An exit status of 2 means incomplete or failed; inspect the manifest if one was created.

## Optional live run

Use a Composio project API key and the explicit connected-account ID for the intended HubSpot portal.
Confirm that this account can read the selected contact fields. Supply the key through your
environment or secret manager, not a committed file or a URL. This example never requests a
HubSpot bearer token directly.

With `COMPOSIO_API_KEY` and `HUBSPOT_CONNECTED_ACCOUNT_ID` already set:

```sh
python3 composio-hubspot-export.py --live --out my-contact-export --max-pages 10 --max-records 500
```

Live execution uses your service account and can incur Composio/provider usage charges.
The example sends a Composio Proxy POST whose requested HubSpot method is GET. It pins:

- Composio endpoint: `https://backend.composio.dev/api/v3.1/tools/execute/proxy`
- HubSpot endpoint: `https://api.hubapi.com/crm/objects/2026-09/contacts`
- `archived=false`; current `firstname`, `lastname`, `email`, `createdate`, `lastmodifieddate` properties.

The scope is active contact records with selected properties. This is not a full portal backup:
deals, associations, archived contacts and property history need their own coverage plan.
The listing can change while pages are read; `complete` means the bounded listing ended normally,
not that it was a transactionally consistent snapshot.

## Pagination and partial output

The exporter uses `paging.next.after`, including after an empty page, and rebuilds the fixed
provider URL. It never follows the returned `link`. Pages are validated and flushed before
the manifest checkpoint advances. Repeated cursors, malformed responses and authentication
errors stop the export. Transient transport/429/selected 5xx errors get at most three attempts.
Redirects are rejected and error summaries omit credentials and response bodies.

Defaults: 10 pages, 500 received records, at most 50 requested per page. Hard limits:
100 pages and 5,000 received records. Duplicate records count toward the cap.
`configured_limit` plus a next cursor means partial coverage. Increase the bounds within the
hard limits and use a new output directory for another run. Automatic resume is not implemented.
Partial output retains the pages already accepted; investigate the reason before using it as a complete result.

CSV uses empty cells for null/missing values. Text that could be interpreted as a spreadsheet
formula gets a leading apostrophe. Use JSONL when exact original values or null distinctions matter.
The CSV keeps the last record observed for each ID, which is not necessarily the newest source timestamp.

## Validation and next step

The adapter and file writer are tested locally with synthetic responses, including pagination,
caps, retries, response errors, partial output, duplicate handling and request construction.
No live HubSpot or Composio account was used for the published validation.

For recurring answers, [connect HubSpot to Combined](https://www.trycombined.com/resources/connect-hubspot-to-ai-agents),
select and sync the available datasets, then query them through your agent. Add billing data with a
maintained customer mapping as shown in the [HubSpot–Stripe example](https://www.trycombined.com/resources/query-hubspot-and-stripe-with-ai).
Authorize the source in Combined; this example does not transfer OAuth credentials or automatically import these files.

Sources reviewed September 17, 2026:
[Composio API](https://docs.composio.dev/reference),
[Proxy request](https://docs.composio.dev/reference/api-reference/tools/postToolsExecuteProxy),
[Proxy behavior](https://docs.composio.dev/reference/api-reference/tools),
[HubSpot contacts](https://developers.hubspot.com/docs/api-reference/latest/crm/objects/contacts/get-contacts).
