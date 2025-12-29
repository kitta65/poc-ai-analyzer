# AI Analyzer

## About

AI Analyzer is a Proof of Concept (PoC) project. It automatically performs data retrieval, visualization, and provides insights based on natural language instructions for what you want to analyze.

## Architecture

The frontend is primarily implemented with Streamlit, the backend with Cube, and the data source with BigQuery.
As a PoC, the analysis target is limited to the BigQuery public dataset "theLook eCommerce" (`bigquery-public-data.thelook_ecommerce`).

The process flow is as follows:

1. The user provides natural language instructions for what they want to analyze.
2. The LLM generates a GraphQL Query to retrieve the necessary data from Cube's GraphQL API.
3. The retrieved data is converted into a DataFrame.
4. Based on the data's column names and the initial instructions, the LLM generates Vega-Lite configurations for visualization.
5. Visualization is performed in Streamlit via Altair.
