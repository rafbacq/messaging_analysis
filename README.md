# Messaging Analysis

An advanced, production-quality machine learning project for analyzing text-message histories. 
This project parses message exports from platforms like iMessage and Instagram, extracts NLP and statistical features, evaluates relationship dynamics, and trains predictive models on conversation engagement.

## Features
- **Extensible Parsers**: Supports iMessage and Meta/Instagram HTML exports.
- **Data Privacy**: Runs entirely locally. Redacts PII like phone numbers and emails by default.
- **NLP Analysis**: Extracts sentiment, dialogue acts, and word counts.
- **Relationship Dynamics**: Computes probabilistically aggregated scores for Engagement, Reciprocity, and Warmth.
- **Machine Learning**: Predicts session continuation and provides interpretable feature importances.
- **Streamlit Dashboard**: Interactive visualization of the analysis.

## Setup

1. Place your raw HTML export files in the `text_data/` directory. **Do not modify this directory's contents manually.**
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the pipeline:
   ```bash
   python run_pipeline.py --input text_data --output outputs --my-name "Your Name"
   ```
4. View the dashboard:
   ```bash
   streamlit run src/dashboard/app.py
   ```

## Methodology & Limitations
- **No Mind-Reading**: This system computes observable behavioral metrics (e.g., response times, sentiment polarity, message balance). It does *not* claim to know true emotions or intentions.
- **Evaluation**: The ML model uses a chronological train/test split to prevent data leakage. Baseline accuracy is compared against majority class.

## Project Structure
- `src/parser/`: Data ingestion logic
- `src/processing/`: Cleaning and sessionization
- `src/features/`: NLP and statistical feature engineering
- `src/modeling/`: Scikit-learn predictive models
- `src/reporting/`: Markdown report generator
- `src/dashboard/`: Interactive Streamlit app
