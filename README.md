# Stack Overflow Tag Analysis — Cloud ETL Pipeline

## Project Description

This project implements a Python ETL (Extract, Transform, Load) pipeline that analyzes Stack Overflow tag statistics using Google BigQuery. The pipeline extracts large-scale developer data from a cloud data warehouse, transforms the data using pandas to clean and calculate additional metrics, and loads the final dataset into a timestamped CSV file. This project demonstrates a real-world data engineering workflow similar to what companies use to process and analyze large datasets.

---

# Project Structure

```
lab_3/
│
├── pipeline.py        # Main ETL pipeline
├── requirements.txt   # Python dependencies
├── README.md          # Project documentation
└── output/
      stackoverflow_tags_TIMESTAMP.csv
```

---

# How to Run the Project

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
cd lab_3
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

Dependencies used in this project:

```
google-cloud-bigquery
pandas
pyarrow
```

### 3. Authenticate with Google Cloud

BigQuery requires authentication to access datasets.

Run:

```bash
gcloud auth application-default login
```

A browser window will open asking you to sign in with your Google account.

---

### 4. Run the ETL Pipeline

```bash
python pipeline.py
```

Expected output:

```
==================================================
 Stack Overflow Tag Analysis — ETL Pipeline
==================================================
[EXTRACT] Running BigQuery query...
[EXTRACT] Retrieved 100 rows from BigQuery.
[TRANSFORM] Cleaning and enriching data...
[TRANSFORM] Done. 99 tags remaining.
[LOAD] Saving results...
[LOAD] Pipeline complete!
Pipeline finished successfully.
```

The pipeline will generate a timestamped CSV file inside the `output/` directory.

---

# Pipeline Architecture

This project follows the **ETL architecture**, a common pattern used in data engineering pipelines.

## Extract

The extract phase connects to **Google BigQuery**, a cloud data warehouse, and runs a SQL query against the public Stack Overflow dataset.

The query retrieves:

- Programming tags
- Total number of questions
- Average score
- Average view count
- Number of unanswered questions
- Average answers per question

The query also uses:

```
UNNEST(SPLIT(tags, '|'))
```

to separate the multiple tags stored in each Stack Overflow post.

The results are returned as a **pandas DataFrame** for further processing.

---

## Transform

The transform phase cleans and enriches the dataset using pandas.

Operations performed include:

1. Removing rows with missing values
2. Filtering out tags shorter than two characters
3. Creating a new metric called `unanswered_rate`

```
unanswered_rate = unanswered_count / total_questions
```

4. Creating an `engagement_score` that measures overall activity for each tag

```
engagement_score =
(avg_score * 0.4) +
(avg_views / 1000 * 0.4) +
(avg_answers * 0.2)
```

5. Sorting the dataset by `engagement_score` in descending order

This produces a ranked list of the most engaged programming communities on Stack Overflow.

---

## Load

The load phase saves the cleaned dataset to a CSV file.

A timestamp is added to the filename to prevent previous results from being overwritten.

Example filename:

```
output/stackoverflow_tags_20260308_213412.csv
```

The CSV contains the following columns:

```
tag
total_questions
avg_score
avg_views
unanswered_count
avg_answers
unanswered_rate
engagement_score
```

---

# Analysis Findings

## Question 1  
**Which tag has the highest engagement score?**

The tag with the highest engagement score was **npm**, with a score of approximately **1.27**. This likely reflects the heavy usage of npm in the JavaScript ecosystem, where developers frequently ask questions related to package management, dependencies, and build tools.

---

## Question 2  
**Which tag has the highest unanswered rate?**

One of the tags with the highest unanswered rates was **windows**, with an unanswered rate of approximately **0.36**. This may indicate that questions related to operating system issues can be more complex or specific, making them harder for the community to answer quickly.

---

## Question 3  
**Why is querying BigQuery different from querying a local CSV file?**

Querying BigQuery allows developers to run SQL queries on extremely large datasets stored in the cloud, often containing billions of rows. In contrast, a CSV file must be downloaded and processed locally, which limits performance and scalability. BigQuery distributes query processing across Google’s infrastructure, making it much faster for large-scale analytics.

---

## Question 4  
**How could Stack Overflow use these results?**

Stack Overflow could use this data to identify which developer communities are the most active and which topics may require additional support. For example, tags with high unanswered rates could indicate areas where the platform may need more expert contributors or improved documentation. This information could also help prioritize moderation, community engagement, and content development.

---

# Screenshots

Include the following screenshots in your repository:

1. BigQuery query results showing the SQL query output
2. Terminal output showing the ETL pipeline running successfully

---

# Technologies Used

```
Python
Pandas
Google BigQuery
Google Cloud CLI
SQL
```

---

# Author

David Farina