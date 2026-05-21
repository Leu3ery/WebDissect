## Overview

| Section | Content |
| --- | --- |
| **Current Situation** | There are no tools that unify different website recon techniques; intel is scattered across different tools |
| **Current State** | Postman, Burpsuite, mitmproxy, and other tools only store HTTP endpoints and not the entire infrastructure |
| **Objectives** | Easy website analysis even without prior knowledge of HTTP or web technologies<br>HAR analysis completed in under 5 seconds for files up to 10 MB<br>Uptime > 90%<br>Login only via school email |
| **Requirements** | See below |
| **UI Concept** | UI concept is located in the design_concept folder |
| **Deliverables** | Prototype is considered approved if FA01–FA06 are completed |

## Functional Requirements

| ID | Requirement |
| --- | --- |
| FA01 | Register and login with school email |
| FA02 | User account management (change password) |
| FA03 | Manage projects (create + update [upload HAR files + target URL]) |
| FA04 | Ability to start website analysis (DNS, tech stack fingerprinting, endpoints mapping, SSL/TLS certificate check) |
| FA05 | Ability to save results or retrieve previous ones |
| FA06 | Global error handling + logging |

## Non-Functional Requirements

| ID | Requirement |
| --- | --- |
| NA01 | HAR analysis completed in under 5 seconds for files up to 10 MB |
| NA02 | Uptime > 99% |
| NA03 | Login only via school email (Firstname.Lastname@htlstp.at) |
| NA04 | 90% test coverage for backend logic and API endpoints (unit + integration) |
| NA05 | Deployment using Docker Compose and nginx |
| NA06 | Complete documentation (OpenAPI, ER diagram, setup guide) |

# Technical Documentation

| Section | Content |
| --- | --- |
| **Architecture** | FastAPI, Pydantic, SQLAlchemy, WebSockets, Pytest, Angular, nginx |
| **Data Catalog** | See below |
| **ER Diagram** | Will be delivered later |
| **API Documentation** | See below |
| **Setup** | Single-command setup via Docker Compose |

## API Documentation

Base URL: `https://…/api/`

| Method | URL | Description |
| --- | --- | --- |
| POST | /auth/register | Register a new user |
| POST | /auth/code/submit | Submit OTP code from email |
| POST | /auth/login | Login using email + password |
| PATCH | /auth/me | Update user password |
|  |  |  |
| GET | /me | Fetch user projects |
| POST | /projects | Create project |
| POST | /projects/{id}/upload | Upload .har file |
| GET | /projects/{id} | Get project info + data for all categories |
| PATCH | /projects/{id} | Update project (name, domain) |
| POST | /projects/{id}/analysis/start | Start user-triggered analysis |
|  |  |  |
| WS | ws://category/{id} | Live updates about analysis progress |


## Datacatalog

### users

| Attribute | Type | Constraints |
| --- | --- | --- |
| id | INT | PK |
| email | NVARCHAR(100) | NOT NULL UNIQUE |
| password_hash | NVARCHAR(200) | NOT NULL |
| created_at | DATETIME | NOT NULL |

### pending_verifications

| Attribute | Type | Constraints |
| --- | --- | --- |
| id | INT | PK |
| email | NVARCHAR(100) | NOT NULL UNIQUE |
| code | VARCHAR(6) (TODO INT?) | NOT NULL |
| expires_at | DATETIME | NOT NULL |
| attempts | INT | NOT NULL DEFAULT 0 |

### projects

| Attribute | Type | Constraints |
| --- | --- | --- |
| id | INT | PK |
| name | NVARCHAR(30) | NOT NULL |
| domain | NVARCHAR(253) | NOT NULL |
| user | INT | FK (user.id) |

### har_files

| Attribute | Type | Constraints |
| --- | --- | --- |
| id | INT | PK |
| filename | NVARCHAR(30) | NOT NULL |

### project_hars (junction table)

| Attribute | Type | Constraints |
| --- | --- | --- |
| project_id | INT | FK project(id) |
| har_id | INT | FK har_file(id) |

### Certificate

| Attribute | Type | Constraints |
| --- | --- | --- |
| id | INT | PK |
| subject_domain | NVARCHAR(253) | NOT NULL |
| subject_organization | NVARCHAR(64) | NOT NULL |
| subject_country | CHAR(2) |  |
| issuer_name | NVARCHAR(253) | NOT NULL |
| issuer_organization | NVARCHAR(64) |  |
| issuer_country | CHAR(2) |  |
| valid_from | DATETIME | NOT NULL |
| valid_to | DATETIME | NOT NULL |
| serial_number | VARCHAR(40) | NOT NULL |
| public_key_type | VARCHAR(10) | NOT NULL |
| fingerprint_sha256 | CHAR(64) | NOT NULL, UNIQUE |

### dns_entries

| Attribute | Type | Constraints |
| --- | --- | --- |
| id | INT | PK |
| type | NVARCHAR(4) | CHECK (type in (A, AAAA, MX, NS, TXT)) |
| domain | NVARCHAR(253) | NOT NULL |
| value | NVARCHAR(253) | NOT NULL |
| ttl | int | NOT NULL, CHECK (ttl > 0) |

### technologies

| Attribute | Type | Constraints |
| --- | --- | --- |
| id | INT | PK |
| name | VARCHAR(100) | NOT NULL |
| description | VARCHAR(100) | NULL |
| icon_url | VARCHAR(100) | NULL |

### endpoints

| Attribute | Type | Constraints |
| --- | --- | --- |
| id | INT | PK |
| method | VARCHAR(10) | CHECK (method IN (GET, POST, PUT, DELETE)) NOT NULL |
| path | VARCHAR(200) | NOT NULL |
| status | INT | CHECK (status < 600 & status >100) NOT NULL |
| content_type | VARCHAR(100) | NOT NULL |