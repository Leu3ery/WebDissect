## Requirements

1. Register and login with school email (via verification code to @htlstp.at)
2. User account management (change password)
3. Manage projects (create + update [upload HAR files + target URL])
4. Ability to start website analysis and save results or retrieve previous ones (DNS, tech stack fingerprinting, endpoints mapping, SSL/TLS certificate check)
5. 90% test coverage for backend logic and API endpoints (unit + integration)
6. Complete documentation (OpenAPI, ER diagram, setup guide)
7. Global error handling + logging
8. Deployment using Docker Compose and nginx

## Effort Estimate (T-Shirt Size Method)

### Size Reference

| Size | Meaning                                        | Hours |
|------|------------------------------------------------|-------|
| XS   | Trivial, no notable risk                       | 1     |
| S    | Straightforward, known solution                | 1.5-2 |
| M    | Normal effort, little unknown                  | 3–4   |
| L    | Complex, unknown, or much coordination needed  | 6–10  |
| XL   | Very large — must be split up                  | —     |


## Effort Estimate

| ID | Requirement | Size | Effort (h) |
| --- | --- | - | --- |
| FA01 | Register and login with school email (via verification code to @htlstp.at) | M | 4 |
| FA02 | User account management (change password) | S | 1.5 |
| FA03 | Manage projects (create + update [upload HAR files + target URL]) | M | 3 |
| FA04 | Ability to start website analysis and save results or retrieve previous ones (DNS, tech stack fingerprinting, endpoints mapping, SSL/TLS certificate check) | L | 10 |
| FA05 | 90% test coverage for backend logic and API endpoints (unit + integration) | M | 3 |
| FA06 | Complete documentation (OpenAPI, ER diagram, setup guide) | M | 3 |
| FA07 | Global error handling + logging | S | 1.5 |
| FA08 | Deployment using Docker Compose and nginx | M | 4 |

**Total: 30h**
Available in school: 42 man-hours