# Zolvo Collection AI

Zolvo Collection AI is a robust, AI-powered **Debtor Prioritization and Decision Support System** designed to streamline B2B accounts receivable and collections management.

This Proof of Concept (PoC) application integrates a sophisticated rule-based risk scoring algorithm with the reasoning capabilities of the **Llama 3.3 70B** large language model. It provides collections teams with transparent, explainable action recommendations and comprehensive portfolio analytics.

## Key Features

* **Advanced Rule-Based Risk Scoring:** Calculates a mathematical risk score (0-100) for each debtor by evaluating multiple dimensions:
  * Days Overdue (30%)
  * Outstanding Amount (20%)
  * Payment History (15%)
  * Sector Risk (15%)
  * Credit Rating (10%)
  * Days Since Last Contact (10%)
  * Dynamic Trend Bonus/Penalty based on historical payment performance.
* **LLM-Powered Explainability:** Goes beyond simple "Call" or "Email" actions. Using the **Llama 3.3 70B** model via the Groq API, the system generates professional explanations (in Turkish or English) detailing *why* a specific action is recommended based on the debtor's full context (sector, credit rating, past delays). *Note: The AI explains the decision; it does not make the final call.*
* **Comprehensive Visual Analytics:** 
  * Interactive portfolio sector distribution via Plotly Pie Charts.
  * Individual debtor trend analysis using historical invoice delay Sparklines.
  * Detailed breakdown of risk score components.
* **Cloud-Native Security (Cloudflare Workers):** The application implements a secure, serverless edge proxy via Cloudflare. API keys are never exposed on the client side; all LLM requests are securely routed through the proxy.

## System Architecture

1. **Synthetic Data Engine (`data_generator.py`):** Generates realistic B2B debtor profiles including sectors (Technology, Construction, etc.), Findeks-style credit ratings (A, B, C, D), invoice counts, and historical payment delay matrices.
2. **Scoring Engine (`scoring_engine.py`):** Processes the data through a weighted algorithmic pipeline to produce the final risk scores and actionable categorizations.
3. **Streamlit Interface (`app.py`):** Renders the high-performance UI, integrating Plotly for data visualization, real-time filtering, and detailed debtor analysis views.
4. **Cloudflare Proxy:** Acts as a secure intermediary for API calls. When an explanation is requested, the Streamlit app queries the Cloudflare Worker, which injects the encrypted API key and forwards the request to Groq.
5. **LLM Engine (`llm_engine.py`):** Formats the debtor context and interfaces with the LLM to generate concise, professional strategic advice.

## Installation and Setup

To run the project locally, follow these steps:

### Prerequisites
- Python 3.10 or higher
- Cloudflare Account (for the security proxy layer)

### Instructions

1. **Clone the Repository**
   ```bash
   git clone https://github.com/emreerbasli/Case.git
   cd Case
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure the Security Proxy**
   * The application codebase does not contain API keys.
   * Create a Cloudflare Worker and define your Groq API key as a secret environment variable (`ZOLVO_API_KEY`).
   * Update the `base_url` parameter in `llm_engine.py` with your custom Worker URL.

4. **Launch the Application**
   ```bash
   streamlit run app.py
   ```

## Technology Stack

* **Backend / Frontend:** Python, Streamlit, Pandas, Plotly
* **Artificial Intelligence (LLM):** Meta Llama 3.3 70B (via Groq API)
* **Security Layer:** Cloudflare Workers (Serverless Edge Proxy)
* **Version Control:** Git & GitHub

---
*This project is a Proof of Concept (PoC) demonstrating the potential of integrating advanced analytics and Generative AI into modern Collections Intelligence systems.*
