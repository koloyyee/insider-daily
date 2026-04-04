# SEC Daily

## Functional MVP + SRE Upgrade

- Scrape 10-K/Q and Form 144 filings from the SEC’s EDGAR database every 15 minutes.
- Store metadata (Ticker, Form Type, Date, Accession Number) in a Postgres
- Display the filings in a simple web UI with real-time updates using Server-Sent Events (SSE).
- Categorize filings by ticker and form type, and allow users to filter and search through the filings.

---

### **Stage 1: The "Functinal MVP" (Focus: Docker)**

_Goal: Get the scraper, database, and UI running on Hetzner as a single cohesive unit._

- **Frontend:** **Datastar + Tailwind.** Use Datastar’s Server-Sent Events (SSE) to "push" new filings to the UI instantly as they are scraped.
- **Backend:** **FastAPI + FastScheduler.** FastScheduler will handle the 15-minute intervals to check for new 10-K/Q and Form 144 filings using `edgartools`.
- **Database:** **Postgres.** Store filing metadata (Ticker, Form Type, Date, Accession Number).
- **Infrastructure:** **Docker Compose.**
  - `app` container (FastAPI)
  - `db` container (Postgres)
  - `proxy` container (Nginx)

---

### **Stage 2: The "SRE Upgrade" (Focus: Ansible & Observability)**

_Goal: Move from "manual setup" to "Infrastructure as Code" and professional monitoring._

#### **Part A: Automation with Ansible**

Instead of SSHing into Hetzner to run `docker-compose up`, you will write an **Ansible Playbook**.

- **Task 1:** Provision the Debian server (Install Docker, set up `UFW` firewall, create a sudo user).
- **Task 2:** Copy your project files and `.env` secrets to the server.
- **Task 3:** Deploy the Docker stack and ensure it restarts automatically if the server reboots.

#### **Part B: Monitoring with Prometheus & Grafana**

You will add "The Watchers" to your `docker-compose.yml` to monitor your Postgres health and scraping performance.

- **Postgres Exporter:** A tiny sidecar container that reads Postgres metrics and sends them to Prometheus.
- **Prometheus:** The "time-series database" that stores your metrics (e.g., "How many filings did I scrape in the last hour?").
- **Grafana:** The dashboard. You’ll use a pre-built **Postgres Dashboard (ID: 9628)** to see things like:
  - Active DB connections.
  - Scraper latency (how long the SEC takes to respond).
  - Disk usage for your filing data.

---

Gemini conversation: <https://gemini.google.com/app/b50e049218a9bc31>
