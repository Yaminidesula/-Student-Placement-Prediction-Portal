"""
Student Placement Prediction Model Training Script
This script trains a Logistic Regression model on the Campus Recruitment Dataset
and saves it as model.pkl for use in the Flask application.
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib
import warnings
warnings.filterwarnings('ignore')

# Create synthetic dataset (Campus Recruitment style)
# In production, replace this with actual dataset loading
def create_sample_dataset():
    """
    Create a synthetic dataset similar to Campus Recruitment Dataset
    Features: Gender, 10th %, 12th %, Degree %, MBA %, Specialization, Work Experience, Skills
    Target: Placement Status (Placed/Not Placed)
    """
    np.random.seed(42)
    n_samples = 250
    
    data = {
        'gender': np.random.choice(['M', 'F'], n_samples),
        'ssc_p': np.random.uniform(50, 95, n_samples),  # 10th percentage
        'hsc_p': np.random.uniform(50, 95, n_samples),  # 12th percentage
        'degree_p': np.random.uniform(50, 95, n_samples),  # Degree percentage
        'mba_p': np.random.uniform(50, 95, n_samples),  # MBA percentage
        'specialisation': np.random.choice(['Mkt&HR', 'Mkt&Fin'], n_samples),
        'workex': np.random.choice(['Yes', 'No'], n_samples),
        'status': np.random.choice(['Placed', 'Not Placed'], n_samples, p=[0.65, 0.35])
    }
    
    # Add skills as a composite feature
    skills_list = ['Python', 'Java', 'SQL', 'Excel', 'Communication', 'Leadership', 
                   'Analytics', 'Machine Learning', 'Web Development', 'Cloud Computing']
    data['skills'] = [', '.join(np.random.choice(skills_list, np.random.randint(2, 6), replace=False)) 
                      for _ in range(n_samples)]
    
    df = pd.DataFrame(data)
    
    # Make placement more likely with better scores
    for idx, row in df.iterrows():
        score = (row['ssc_p'] + row['hsc_p'] + row['degree_p'] + row['mba_p']) / 4
        if score > 75 and row['workex'] == 'Yes':
            df.at[idx, 'status'] = 'Placed'
        elif score < 60:
            df.at[idx, 'status'] = 'Not Placed'
    
    return df

def preprocess_data(df):
    """
    Preprocess the dataset:
    1. Handle missing values
    2. Encode categorical variables
    3. Create feature matrix X and target vector y
    """
    # Create a copy to avoid modifying original data
    df_processed = df.copy()
    
    # Handle missing values (fill with mode for categorical, median for numerical)
    categorical_cols = ['gender', 'specialisation', 'workex']
    numerical_cols = ['ssc_p', 'hsc_p', 'degree_p', 'mba_p']
    
    for col in categorical_cols:
        if df_processed[col].isnull().sum() > 0:
            df_processed[col].fillna(df_processed[col].mode()[0], inplace=True)
    
    for col in numerical_cols:
        if df_processed[col].isnull().sum() > 0:
            df_processed[col].fillna(df_processed[col].median(), inplace=True)
    
    # Encode categorical variables
    label_encoders = {}
    
    # Gender encoding: M=1, F=0
    label_encoders['gender'] = LabelEncoder()
    df_processed['gender_encoded'] = label_encoders['gender'].fit_transform(df_processed['gender'])
    
    # Specialization encoding
    label_encoders['specialisation'] = LabelEncoder()
    df_processed['specialisation_encoded'] = label_encoders['specialisation'].fit_transform(df_processed['specialisation'])
    
    # Work experience encoding: Yes=1, No=0
    label_encoders['workex'] = LabelEncoder()
    df_processed['workex_encoded'] = label_encoders['workex'].fit_transform(df_processed['workex'])
    
    # Skills encoding - count number of skills as a feature
    df_processed['skills_count'] = df_processed['skills'].apply(lambda x: len(str(x).split(',')) if pd.notna(x) else 0)
    
    # Select features for training
    feature_columns = ['gender_encoded', 'ssc_p', 'hsc_p', 'degree_p', 'mba_p', 
                       'specialisation_encoded', 'workex_encoded', 'skills_count']
    
    X = df_processed[feature_columns]
    
    # Target variable: Placed=1, Not Placed=0
    label_encoders['status'] = LabelEncoder()
    y = label_encoders['status'].fit_transform(df_processed['status'])
    
    return X, y, label_encoders, feature_columns

def train_model():
    """
    Train the Logistic Regression model and save it
    """
    print("=" * 60)
    print("Student Placement Prediction - Model Training")
    print("=" * 60)
    
    # Create/load dataset
    print("\n[1/5] Loading dataset...")
    df = create_sample_dataset()
    print(f"Dataset loaded with {len(df)} records and {len(df.columns)} features")
    print(f"Features: {list(df.columns)}")
    
    # Preprocess data
    print("\n[2/5] Preprocessing data...")
    X, y, label_encoders, feature_columns = preprocess_data(df)
    print(f"Features selected: {feature_columns}")
    print(f"Target classes: {label_encoders['status'].classes_}")
    
    # Split data into train and test sets (80:20)
    print("\n[3/5] Splitting data (80% train, 20% test)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"Training set: {len(X_train)} samples")
    print(f"Test set: {len(X_test)} samples")
    
    # Feature scaling
    print("\n[4/5] Scaling features...")
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train Logistic Regression model
    print("\n[5/5] Training Logistic Regression model...")
    model = LogisticRegression(
        random_state=42,
        max_iter=1000,
        C=1.0,
        solver='lbfgs'
    )
    model.fit(X_train_scaled, y_train)
    
    # Evaluate model
    print("\n" + "=" * 60)
    print("Model Evaluation")
    print("=" * 60)
    
    y_pred = model.predict(X_test_scaled)
    y_pred_proba = model.predict_proba(X_test_scaled)
    
    accuracy = accuracy_score(y_test, y_pred)
    print(f"\nAccuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
    
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=['Not Placed', 'Placed']))
    
    print("\nConfusion Matrix:")
    print(confusion_matrix(y_test, y_pred))
    
    # Feature importance (coefficients)
    print("\nFeature Importance (Coefficients):")
    for feature, coef in zip(feature_columns, model.coef_[0]):
        print(f"  {feature}: {coef:.4f}")
    
    # Save model and preprocessing objects
    print("\n" + "=" * 60)
    print("Saving Model")
    print("=" * 60)
    
    model_data = {
        'model': model,
        'scaler': scaler,
        'label_encoders': label_encoders,
        'feature_columns': feature_columns
    }
    
    joblib.dump(model_data, 'model.pkl')
    print("\nModel saved successfully as 'model.pkl'")
    print("\nThe model is ready to use in the Flask application!")
    print("=" * 60)
    
    return model_data

if __name__ == '__main__':
    train_model()
