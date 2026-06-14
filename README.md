# SEC Daily

## Design
An automated, monolith Python application to first focused to track and display insider trading (Form 4) and active investor acquisitions (Form 13D/G) directly from SEC EDGAR. 

## Functional 
- List all Form 4 and 13D/G filings
- Information including:
  - Date
  - Company
  - Person
  - Position
  - Total amount
  - Acquired/Sold
- Regularly fetch data from the SEC Edgar
- Shows the person buy/sold over time.

## Non-functional
- Unit testing
- E2E testing
- Integration testing
- CI/CD
- Rate limiting for scraping
- Zero-knowledge infrastructure with Docker secrets
- Database resiliency

## Tech 
- FastAPI
- Alembic
- Datastar
- Postgres
- Edgartools
- TailwindCSS
- PyTest
- Playwright
- GitHub Action

## Architecture
                  [  U.S. SEC EDGAR API  ]
                             │
                     (Asynchronous Ingestion via edgartools)
                             │
                             ▼
     ┌──────────────────────────────────────────────┐
     │         FastAPI Monolith Processing          │
     │  ┌──────────────────┐  ┌──────────────────┐  │
     │  │  Scraper Worker  │  │   App Router     │  │
     │  └────────┬─────────┘  └────────┬─────────┘  │
     └───────────┼─────────────────────┼────────────┘
                 │                     │
      (Alembic DB Migrations)    (Server-Sent Events)
                 │                     │
                 ▼                     ▼
       [ PostgreSQL Storage ]   [ Datastar HTML Frontend ]