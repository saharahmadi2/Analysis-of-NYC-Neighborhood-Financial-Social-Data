
# Sahar Ahmadi
# CIS 3120 Final Project
# Neighborhood Financial Health Analysis


import os
import pandas as pd
import matplotlib.pyplot as plt
import re
import requests
from bs4 import BeautifulSoup
from collections import Counter

# Data Cleaning Class

class DataCleaner:
    def __init__(self, input_file):
        self.input_file = input_file

        try:
            self.df = pd.read_csv(self.input_file, encoding="utf-8")
        except UnicodeDecodeError:
            self.df = pd.read_csv(self.input_file, encoding="latin1")


    def clean_data(self):
        self.df.dropna(how="all", inplace=True)
        self.df.columns = [c.strip() for c in self.df.columns]
        self.df.drop_duplicates(inplace=True)
        self.df.dropna(inplace=True)

        for col in self.df.select_dtypes(include="object").columns:
            try:
                self.df[col] = pd.to_numeric(
                    self.df[col].str.replace(",", ""), errors="ignore"
                )
            except:
                pass

        for col in self.df.select_dtypes(include="object").columns:
            self.df[col] = self.df[col].str.strip().str.title()
        return self.df

    def save_cleaned_data(self, output_file):
        self.df.to_csv(output_file, index=False)
        print(f"Cleaned data saved as {output_file}")



raw_csv = "Neighborhood_Financial_Health_Digital_Mapping_and_Data_Tool_20251213.csv"
clean_csv = "Cleaned_Neighborhood_Financial_Health_Digital_Mapping_and_Data_Tool_20251213.csv"

cleaner = DataCleaner(raw_csv)
cleaner.clean_data()
cleaner.save_cleaned_data(clean_csv)


# 1. Load Dataset

df = pd.read_csv(clean_csv)


# 2. Additional Data Cleaning
numeric_cols = df.select_dtypes(include=['float64','int64']).columns
for col in numeric_cols:
    df[col] = df[col].fillna(df[col].mean())

string_cols = df.select_dtypes(include=['object']).columns
for col in string_cols:
    df[col] = df[col].fillna("Unknown")

df = df.drop_duplicates()
df.to_csv("Cleaned_Financial_Data.csv", index=False)


# 3. OOP: Neighborhood Class

class Neighborhood:
    def __init__(self, name, index_score, total_outcome, median_income):
        self.name = name
        self.index_score = index_score
        self.total_outcome = total_outcome
        self.median_income = median_income

    def is_high_score(self):
        return self.index_score > 3

    def income_category(self):
        if self.median_income > 70000:
            return "High"
        elif self.median_income > 50000:
            return "Medium"
        else:
            return "Low"

neighborhoods = []
for i in range(len(df)):
    neighborhoods.append(
        Neighborhood(
            df.iloc[i]['Neighborhoods'],
            df.iloc[i]['IndexScore'],
            df.iloc[i]['TotalOutcome'],
            df.iloc[i]['Median_Income']
        )
    )


# 4. Filtering, Grouping, Aggregation

borough_group = df.groupby("Borough").agg(
    Avg_IndexScore=("IndexScore","mean"),
    Avg_Income=("Median_Income","mean"),
    TotalOutcome=("TotalOutcome","sum")
).sort_values(by="Avg_IndexScore", ascending=False)

high_score = df[df["IndexScore"] > 3]


# 5. Visualizations
# Bar Chart: Average Index Score by Borough
plt.figure(figsize=(6,4))
plt.bar(borough_group.index, borough_group["Avg_IndexScore"], color='orange')
plt.title("Average Index Score by Borough")
plt.xlabel("Borough")
plt.ylabel("Avg Index Score")
plt.tight_layout()
plt.show()

# Histogram: Distribution of Index Scores
plt.figure(figsize=(8,5))
plt.hist(df["IndexScore"], bins=10, color='skyblue', edgecolor='black', alpha=0.7)
plt.title("Distribution of Index Scores Across Neighborhoods")
plt.xlabel("Index Score")
plt.ylabel("Number of Neighborhoods")
plt.grid(axis='y', alpha=0.75)
plt.tight_layout()
plt.savefig("Histogram_IndexScore.png")
plt.show()


# 6. Regex Extraction
df["PUMA_Code"] = df["PUMA"].apply(
    lambda x: re.findall(r'\d+', str(x))[0] if re.findall(r'\d+', str(x)) else "Unknown"
)


# 7. WEB SCRAPING
url = "https://www.nyc.gov/site/opportunity/poverty-in-nyc/poverty-measure.page"
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

headlines = [h.text.strip() for h in soup.find_all("h2")[:5]]

with open("scraped_headlines.txt", "w") as f:
    for h in headlines:
        f.write(h + "\n")



# 8. TEXT MINING
text_data = " ".join(df["Neighborhoods"].astype(str))
tokens = re.findall(r'\b[a-zA-Z]{3,}\b', text_data.lower())

word_freq = Counter(tokens)
top_words = word_freq.most_common(10)

with open("text_mining_results.txt", "w") as f:
    f.write("Top Neighborhood Name Keywords:\n")
    for word, count in top_words:
        f.write(f"{word}: {count}\n")



# 9. Save Analysis Log
with open("analysis_log.txt","w") as f:
    f.write("High Index Score Neighborhoods:\n")
    f.write(str(high_score[["Neighborhoods","IndexScore","Median_Income"]]))

print("Project completed successfully")
