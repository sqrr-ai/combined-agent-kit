# Business-data MCP connection diagnostic

Use with https://www.trycombined.com/resources/mcp-authentication-errors-business-data
This worksheet is for your own diagnostic notes. Filling it does not send a support request.

## Connection

- Client and version:
- UTC time of failure:
- Endpoint origin and path (omit query values and credentials in a shared report):
- Transport: Streamable HTTP / another transport
- Authentication route: OAuth / provisioned credential
- First failing stage: connection / authorization / discovery / query / answer verification
- HTTP status, MCP error or correlation ID:

## Checks

1. Verify the exact endpoint from Combined's Access workspace, including the account ID in your private configuration.
2. Check JSON syntax and whether the client can see the intended environment variables.
3. If OAuth is used, inspect the WWW-Authenticate challenge and its protected-resource metadata URL.
4. If login succeeds but data is denied, check account membership and the specific source/dataset grants.
5. If discovery succeeds, use the returned relation and field names for one small read-only query.
6. If the query succeeds, inspect the receipt, freshness, truncation, coverage and reporting period.

## Public metadata check

This request has no credential and does not query business data:

```sh
curl --silent --show-error --max-time 20 \
  'https://platform.trycombined.com/.well-known/oauth-protected-resource/mcp'
```

A metadata response establishes discovery reachability only. It does not authenticate your client or prove a source grant.

## When sharing a diagnostic

Share the client version, UTC timestamp, failing stage, status and correlation ID.
Remove bearer tokens, provider secrets, cookies, customer records, query results and private account identifiers.
Do not paste a full network log without reviewing it for credentials and business data.

## References

- https://www.trycombined.com/docs/integrations/mcp
- https://www.trycombined.com/docs/getting-started/authentication
- https://www.trycombined.com/docs/troubleshooting/query-and-mcp
