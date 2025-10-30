# Project Samarth: Intelligent Q&A System for Indian Agricultural and Climate Data

## Overview
Project Samarth is an end-to-end prototype of an intelligent question-answering (Q&A) system that sources live data from the Indian Government's [data.gov.in](https://data.gov.in) portal. The system integrates heterogeneous datasets from the Ministry of Agriculture & Farmers Welfare and the India Meteorological Department (IMD) to answer complex, natural language questions about the nation's agricultural economy and climate patterns. It aims to empower policymakers and researchers with cross-domain insights derived from real-time government data.

## Features
- Programmatic access to live datasets on crop production and climate indicators
- Intelligent natural language question parsing to identify query intent and parameters
- Dynamic querying and integration of multi-source data with cross-domain synthesis
- Source citations for every data-backed statement ensuring traceability and transparency
- Simple web-based chat interface to interact with the system and receive detailed answers

## System Architecture
1. **Data Ingestion & Normalization:**  
   - API calls and CSV downloads from data.gov.in  
   - Data cleaning and harmonization (region names, date formats, units)

2. **Backend Q&A Engine:**  
   - NLP-powered question parsing (entities, filters)  
   - Dynamic query generation across agriculture and climate datasets  
   - Result synthesis with source referencing

3. **Frontend Interface:**  
   - Minimal functional chat UI built with Streamlit/Flask (configurable)  
   - Displays user questions, detailed answers, and data source citations

## Getting Started

### Prerequisites
- Python 3.8+
- API key for data.gov.in (register and obtain from portal)
- Recommended: virtual environment for dependency management

### Installation

