@echo off
rem Start MongoDB Model Context Protocol (MCP) Server for Break-Even
rem Designed for clean stdio JSON-RPC transport (no echo or output noise)

cd /d "%~dp0"
..\.venv\Scripts\python.exe app/services/mcp_server.py
