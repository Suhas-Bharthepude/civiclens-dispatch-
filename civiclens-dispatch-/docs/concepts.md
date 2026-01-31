# REST API Concepts for CivicLens Dispatch

## What is an Endpoint?
An **endpoint** is a specific URL path on a server where clients can send requests to access or manipulate resources. Each endpoint represents a specific function or piece of data.

Example: `/incidents` is an endpoint for working with incident data.

## What is a Route?
A **route** is the mapping between a URL path (like `/incidents/{id}`) and the code that handles requests to that path. Routes define what happens when a client accesses an endpoint.

## HTTP Methods
Different methods tell the server what action to perform:

- **GET**: Retrieve data (read-only, no changes to server)
- **POST**: Create new data
- **PUT**: Update/replace existing data completely  
- **PATCH**: Update part of existing data
- **DELETE**: Remove data

## Status Codes
The server responds with numeric codes indicating the result:

- **200 OK**: Request succeeded
- **201 Created**: New resource successfully created
- **400 Bad Request**: Client sent invalid data
- **404 Not Found**: Resource doesn't exist
- **500 Internal Server Error**: Server encountered an error

## JSON Body
The **request body** contains data sent from client to server (usually in JSON format for APIs). The **response body** contains data sent back from server to client.

Example JSON:
```json
{
  "description": "Fire on Main St",
  "location": "123 Main St",
  "source": "citizen"
}
```

---

## CivicLens Dispatch Endpoints

### Core Incident Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/health` | Check if API is running |
| GET | `/incidents` | List all incidents (with filters) |
| POST | `/incidents` | Create new incident |
| GET | `/incidents/{id}` | Get specific incident details |
| PATCH | `/incidents/{id}` | Update incident fields |
| DELETE | `/incidents/{id}` | Delete incident |

### File Upload Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/incidents/{id}/audio` | Upload audio file for incident |
| POST | `/incidents/{id}/image` | Upload image for incident |

### Processing Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/incidents/{id}/process` | Trigger AI processing pipeline |

### Query Parameters Examples

- `GET /incidents?severity=high` - Filter by severity
- `GET /incidents?limit=10&offset=20` - Pagination
- `GET /incidents?source=citizen&sort_by=risk_score` - Filter and sort

---

## Request/Response Flow

1. Client sends HTTP request to endpoint
2. Server route handler receives request
3. Server validates data (if applicable)
4. Server performs business logic (database, AI, etc.)
5. Server returns HTTP response with status code and data



