# Architecture

## Overview
Our platform is built as a monolithic web service using **FastAPI**. It is designed to be completely offline and self-hostable, running in a single Docker container.

## Why FastAPI?
- **Speed**: Built on Starlette, it is one of the fastest Python frameworks available.
- **Simplicity**: Easy to read, self-documenting (Swagger UI out of the box).
- **Self-Hostable**: Can be easily packaged with Uvicorn in a lightweight Docker container without requiring external web servers like Nginx for basic workloads.

## Frontend
We opted for Server-Side Rendering (SSR) using **Jinja2** templates. This removes the need for a complex frontend build process (Webpack, NPM) while still allowing us to create a stunning, responsive, and modern UI using pure CSS.

## Storage
We use **SQLite**. As per the rules ("no hosted dependencies"), SQLite is the perfect choice for a zero-configuration, robust SQL database that lives entirely within a local file (`data.db`). We use **SQLAlchemy** as our ORM to interact with the database.

## Auth & Security
Authentication is handled via session cookies. Role isolation is strictly enforced at the API route level using dependency injection in FastAPI, ensuring that data leaking is impossible even if UI elements are bypassed.
