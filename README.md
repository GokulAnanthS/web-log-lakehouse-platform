# Enterprise-Grade Web Log Intelligence Lakehouse Platform

An end-to-end, production-style data platform that ingests large-scale web server logs, processes them using a Delta Lake-based lakehouse, enables advanced analytics through Snowflake and dbt, applies machine learning for bot detection and anomaly detection, and delivers insights via Power BI, with full observability and CI/CD.

Project Difficulty: 9/10  
Architecture Style: Hybrid Cloud Lakehouse + Warehouse

---

## 1. Problem Statement

Web server logs contain valuable information about:
- User behavior
- Bot activity
- Traffic anomalies
- System performance
- Security signals

However, raw logs are:
- Unstructured
- Extremely large
- Hard to analyze directly

This project builds a **production-grade data platform** that:
- Converts raw logs into analytics-ready datasets
- Supports machine learning use cases
- Enables real-time observability
- Follows modern data engineering best practices

---

## 2. High-Level Architecture

Raw Logs (Kaggle)
|
v
AWS S3 (Delta Lake - Bronze)
|
Spark (AWS Glue / EMR)
|
AWS S3 (Delta Lake - Silver / Gold)
|
Snowflake (Warehouse)
|
dbt (Analytics Models)
|
Power BI (Dashboards)

ML Pipelines:
Delta Gold → ML Training → MLflow (Tracking & Registry)

Orchestration:
Airflow (Docker, Local)

Monitoring:
Prometheus → Grafana

CI/CD:
GitHub Actions → Validation & Deployment


---

## 3. Technology Stack

| Layer | Tools |
|------|------|
Orchestration | Apache Airflow |
Lakehouse | AWS S3 + Delta Lake |
Processing | Apache Spark, DuckDB |
Warehouse | Snowflake |
Transformations | dbt |
ML | Scikit-learn |
ML Tracking | MLflow |
BI | Power BI |
Monitoring | Prometheus, Grafana |
DevOps | Docker, Git, CI/CD |
Cloud | AWS (Hybrid usage model) |

---

## 4. Lakehouse Design

We follow a Medallion Architecture:

### Bronze (Raw)
- Raw log files
- Immutable
- Stored as Delta tables
- Minimal transformation

### Silver (Structured)
- Parsed fields
- Clean schema
- Enriched with:
  - GeoIP
  - Device info
  - Bot flags
  - URL decoding

### Gold (Business)
- Analytics-ready tables
- Fact and dimension modeling
- Optimized for Snowflake ingestion and BI usage

---

## 5. Data Warehouse Design (Snowflake)

Star Schema:
- FactWebTraffic
- DimDate
- DimIP
- DimDevice
- DimGeo
- DimBot
- DimURL

Optimized for:
- BI dashboards
- ML feature extraction
- Analytical queries

---

## 6. Machine Learning Scope

1. Bot Detection
   - Classify traffic into:
     - Human
     - Search bots
     - Scrapers
     - Malicious patterns

2. Anomaly Detection
   - Detect:
     - Traffic spikes
     - Crawling attacks
     - System abuse

3. User Behavior Clustering
   - Segment traffic by usage patterns

MLflow is used for:
- Experiment tracking
- Model versioning
- Reproducibility

---

## 7. Observability

Prometheus collects:
- Airflow DAG metrics
- Job runtime
- Data freshness

Grafana displays:
- Pipeline health
- SLA violations
- Processing latency
- System stability

---

## 8. DevOps & CI/CD

- Dockerized services:
  - Airflow
  - MLflow
  - Prometheus
  - Grafana

- Git-based workflow:
  - Feature branches
  - Clean commits

- CI/CD:
  - DAG validation
  - dbt tests
  - Unit tests
  - Linting

---

## 9. Execution Strategy

Hybrid AWS model:
- AWS handles:
  - S3 storage
  - Spark processing
  - Delta Lake
  - Snowflake integration

- Local machine handles:
  - Airflow
  - MLflow
  - Monitoring
  - Development & testing

This balances:
- Cost efficiency
- Real-world cloud exposure
- Developer productivity

---

## 10. Learning Outcomes

This project demonstrates:
- End-to-end data platform design
- Lakehouse + Warehouse integration
- Analytics engineering with dbt
- MLOps fundamentals
- Observability for data pipelines
- Production-grade DevOps practices
