# -*- coding: utf-8 -*-
"""new1project.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/19eKCr7mcSF-4vMPj0Q3auCmMMloBHeiT
"""

import pandas as pd

# Load the dataset
file_path = "HR_comma_sep.csv"
data = pd.read_csv(file_path)
# Correct the column names
data.rename(columns={
    'average_montly_hours': 'average_monthly_hours',
    'time_spend_company': 'time_spent_company',
    'Department': 'department'
}, inplace=True)

# Define features and target
X = data.drop(columns=['satisfaction_level'])
y = data['satisfaction_level']

# Define categorical and numerical columns
categorical_cols = ['department', 'salary']
numerical_cols = X.select_dtypes(include=['int64', 'float64']).columns.tolist()
numerical_cols = [col for col in numerical_cols if col not in categorical_cols]

# Feature Engineering: Creating new feature
X['average_monthly_hours_per_year'] = X['average_monthly_hours'] * 12

# Update numerical columns to include the new feature
numerical_cols.append('average_monthly_hours_per_year')

import seaborn as sns
import matplotlib.pyplot as plt

# Determine the number of rows needed based on the number of numerical columns
num_cols = 4  # Number of figures per row
num_rows = (len(numerical_cols) + num_cols - 1) // num_cols  # Calculate the number of rows

fig, axes = plt.subplots(num_rows, num_cols, figsize=(15, num_rows * 5))

# Flatten axes array if there are multiple rows
axes = axes.flatten()

for i, col in enumerate(numerical_cols):
    sns.histplot(X[col], kde=True, bins=30, ax=axes[i])
    axes[i].set_title(f'Distribution of {col}')
    axes[i].set_xlabel(col)
    axes[i].set_ylabel('Frequency')

# Remove any empty subplots if there are fewer columns than grid slots
for j in range(i + 1, len(axes)):
    fig.delaxes(axes[j])

plt.tight_layout()
plt.show()

# Visualizing categorical features
for col in categorical_cols:
    plt.figure(figsize=(10, 6))
    sns.countplot(x=col, data=X)
    plt.title(f'Count of {col}')
    plt.xlabel(col)
    plt.ylabel('Count')
    plt.xticks(rotation=45)
    plt.show()

# Visualizing correlation matrix for numerical features
plt.figure(figsize=(12, 8))
corr_matrix = X[numerical_cols].corr()
sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', linewidths=0.5)
plt.title('Correlation Matrix for Numerical Features')
plt.show()

from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

# Preprocessing pipelines for numerical and categorical data
numerical_pipeline = Pipeline(steps=[
    ('scaler', StandardScaler())
])

categorical_pipeline = Pipeline(steps=[
    ('onehot', OneHotEncoder(drop='first'))
])

# Combine preprocessing steps
preprocessor = ColumnTransformer(
    transformers=[
        ('num', numerical_pipeline, numerical_cols),
        ('cat', categorical_pipeline, categorical_cols)
    ]
)

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
#Create the model pipeline
model_pipeline = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('regressor', RandomForestRegressor(random_state=42))
])

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

from sklearn.metrics import mean_squared_error, r2_score

# Train the model
model_pipeline.fit(X_train, y_train)

# Make predictions
y_pred = model_pipeline.predict(X_test)

# Evaluate the model
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

# Display the evaluation metrics
evaluation_results = {
    'Mean Squared Error': mse,
    'R-squared': r2
}

print("Evaluation Results (Initial Model):", evaluation_results)

# Feature importance
importances = model_pipeline.named_steps['regressor'].feature_importances_
feature_names = numerical_cols + model_pipeline.named_steps['preprocessor'].transformers_[1][1].named_steps['onehot'].get_feature_names_out(categorical_cols).tolist()

# Plot feature importance
plt.figure(figsize=(12, 8))
plt.barh(feature_names, importances)
plt.xlabel('Feature Importance')
plt.ylabel('Feature')
plt.title('Feature Importance in Predicting Employee Satisfaction')
plt.show()

from sklearn.model_selection import RandomizedSearchCV
from scipy.stats import randint

# Define the parameter distributions for Random Forest
param_dist = {
    'regressor__n_estimators': randint(50, 200),
    'regressor__max_features': ['auto', 'sqrt', 'log2'],
    'regressor__max_depth': [None, 10, 20, 30],
    'regressor__min_samples_split': randint(2, 11),
    'regressor__min_samples_leaf': randint(1, 5)
}

# Create the Randomized Search CV object
random_search = RandomizedSearchCV(estimator=model_pipeline, param_distributions=param_dist,
                                   n_iter=100, cv=5, n_jobs=-1, scoring='neg_mean_squared_error',
                                   random_state=42)

# Perform Randomized Search
random_search.fit(X_train, y_train)

# Get the best parameters and the best model
best_params = random_search.best_params_
best_model = random_search.best_estimator_

print("Best Parameters:", best_params)

# Make predictions with the best model
y_pred_optimized = best_model.predict(X_test)

# Evaluate the optimized model
mse_optimized = mean_squared_error(y_test, y_pred_optimized)
r2_optimized = r2_score(y_test, y_pred_optimized)

# Display the evaluation metrics for the optimized model
evaluation_results_optimized = {
    'Mean Squared Error': mse_optimized,
    'R-squared': r2_optimized
}

print("Evaluation Results (Optimized Model):", evaluation_results_optimized)

# Feature importance for the optimized model
importances_optimized = best_model.named_steps['regressor'].feature_importances_
feature_names_optimized = numerical_cols + best_model.named_steps['preprocessor'].transformers_[1][1].named_steps['onehot'].get_feature_names_out(categorical_cols).tolist()

# Plot feature importance for the optimized model
plt.figure(figsize=(12, 8))
plt.barh(feature_names_optimized, importances_optimized)
plt.xlabel('Feature Importance')
plt.ylabel('Feature')
plt.title('Feature Importance in Predicting Employee Satisfaction (Optimized Model)')
plt.show()

import joblib

# Save the best model
model_file = 'employee_satisfaction_level_model.pkl'
joblib.dump(best_model, model_file)
print(f"Model saved to {model_file}")

# Load the model to ensure it works
try:
    loaded_model = joblib.load(model_file)
    print(f"Model loaded from {model_file}")
except FileNotFoundError:
    print(f"FileNotFoundError: No such file or directory: '{model_file}'")

