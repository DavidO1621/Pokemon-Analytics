Pokémon Team Analyzer: A Data-Driven Decision Support System
This project is a full-stack analytical application designed to mitigate strategic risk in competitive team building. It transforms raw, external API data into actionable, quantitative insights, demonstrating end-to-end proficiency in data engineering, statistical modeling, and interactive visualization.

Project Overview
The Pokémon Team Analyzer provides users with a comprehensive breakdown of team composition, including statistical benchmarking of individual Pokémon and an aggregated analysis of shared type vulnerabilities. This tool provides an objective, data-backed foundation for strategic optimization, moving beyond anecdotal observation into quantifiable performance metrics.

Technical Deep Dive: The Data Pipeline
The application's core strength lies in its robust data handling and analytical workflow:

1. High-Performance ELT & Data Ingestion
Asynchronous Processing: Engineered a high-efficiency ELT (Extract, Load, Transform) pipeline. Data acquisition uses aiohttp asynchronous fetching against the RESTful Pokémon API, significantly reducing latency when ingesting large, generation-wide datasets.

Data Normalization: Raw JSON data is systematically cleaned and structured into analytical models using Pandas DataFrames, preparing the data for vectorized computations.

2. Statistical Benchmarking & Cohort Analysis
Rigorous Modeling: Established the analytical core by performing complex descriptive statistics (μ, σ) on entire Pokémon populations.

Actionable Metrics: Leveraged SciPy-driven Z-score analysis to accurately benchmark individual Pokémon stats. This calculation provides users with an actionable percentile rank, objectively quantifying performance against chosen historical cohorts (Generations), which can be interpreted as a time-series analysis of stat growth trends.

3. Decision-Support Aggregation
Categorical Risk Assessment: Implemented a sophisticated categorical aggregation model using collections. Counter to track and quantify cumulative damage multipliers across the entire team.

Strategic Flags: The model flags "critical shared weaknesses" (instances where 3 or more team members share a vulnerability), providing an immediate, high-impact decision-support metric for team revision.

Key Features & Deliverables
Real-Time Benchmarking: Provides percentile ranking for all six base stats, revealing the strategic value of an entity's statistics relative to its peers.

Interactive Visualization: Deployed as a full-stack Dash application featuring high-fidelity Plotly charts that visualize statistical distributions.

Optimized UX: Custom non-overlapping annotation logic was implemented on histograms (using precise yref coordinates) to ensure 100% clarity and accurate interpretation of multiple statistical overlays (μ, ±σ, and percentile).

Technology Stack
Category

Tool

Function

Backend & Modeling

Python

Core logic, statistical processing, and server-side execution.

Data Structure

Pandas

Data structuring, cleaning, and statistical calculations.

Statistical Engine

SciPy

Z-score and Normal CDF (Percentile) calculations.

Data Ingestion

aiohttp

Asynchronous, high-performance API calls.

Frontend/Deployment

Dash

Full-stack application framework for web deployment.

Visualization

Plotly

Creation of interactive, data-rich histograms.
