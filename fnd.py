# Libraries
import pandas as pd
import matplotlib.pyplot as plt
import pickle
from sklearn.model_selection import train_test_split 
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report

# Load the datasets
fake_data = pd.read_csv('Fake.csv')
true_data = pd.read_csv('True.csv')

# Assign labels to each dataset
true_data['label'] = 'REAL'
fake_data['label'] = 'FAKE'

# Combining both datasets
data = pd.concat([true_data, fake_data])
# remove any rows with missing values
data = data[['text', 'label']].dropna()
# Shuffle the dataset to ensure randomness
data = data.sample(frac=1, random_state=42)

# Plot a bar chart showing the distribution of fake vs real news
label_counts = data['label'].value_counts()
plt.figure(figsize=(5, 4))
label_counts.plot(kind='bar', color=['green', 'red'])
plt.title('News Label Distribution')
plt.xlabel('Label')
plt.ylabel('Count')
plt.grid(True)
plt.tight_layout()
plt.show()

X = data['text']    #The news text
y = data['label']   #The class (REAL/FAKE)

# Split the dataset into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Initialize the TF-IDF Vectorizer to convert text to numeric format
vectorization = TfidfVectorizer()
# Fit the vectorizer on training data and transform the training text
X_train = vectorization.fit_transform(X_train)
# Transform the testing text using the already fitted vectorizer
X_test = vectorization.transform(X_test)

# Initialize and train the Logistic Regression model
LRmodel = LogisticRegression()
LRmodel.fit(X_train, y_train)

# Predict the labels for the test data
pred_lr = LRmodel.predict(X_test)
# Calculate the accuracy of the model
accuracy = accuracy_score(y_test, pred_lr)
print(f"Logistic Regression Accuracy: {round(accuracy * 100, 2)}%")

print(classification_report(y_test, pred_lr))

# Save the trained model and vectorizer using pickle
pickle.dump(LRmodel, open("LRmodel.pkl", "wb"))
pickle.dump(vectorization, open("vectorization.pkl", "wb"))
