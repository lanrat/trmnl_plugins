# [GitHub Workflow Actions](https://usetrmnl.com/recipes/162049)

A TRMNL plugin that displays the status of GitHub Actions workflows on your e-ink display.

## Description

This plugin monitors GitHub Actions workflows for specified users and repositories, displaying their current status and recent activity.

## Settings

- **GitHub Usernames**: Comma-separated list of GitHub usernames to monitor
- **GitHub Repositories**: Comma-separated list of repositories in owner/repo format
- **GitHub Personal Access Token**: Optional PAT for higher API rate limits
- **Maximum Age (days)**: Only show workflows from the last N days (default: 7)
