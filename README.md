# sint-epistemic-mcp

Epistemic Status Tracking MCP server — tracks what an agent KNOWS vs INFERS vs ASSUMES with calibrated confidence.

## Tools

| Tool | Description |
|------|-------------|
| `epistemic_register(claim, status, confidence, source, domain)` | Register a knowledge claim with epistemic status |
| `epistemic_status(claim_query, domain)` | Look up claims by text or domain |
| `epistemic_calibrate(domain)` | Get calibration accuracy stats for a domain |
| `epistemic_gaps(domain)` | Identify domains with high ASSUMED/UNCERTAIN ratio |
| `epistemic_graph(domain)` | Export knowledge status as a graph (nodes + edges) |
| `epistemic_stats()` | Summary statistics across all claims |

## Status Types

- **VERIFIED** — confirmed by external validation
- **INFERRED** — logically derived from verified claims
- **ASSUMED** — taken as true without verification
- **UNCERTAIN** — insufficient evidence either way

## Usage

Add to your MCP config:
```json
{
  "mcpServers": {
    "sint-epistemic-mcp": {
      "command": "python",
      "args": ["/path/to/sint-epistemic-mcp/server.py"]
    }
  }
}
```
