# MSF Field Operations Data Platform

## Hybrid ETL + ELT Architecture Analysis

---

# Executive Summary

Médecins Sans Frontières (MSF) operates humanitarian healthcare missions across 70+ countries and requires a centralized cloud-based analytics platform to consolidate operational data from more than 400 field sites worldwide.

The organization receives operational data including patient intake forms, outbreak reports, drug inventory logs, and staffing records through daily CSV uploads from remote field locations.

After analyzing the infrastructure constraints, security requirements, data inconsistencies, and analytics needs, the recommended solution is a **Hybrid ETL + ELT Architecture** using Google BigQuery and cloud-native analytics services.

The architecture combines:

* ETL for secure preprocessing and anonymization
* ELT for scalable cloud analytics and flexible reporting

This hybrid approach provides both secure healthcare data handling and modern scalable analytics capabilities.

---

# 1. Problem Statement

MSF wants to build a centralized analytics platform that can collect, standardize, secure, and analyze operational healthcare data from 400 field clinics and humanitarian sites globally.

The platform must support:

* Patient intake records
* Drug inventory management
* Disease outbreak reporting
* Staff deployment tracking
* Operational analytics and forecasting

The Geneva headquarters analytics team requires consolidated, reliable, and queryable datasets for decision-making and emergency response planning.

---

# 2. Key Constraints Analysis

## A) Infrastructure Constraints

* Field sites have intermittent internet connectivity.
* Most locations upload data through daily batch CSV files.
* Real-time streaming is not feasible.
* MSF infrastructure already uses Google Cloud / BigQuery.

### Impact

A batch-oriented cloud analytics architecture is more practical than a real-time streaming pipeline.

---

## B) Sensitive Healthcare Data

Patient records contain sensitive information such as:

* Patient names
* Age details
* Diagnoses
* GPS treatment coordinates

### Impact

Sensitive healthcare data must be anonymized and validated before it enters the centralized analytics platform.

This creates a strong requirement for an ETL preprocessing layer.

---

## C) Analytics Requirements

MSF analysts require:

* Ad-hoc analytical queries
* Outbreak trend analysis
* Drug forecasting
* Staffing analysis
* Flexible reporting

Requirements evolve continuously and there is no fixed reporting schema.

### Impact

Flexible cloud-based ELT transformations are required for analytics.

---

## D) Data Format Inconsistency

Data arrives from 400 sites with:

* Different CSV structures
* Different column names
* Different date formats
* Local language labels

### Impact

Data normalization and standardization are required before analytics processing.

---

## E) Latency Requirements

Operational requirements indicate:

* 24-hour reporting delay is acceptable
* Weekly forecasting is acceptable
* No use case requires sub-second latency

### Impact

A batch ETL pipeline is fully sufficient.

---

# 3. Architecture Options Evaluation

## Option 1 — Pure Streaming ETL Architecture

### Characteristics

* Real-time stream processing
* Continuous event transformation
* Complex infrastructure clusters

### Advantages

* Real-time dashboard updates
* Live telemetry processing

### Disadvantages for MSF

* Unnecessary infrastructure complexity
* Higher operational cost
* Difficult maintenance
* Not suitable for unstable connectivity
* Real-time processing is unnecessary

### Conclusion

Not recommended for MSF healthcare operations.

---

## Option 2 — Pure ELT Architecture

### Characteristics

* Raw data loaded directly into warehouse
* Transformations occur after loading
* Flexible SQL/dbt transformations

### Advantages

* Flexible analytics
* Easy schema evolution
* Raw data preservation

### Disadvantages for MSF

* Sensitive patient data would enter warehouse before masking
* Governance risks for healthcare information

### Conclusion

Pure ELT alone is not ideal for sensitive healthcare datasets.

---

## Option 3 — Hybrid ETL + ELT Architecture

### Characteristics

* Initial ETL preprocessing layer
* Secure anonymization before loading
* ELT analytics transformations after loading

### Advantages

* Secure healthcare data handling
* Flexible analytics capabilities
* Lower cloud infrastructure complexity
* Better governance and compliance
* Scalable cloud analytics
* Easier schema evolution

### Conclusion

Best architectural fit for MSF requirements.

---

# 4. Final Architecture Decision

## Recommended Solution

MSF should implement a **Hybrid ETL + ELT cloud architecture** using Google BigQuery.

### ETL Layer Responsibilities

* Data validation
* Schema normalization
* Data cleaning
* Patient data anonymization
* Sensitive information masking

### ELT Layer Responsibilities

* Cloud-based SQL transformations
* Flexible reporting
* Forecasting models
* Analytics-ready datasets
* Ad-hoc query support

This hybrid model balances healthcare security requirements with modern cloud analytics flexibility.

---

# 5. Proposed Data Pipeline

```text
FIELD CLINICS / FIELD SITES
            ↓
 DAILY CSV BATCH FILES
            ↓
 ETL PREPROCESSING PIPELINE
            ↓
VALIDATION + STANDARDIZATION + MASKING
            ↓
 CLOUD STORAGE / BIGQUERY
            ↓
 RAW & STAGING TABLES
            ↓
 ELT SQL TRANSFORMATIONS
            ↓
 ANALYTICS-READY DATASETS
            ↓
DASHBOARDS / REPORTING / ANALYTICS
```

---

# 6. Medallion Data Architecture

## Bronze Layer — Raw Data

### Purpose

* Store uploaded batch files
* Preserve historical raw data
* Maintain replayability and auditing

---

## Silver Layer — Cleaned Data

### Purpose

* Standardize schemas
* Normalize formats
* Remove duplicates
* Validate records
* Apply anonymization rules

---

## Gold Layer — Analytics Datasets

### Purpose

* Reporting dashboards
* Forecasting datasets
* Operational KPIs
* Business analytics

---

# 7. Security & Governance Strategy

Because the system contains highly sensitive healthcare data, strong security controls are mandatory.

## Recommended Controls

* Patient data anonymization
* PII masking
* Role-based access control (RBAC)
* Audit logging
* Encryption at rest and in transit
* Secure cloud storage
* Governance and compliance policies

### Important Requirement

Sensitive patient identifiers should never appear directly inside analytics dashboards or reports.

---

# 8. Data Quality & Monitoring

The architecture should include operational monitoring and data quality validation mechanisms.

## Recommended Capabilities

* Failed file detection
* Schema validation
* Missing column checks
* Duplicate detection
* Data freshness monitoring
* ETL job logging
* Pipeline execution tracking

### Benefits

Improves operational reliability, trust, and auditability.

---

# 9. Scalability Strategy

The proposed hybrid cloud architecture is highly scalable.

## Scalability Benefits

* Easy onboarding of additional field sites
* Elastic BigQuery compute scaling
* Independent compute and storage scaling
* Reusable transformation models
* Efficient batch processing

The platform can easily expand beyond 400 global field locations.

---

# 10. Recommended Technology Stack

| Component                 | Technology                  |
| ------------------------- | --------------------------- |
| Data Warehouse            | Google BigQuery             |
| Raw File Storage          | Google Cloud Storage        |
| ETL Processing            | Python / Apache Airflow     |
| Transformation Layer      | dbt                         |
| Analytics & Visualization | Looker / Tableau / Power BI |
| Monitoring & Logging      | Google Cloud Monitoring     |

---

# 11. Future Enhancements

Potential future improvements include:

* Machine learning outbreak prediction
* Geospatial disease analytics
* Automated anomaly detection
* Near real-time emergency alerts
* Predictive drug inventory forecasting
* Mobile data collection integration

These enhancements can be implemented without redesigning the core architecture.

---

# 12. Final Conclusion

MSF should implement a **Hybrid ETL + ELT cloud architecture** for its global healthcare analytics platform.

An initial ETL layer should anonymize, validate, and standardize sensitive healthcare data before loading it into BigQuery.

After loading, ELT-style SQL/dbt transformations can support flexible analytics, forecasting, reporting, and schema evolution.

This hybrid approach provides:

* Secure healthcare data processing
* Flexible cloud analytics
* Lower operational complexity
* Better scalability
* Easier governance
* Cost-efficient cloud infrastructure

The proposed solution is practical, scalable, secure, and strongly aligned with MSF operational requirements.

---

# End of Report
