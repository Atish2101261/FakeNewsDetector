import pandas as pd
import pickle
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

print("Loading data for topic training...")
fake_data = pd.read_csv('Fake.csv')
true_data = pd.read_csv('True.csv')

# Combine datasets and shuffle
data = pd.concat([true_data, fake_data])
data = data[['text', 'subject']].dropna()
data = data.sample(frac=1, random_state=42)

X = data['text']
y = data['subject']

print(f"Dataset size: {len(data)} rows")
print("Unique subjects:", y.unique())

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Vectorization
print("Vectorizing text...")
vectorizer = TfidfVectorizer(max_features=5000) # Limiting features for speed
X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

# Model Training
print("Training Subject Model...")
SubjectModel = LogisticRegression(max_iter=1000)
SubjectModel.fit(X_train_vec, y_train)

# Evaluation
y_pred = SubjectModel.predict(X_test_vec)
acc = accuracy_score(y_test, y_pred)
print(f"Subject Classification Accuracy: {round(acc * 100, 2)}%")

# Save
print("Saving Subject Model and Vectorizer...")
pickle.dump(SubjectModel, open("SubjectModel.pkl", "wb"))
pickle.dump(vectorizer, open("SubjectVectorizer.pkl", "wb"))
print("Done!")
