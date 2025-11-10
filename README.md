# TRMNL Plugins

A collection of custom plugins for [TRMNL](https://usetrmnl.com/) e-ink displays.

## Overview

This repository contains various TRMNL plugins, each in its own directory. Each plugin directory includes a README.md file with detailed information about the plugin's functionality and configuration settings.

## Development

### Prerequisites

- Docker
- TRMNL API key (obtain from [your TRMNL account](https://usetrmnl.com/account))

### Setup

1. Use the `trmnlp.sh` script to develop and test plugins:

   ```bash
   ./trmnlp.sh <plugin-directory> [command]
   ```

   On first run, the script will prompt you to enter your TRMNL API key and automatically create the `trmnl.env` file.

The script runs the TRMNL plugin development environment in Docker, mounting the specified plugin directory and making it available at <http://localhost:4567>.


### Usage

Create a new plugin with:

```bash
 ./trmnlp.sh <new-plugin-dir-name> init
 ```

Run the development server:

```bash
 ./trmnlp.sh <plugin-directory> serve
 ```

Pull changes from TRMNL server:

```bash
 ./trmnlp.sh <plugin-directory> pull
 ```

Push changes to TRMNL server:

```bash
 ./trmnlp.sh <plugin-directory> push
 ```
