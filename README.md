# TRMNL Plugins

A collection of custom plugins for [TRMNL](https://usetrmnl.com/) e-ink displays.

## Overview

This repository contains various TRMNL plugins, each in its own directory. Each plugin directory includes a README.md file with detailed information about the plugin's functionality and configuration settings.

## Development

### Prerequisites

- Docker
- TRMNL API key (obtain from [your TRMNL account](https://usetrmnl.com/account))

### Setup

1. Create a `trmnl.env` file in the root directory with your API key:

   ```env
   TRMNL_API_KEY=your_api_key_here
   ```

2. Use the `trmnlp.sh` script to develop and test plugins:

   ```bash
   ./trmnlp.sh <plugin-directory> [command]
   ```

The script runs the TRMNL plugin development environment in Docker, mounting the specified plugin directory and making it available at <http://localhost:4567>.
