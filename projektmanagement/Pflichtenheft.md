| Ausgangslage | There are no tools that unify different website recon techniques, intel is scattered around different tools                                                                                                      |
| --- |------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Ist Zustand | Postman, Burpsuite, mitmproxy, and other Tools only store HTTP Endpoints and not the entire infrastructure                                                                                                       |
| Zielsetzung | Easy website analysis even if one does not have previous knowledge of http or web technologies<br>HAR analysis completed in under 5 seconds for files up to 10 MB<br>Uptime < 99%<br>Login only via school email |
| Anforderung | See below                                                                                                                                                                                                        |
| UI-Konzept | UI Concept is located in design_concept folder                                                                                                                                                                   |
| Lieferobjekte | Prototype is to be considered approved if FA01-FA06 are completed                                                                                                                                                |

## Funktionale Anforderungen

| ID | Anforderung |
| --- | --- |
| FA01 | Register and login with school email |
| FA02 | User account management (change password) |
| FA03 | Manage projects (create + update [upload har files + target url]) |
| FA04 | Ability to start website analysis  (dns, tech stack fingerprinting, endpoints mapping, SSL/TLS certificate check) |
| FA05 | Ability ot save the result or get old one |
| FA06 | Global error handling + logging |

## Nicht-funktionale Anforderungen

| ID | Anforderungen |
| --- | --- |
| NA01 | HAR analysis completed in under 5 seconds for files up to 10 MB |
| NA02 | Uptime < 99% |
| NA03 | Login only via school email (Firstname.Lastname@htlstp.at) |
| NA04 | 90% test coverage for backend logic and api endpoints (unit + integration) |
| NA05 | Deployment using docker compose and nginx |
| NA06 | Complete documentation (openAPI, er diagramm, how to start) |

# Technische Doku

| Architecture | FastAPI Pydantic SQLAlchemy websockets Pytest Angular nginx |
| --- | --- |
| Data Catalog | Will be delivered later on |
| ER Diagram | Will be delivered later on |
| API Documentation | See below |
| Setup | Simple Setup is possible using one command (docker compose) |

## API Documentation

Base URL: https://…/api/

| **Method** | **URL** | **Description** |
| --- | --- | --- |
| POST | /auth/register |  |
| POST | /auth/code/submit | Submit Code from email |
| POST | /auth/login | Login using email + password |
| PATCH | /auth/me | Update User password |
|  |  |  |
| GET | /me | Fetch User Projects |
| POST | /projects | Create Project |
| POST | /projects/{id}/upload | Upload .har |
| GET | /projects/{id} | Get projet info + data of all categories |
| PATCH | /projects/{id} | Update project (name, domain) |
| POST | /projects/{id}/analysis/start | Start user-triggered analysis |
|  |  |  |
|  | ws://category/{id} | Live updates about analysis |