# Task 3: System Agent with API Integration - Implementation Plan

## Initial Benchmark Score
- Run 1: 3/10 passed
- Failures: Questions 4,5,6,7,8,9,10

## Overview
Add `query_api` tool to the existing agent from Task 2, allowing it to interact with the deployed backend.

## New Tool: query_api

### Purpose
Call the deployed backend API to get real system data (item counts, status codes, analytics).

### Parameters
- `method` (string): HTTP method (GET, POST, etc.)
- `path` (string): API endpoint path (e.g., "/items/", "/analytics/completion-rate")
- `body` (string, optional): JSON request body for POST requests

### Returns
JSON string with:
- `status_code`: HTTP status code
- `body`: Response body (parsed if JSON, raw string otherwise)

### Authentication
- Uses `LMS_API_KEY` from `.env.docker.secret`
- Added to request headers as `Authorization: Bearer <key>`

## Agent Updates

### 1. Load new environment variables
- `LMS_API_KEY` - backend authentication
- `AGENT_API_BASE_URL` - backend URL (default: http://localhost:42002)

### 2. Update tool definitions
Add `query_api` to existing `read_file` and `list_files` tools

### 3. Enhance system prompt
Instruct LLM when to use each tool:
- **read_file** - for wiki documentation or source code
- **list_files** - to discover files
- **query_api** - for live system data (item counts, status codes, analytics)

## Iteration Strategy

### Iteration 1: Basic API calls
- [ ] Fix question 4: "How many items are in the database?"
- [ ] Fix question 5: "What status code for /items/ without auth?"

### Iteration 2: Error handling
- [ ] Fix question 6: "lab-99 completion rate error"
- [ ] Fix question 7: "top-learners crash"

### Iteration 3: Multi-step reasoning
- [ ] Fix question 8: "HTTP request lifecycle" (read_file)
- [ ] Fix question 9: "ETL idempotency" (read_file)

## Challenges and Solutions

### Challenge 1: LLM doesn't use query_api
**Solution**: Improve tool description to be more specific about when to use it

### Challenge 2: Authentication errors
**Solution**: Ensure `LMS_API_KEY` is loaded and added to all requests

### Challenge 3: Large responses
**Solution**: Truncate large JSON responses to avoid token limits

## Testing Strategy

### New tests
1. **Framework question**: "What framework does the backend use?" → expects read_file
2. **Items count question**: "How many items in database?" → expects query_api

## Final Goal
Pass all 10 benchmark questions with correct tools and answers.