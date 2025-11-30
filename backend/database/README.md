# Database Setup

This directory contains database schema and connection utilities.

## Setup Instructions

1. Ensure PostgreSQL is installed and running locally
2. Create the database:
   ```bash
   createdb -U postgres mydb
   ```
3. Run the schema script:
   ```bash
   psql -U postgres -d mydb -f schema.sql
   ```

## Database Connection

The application uses the following connection string format:
```
postgresql://postgres:lap@localhost:5432/mydb
```

This can be configured via the `DATABASE_URL` environment variable.

## Schema Overview

- **users**: Stores user account information
- **chat_messages**: Stores chat conversation messages
- **documents**: Stores document metadata and file information

All tables use UUID primary keys and include appropriate foreign key constraints and indexes for performance.

