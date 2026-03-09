# pipeline.py
# Stack Overflow Tag Analysis — ETL Pipeline
# Author: David Farina

import pandas as pd
from google.cloud import bigquery
from datetime import datetime
import os

PROJECT_ID = 'zeta-environs-489004-b7'
OUTPUT_DIR = 'output'

START_DATE = '2020-01-01'
END_DATE = '2024-01-01'
MIN_QUESTIONS = 500


# ─────────────────────────────────────────
# EXTRACT
# ─────────────────────────────────────────
def extract(client: bigquery.Client) -> pd.DataFrame:
    """Pulls raw tag statistics from BigQuery."""
    print('[EXTRACT] Running BigQuery query...')

    query = f'''
    SELECT tag, COUNT(*) AS total_questions,
        ROUND(AVG(score), 2) AS avg_score,
        ROUND(AVG(view_count), 0) AS avg_views,
        COUNTIF(answer_count = 0) AS unanswered_count,
        ROUND(AVG(answer_count), 2) AS avg_answers
    FROM `bigquery-public-data.stackoverflow.posts_questions`,
        UNNEST(SPLIT(tags, '|')) AS tag
    WHERE creation_date >= '{START_DATE}'
        AND creation_date < '{END_DATE}'
    GROUP BY tag
    HAVING COUNT(*) > {MIN_QUESTIONS}
    ORDER BY total_questions DESC
    LIMIT 100
    '''

    # Run the query and convert results to a pandas DataFrame
    df = client.query(query).to_dataframe()

    print(f'[EXTRACT] Retrieved {len(df)} rows from BigQuery.')
    return df


# ─────────────────────────────────────────
# TRANSFORM
# ─────────────────────────────────────────
def transform(df: pd.DataFrame) -> pd.DataFrame:
    """Cleans and enriches the raw data."""
    print('[TRANSFORM] Cleaning and enriching data...')

    # Step 1: Drop rows where tag or total_questions is missing
    df.dropna(subset=['tag', 'total_questions'], inplace=True)

    # Step 2: Remove tags shorter than 2 characters
    df = df[df['tag'].str.len() > 1]

    # Step 3: Create unanswered_rate column
    df['unanswered_rate'] = (
        df['unanswered_count'] / df['total_questions']
    ).round(4)

    # Step 4: Create engagement_score column
    df['engagement_score'] = (
        (df['avg_score'] * 0.4) +
        (df['avg_views'] / 1000 * 0.4) +
        (df['avg_answers'] * 0.2)
    ).round(2)

    # Step 5: Sort by engagement_score and reset index
    df.sort_values('engagement_score', ascending=False, inplace=True)
    df.reset_index(drop=True, inplace=True)

    print(f'[TRANSFORM] Done. {len(df)} tags remaining.')
    return df


# ─────────────────────────────────────────
# LOAD
# ─────────────────────────────────────────
def load(df: pd.DataFrame) -> None:
    """Saves transformed data to a timestamped CSV."""
    print('[LOAD] Saving results...')

    # Step 1: Create output folder if it doesn't exist
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Step 2: Build timestamped filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = os.path.join(
        OUTPUT_DIR,
        f'stackoverflow_tags_{timestamp}.csv'
    )

    # Step 3: Save DataFrame to CSV
    df.to_csv(filename, index=False)

    print(f'[LOAD] Saved to {filename}')
    print('[LOAD] Pipeline complete!')


# ─────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────
def main():
    print('=' * 50)
    print(' Stack Overflow Tag Analysis — ETL Pipeline')
    print('=' * 50)

    # Create BigQuery client
    client = bigquery.Client(project=PROJECT_ID)

    # Run ETL pipeline
    raw_df = extract(client)
    transformed_df = transform(raw_df)
    load(transformed_df)

    print('Pipeline finished successfully.')


if __name__ == '__main__':
    main()
    