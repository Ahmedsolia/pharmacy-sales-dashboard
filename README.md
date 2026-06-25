<img width="1747" height="870" alt="image" src="https://github.com/user-attachments/assets/4000b9b3-1a83-46f6-a9c7-7b37db2e8691" /># 💊 Pharmaceutical Sales & Analytics Dashboard

![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-2C2D72?style=for-the-badge&logo=pandas&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)

An end-to-end data analytics and business intelligence project focused on pharmaceutical sales. This repository contains the complete pipeline: from raw data assessment and entity resolution to predictive modeling and an interactive, Arabic-supported interactive web dashboard.

---

## 📑 Table of Contents
1. [Project Overview](#-project-overview)
2. [Key Features](#-key-features)
3. [Project Architecture & Data Pipeline](#-project-architecture--data-pipeline)
4. [Tech Stack](#-tech-stack)
5. [Local Installation & Setup](#-local-installation--setup)
6. [Repository Structure](#-repository-structure)

---

## 📊 Project Overview
Pharmaceutical sales data is often fragmented across different suppliers, warehouses, and regions. This project resolves common data quality issues (like misspelled sales representative names, inconsistent pharmacy names, and missing regions) to create a single source of truth. 

The final output is a **Streamlit Dashboard** that allows stakeholders to dynamically filter sales data by region, analyze supplier performance, track top-selling products, and evaluate the precise revenue impact of individual pharmacies.

---

## ✨ Key Features
* **Interactive Filtering:** Slice the data dynamically by geographical regions (Greater Cairo, Alexandria, Delta, etc.).
* **Entity Resolution Proof:** A dedicated section demonstrating the impact of data unification, comparing fragmented raw data (`user_name`) vs. clean canonical data (`employee_name`).
* **Pharmacy-Supplier Breakdown:** Visualizes the revenue contribution of the Top 10 pharmacies globally, alongside a breakdown of sales per warehouse.
* **Native Arabic UI/UX:** Fully integrated support for Arabic text visualization inside charts using `arabic-reshaper` and `python-bidi`.
* **High-Level KPIs:** Instant metrics for Total Revenue, Unique Invoices, Total Products, and Customer Count.

---

## 🏗️ Project Architecture & Data Pipeline

The development of this dashboard was preceded by extensive data engineering and modeling phases, documented in the included Jupyter Notebooks:

1. **`Assessment.ipynb`**: Initial exploration of the raw data. Implemented intelligent functions to unify pharmacy names and addresses based on the most frequent values (Mode) tied to `Global_Account_ID`s.
2. **`phase3_data_linking_modeling.ipynb`**: Handled Entity Resolution and constructed a clean **Star-Schema** data model (Fact table for sales, Dimension tables for customers, products, sales reps, geography, and suppliers).
3. **`pharmacy_analysis.ipynb`**: A deep-dive analytical report calculating invoice attribution and supplier reliance, revealing that the top 10 pharmacies account for a massive percentage of total portfolio revenue.
4. **`Modeling_and_Analytics.ipynb`**: Explored relationships via pivot tables and heatmaps to map pharmacy revenue distributions across specific suppliers.
5. **`demand_prediction_clean.ipynb`**: A machine learning pipeline featuring a `RandomForestRegressor` with time-aware splitting to predict future pharmacy demand accurately without data leakage.

---

## 💻 Tech Stack
* **Frontend / App Framework:** Streamlit
* **Data Manipulation:** Pandas, NumPy
* **Data Visualization:** Matplotlib, Seaborn
* **Language Processing:** `arabic-reshaper`, `python-bidi` (for Right-to-Left Arabic text rendering in plots)
* **Machine Learning:** Scikit-Learn

  ![Dashboard Preview]<img width="1747" height="870" alt="Screenshot 2026-06-25 185447" src="https://github.com/user-attachments/assets/8f898729-3eaf-48db-894e-b109fe2d078f" />

