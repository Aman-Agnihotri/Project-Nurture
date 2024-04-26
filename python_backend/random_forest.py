import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
import joblib

# Load the dataset
data = pd.read_csv('../Minor2data.csv')

# Encode categorical variables
data = pd.get_dummies(data, columns=['Health Portfolio', 'Urban or Rural'])

# Select the target variable (Scale) and the features
target = 'Scale'
features = [
    'Age (1-11)',
    'Weight (kg)',
    'Height (cm)',
    'Household Income'
    ]

# Add the encoded 'Health Portfolio' and 'Urban or Rural' features
health_portfolio_features = [col for col in data.columns if 'Health Portfolio_' in col]
urban_rural_features = [col for col in data.columns if 'Urban or Rural_' in col]
features.extend(health_portfolio_features)
features.extend(urban_rural_features)

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(data[features], data[target], test_size=0.2, random_state=42)

# Initialize the Random Forest Regressor
rf_regressor = RandomForestRegressor(n_estimators=100, random_state=42)

# Train the model
rf_regressor.fit(X_train, y_train)

# Make predictions on the test set
y_pred = rf_regressor.predict(X_test)

# Evaluate the model
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)
print(f"Mean Squared Error: {mse}")
print(f"R-squared: {r2}")

# Get feature importances
importances = rf_regressor.feature_importances_
feature_importance = pd.Series(importances, index=X_train.columns)
print("Feature Importances:")
print(feature_importance.sort_values(ascending=False))

joblib.dump(rf_regressor, 'random_forest_model.pkl')

# Make predictions for future scenarios
new_data = pd.DataFrame({
    'Age (1-11)': [6, 8, 10],
    'Weight (kg)': [15.0, 17.5, 20.0],
    'Height (cm)': [110, 120, 130],
    'Household Income': [12000, 15000, 18000],
    'Health Portfolio_Allergies': [0, 0, 0],
    'Health Portfolio_Asthma': [1, 0, 0],
    'Health Portfolio_Excellent': [0, 0, 1],
    'Health Portfolio_Good': [0, 0, 0],
    'Health Portfolio_Normal': [1, 0, 0],
    'Urban or Rural_Rural': [0, 1, 0],
    'Urban or Rural_Urban': [1, 0, 1]
})

# Make predictions for future scenarios
future_predictions = rf_regressor.predict(new_data)
print("\nPredictions for Future Scenarios:")
print(future_predictions)