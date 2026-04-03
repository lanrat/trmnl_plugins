# MCP Servers

Configured in `.mcp.json`. Used by Claude Code to interact with external tools.

## TRMNL

Connects Claude Code to a single TRMNL plugin via the platform API. See [TRMNL AI Agent docs](https://help.trmnl.com/en/articles/14130438-ai-agent) for setup details.

Each API key (`ps_mcp_*`) is scoped to one plugin. Set `TRMNL_MCP_API_KEY` in `trmnl.env` to the key of the plugin you want to work with:

```bash
TRMNL_MCP_API_KEY=ps_mcp_xxxxx
```

Find the key in your plugin's MCP settings on [trmnl.com](https://trmnl.com).

Since Claude Code resolves env vars from the process environment (not `.env` files), source `trmnl.env` before launching:

```bash
set -a; source trmnl.env; set +a
```

Restart the session after changing the key to switch plugins.

## Chrome DevTools

Connects to a running Chrome instance for inspecting pages, running scripts, taking snapshots, and monitoring network/console. Useful for debugging markup with `trmnlp serve`.

Requires Chrome with remote debugging:

```bash
google-chrome --remote-debugging-port=9222
```
