# Detection-as-Code Usage Guide

## How to Request New Detections

This guide explains how to interact with the AI assistant to create new detection rules for your Sumo Logic environment.

## Overview

The AI assistant has been configured (via `prompt.md`) to act as a detection engineering expert. You can request new detections using natural language, and it will:

1. Create a Sigma detection rule
2. Validate it for Sumo Logic compatibility
3. Provide a confidence rating
4. Show you the converted Sumo Logic query

## Requesting a Detection

### Simple Request Format

Just describe what you want to detect:

```
"Create a detection for [threat/behavior]"
```

### Examples

#### Example 1: Basic Request
```
You: Create a detection for PowerShell executing with encoded commands