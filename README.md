# Project Management Dashboard

Designed and implemented a scalable backend system for project collaboration, featuring role-based access control, modular architecture (service/repository pattern), and AWS-based asynchronous document processing. The system emphasizes clean separation of concerns, testability, and real-world backend design practices.

---

## Table of Contents
- [Purpose](#purpose)
- [Demo](#demo)
- [Stack](#stack)
- [Features](#features)
- [Future Improvements](#future-improvements)
- [Installation](#installation)


---
## Purpose

This project was built to:

- Apply clean backend architecture principles
- Practice service/repository design patterns
- Work with relational data modeling
- Integrate cloud services (AWS)
- Build a production-style API system

---

## Demo
Swagger:
<img width="1047" height="1045" alt="image" src="https://github.com/user-attachments/assets/df430e87-7a2a-4667-9ec9-dfddf8d6cde4" />

Database model:
<img width="936" height="715" alt="database_model" src="https://github.com/user-attachments/assets/5d646c0c-cb4d-4890-9a58-fa59596c4a1b" />

---

## Stack
- Python
- FastAPI
- Pydantic
- PostgreSQL + SQLAlchemy
- Docker + Makefile
- AWSS3
- AWS Lambda functions
- Pytest


---

## Features
🔐 Authentication & Security
- Secure user authentication with hashed passwords
- JWT-based authentication for stateless session management
- Structured authentication flow with clear separation of concerns

👥 Project Collaboration & Access Control
- Multi-user project management system
- Role-based access model via project membership (ProjectUser)
- Support for assigning different roles to users within projects

📁 Project & Document Management
- Full CRUD operations for projects and associated documents
- Document-to-project association with relational integrity
- Scalable handling of multiple documents per project

☁️ Cloud File Storage & Processing
- Integration with AWS S3 for reliable and scalable document storage
- Asynchronous document processing using AWS Lambda
- Separation of file storage (cloud) from application data (database)

🧱 Backend Architecture & Design
- Layered architecture (API → Service → Repository → Database)
- Service layer encapsulating business logic
- Repository pattern for clean data access abstraction
- Modular and maintainable codebase structure

🗄 Database & Data Modeling
- Relational database design with normalized schema
- Many-to-many relationship between users and projects with roles
- Explicit SQL schema and indexing for performance optimization
- SQLAlchemy integration for ORM-based data handling

🧪 Testing & Reliability
- Automated test suite using pytest
- Testable architecture with isolated service and repository layers
- Coverage of core business logic and API endpoints

📦 DevOps & Environment
- Dockerized application and database setup
- Reproducible development environment using Docker Compose
- Environment-based configuration support

---

## Future improvements
- Role-based access control (permissions layer, not just roles)
- JWT refresh tokens / session management
- Increased test coverage
- CI/CD pipeline
- Analytics & reporting endpoints
- Extended API documentation

---



## Installation
Clone repo
```bash
git clone https://github.com/lukas5555510/Project-Management-Dashboard.git
```
```bash
cd Project-Management-Dashboard/
```
add .env file following
```
POSTGRES_USER=user_name
POSTGRES_PASSWORD=password
POSTGRES_HOST=db
POSTGRES_PORT=5432
POSTGRES_DB=db_name
AWS_ACCESS_KEY_ID=aws_access_key
AWS_SECRET_ACCESS_KEY=aws_sercret_key
AWS_REGION=aws_region
S3_BUCKET_NAME=s3_bucket_name
JWT_ALGORITHM=HS256
JWT_SECRET_KEY=jwt_secret_key
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
```
build containers
```bash
make build
```
start application
```bash
make up
```
u can also check logs
```bash
make logs
```
