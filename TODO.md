# TODO

## Stage 1

- [x] Dockerfile
- [x] docker-compose
- [ ] Use edgartool to get fillings
- [ ] Implement FastScheduler
- [x] Set up FastAPI server
- [ ] Set up Datastar categorized table by filing types
- [ ] Deploy to dockerhub
- [ ] Deploy to Hetzner
- [ ] GitHub Actions for CI/CD

## Stage 2

- [ ] Ansible
- [ ] Nginx
- [ ] Grafana
- [ ] Prometheus

Here is your consolidated **SEC Tracker Project Plan**. This README is designed to look like a professional SRE/QA portfolio piece, combining your technical goals with a realistic "Mise-en-Place" execution schedule.

# 📈 SEC Tracker: Real-Time Disclosure Engine

**Objective:** Build a production-grade disclosure tracker that scrapes the SEC EDGAR database every 15 minutes, stores filings in PostgreSQL, and streams updates to a real-time dashboard using FastAPI and Datastar.

---

## 🛠 Tech Stack (The SRE Toolkit)

- **Backend:** Python 3.12+ (managed by `uv`) & FastAPI
- **Database:** PostgreSQL (with SQLModel ORM)
- **Frontend:** Datastar (Hypermedia-driven real-time UI)
- **Task Engine:** FastScheduler (Internal Cron)
- **Infrastructure:** Docker & Docker Compose
- **Observability:** Prometheus & Grafana (Stage 1: Containerized)
- **CI/CD:** GitHub Actions (Automated Linting & Deployment)

---

## ⏳ Execution Timetable (18-Hour Sprint)

### **Phase 1: The Infrastructure (4 Hours)**

- **Goal:** Establish the "Kitchen." Get the environment and database ready.
- **Tasks:**
  - Initialize project with `uv init`.
  - Create `docker-compose.yml` defining the FastAPI app and Postgres container.
  - Configure `SQLModel` for async database connections.
  - Implement **Docker Healthchecks** to ensure the app waits for the DB.

### **Phase 2: The Scraper Engine (5 Hours)**

- **Goal:** The "Heart & Lungs." Reliable data ingestion.
- **Tasks:**
  - Integrate `edgartools` to pull the latest 10-K and Form 144 filings.
  - Implement rate-limiting logic (SEC allows max 10 requests/second).
  - Build the "Upsert" logic to prevent duplicate entries in Postgres.
  - Set up `FastScheduler` to trigger the scrape every 15 minutes.

### **Phase 3: The Live UI (5 Hours)**

- **Goal:** The "Service." A modern, reactive experience.
- **Tasks:**
  - Build Jinja2 templates for the dashboard.
  - Implement **Datastar** Server-Sent Events (SSE) to "push" new filings to the browser.
  - Create a "Search/Filter" fragment to sort by Ticker or Filing Type.
  - Style with a minimalist CSS framework (e.g., Tailwind or Simple.css).

### **Phase 4: Deployment & Defense (4 Hours)**

- **Goal:** The "Delivery." Public access and monitoring.
- **Tasks:**
  - Provision **Hetzner VPS** and install Tailscale for secure access.
  - Configure **GitHub Actions** to build the Docker image and deploy on `git push`.
  - Plug in the **Prometheus/Grafana** sidecars to monitor RAM and Scraping success.
  - Final "Project Sentinel" QA audit: Ensure no ghost logs or dependency drift.

---

## 🚀 SRE Portfolio Highlights

- **Observability:** Real-time monitoring of scraper health via Grafana.
- **Resilience:** Graceful handling of SEC connection timeouts and database retries.
- **Portability:** Fully containerized—can move from Hetzner to Home Lab in minutes using `rsync` over Tailscale.
- **Automation:** Zero-touch deployments via GitHub Actions.

---

## 📋 Getting Started (Local Dev)

1.  **Clone:** `git clone ...`
2.  **Environment:** Copy `.env.example` to `.env` and add SEC contact info.
3.  **Launch:** `docker compose up --build`
4.  **View:** Visit `localhost:8000` to see the live stream.
