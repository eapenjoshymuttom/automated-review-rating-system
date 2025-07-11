import os
import pandas as pd
import re
import nltk

from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# Download required resources
nltk.download('stopwords')
nltk.download('wordnet')

# 📁 Input and Output folders
csv_folder = "C:/Users/eapen/OneDrive/Desktop/automated-review-rating-system/data/reviews"
output_folder = "C:/Users/eapen/OneDrive/Desktop/automated-review-rating-system/data/cleaned_dataset"
os.makedirs(output_folder, exist_ok=True)
output_file = os.path.join(output_folder, "cleaned_data.csv")

# 🧠 NLP setup
stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()
import re
import emoji

def remove_emojis(text):
    return emoji.replace_emoji(str(text), replace='')



def clean_text(text):
    if pd.isnull(text):
        return ""
    text = text.lower()
    text = remove_emojis(text)
    text = re.sub(r'READ MORE', '', text, flags=re.IGNORECASE)
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'[^a-zA-Z0-9\s.,!?]', '', text)  # Remove all odd characters
    text = ' '.join(text.split())  # Normalize whitespace
    return text.strip().strip('.')  # Remove trailing dots


def preprocess_text(text):
    """Clean + remove stopwords + lemmatize."""
    text = clean_text(text)
    words = [lemmatizer.lemmatize(w) for w in text.split() if w.lower() not in stop_words]
    return ' '.join(words)

# 📥 Step 1: Load CSV files
all_files = [f for f in os.listdir(csv_folder) if f.endswith(".csv")]
df_list = []

for file in all_files:
    try:
        path = os.path.join(csv_folder, file)
        df = pd.read_csv(path)
        print(f"✅ Loaded {file} with {len(df)} rows")
        df_list.append(df)
    except Exception as e:
        print(f"⚠️ Skipped {file}: {e}")

if not df_list:
    print("❌ No valid CSV files found. Exiting.")
    exit()

# 🧩 Step 2: Combine and basic cleaning
df = pd.concat(df_list, ignore_index=True)
df = df.replace("N/A", pd.NA).dropna()
df = df.drop_duplicates()

# ❌ Step 3: Drop rows with empty essential fields
df = df[
    (df['Description'].astype(str).str.strip() != '') &
    (df['Rating'].astype(str).str.strip() != '') &
    (df['Title'].astype(str).str.strip() != '')
]


# ❌ Step 4: Drop unnecessary columns (if present)
columns_to_drop = ['Name', 'Date', 'Helpful_Votes', 'Certified_Buyer']
existing_columns_to_drop = [col for col in columns_to_drop if col in df.columns]
df = df.drop(columns=existing_columns_to_drop)

# 🧹 Step 5: Preprocess the Description
print("🔄 Preprocessing review descriptions...")
df['Cleaned_Description'] = df['Description'].apply(preprocess_text)
# 💾 Step 6: Save final cleaned data
df.to_csv(output_file, index=False)
print(f"\n✅ Cleaned dataset saved to: {output_file}")
