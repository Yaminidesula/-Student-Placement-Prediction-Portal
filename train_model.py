
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib
import warnings
import os
warnings.filterwarnings('ignore')

def load_campus_recruitment_dataset():
    dataset_path = 'Placement_Data_Full_Class.csv'
    
    if not os.path.exists(dataset_path):
        print(f"ERROR: Dataset file '{dataset_path}' not found!")
        print("Please download the Campus Recruitment Dataset from Kaggle:")
        print("https://www.kaggle.com/datasets/benroshan/factors-affecting-campus-placement")
        return None
    df = pd.read_csv(dataset_path)
    print(f"Dataset loaded successfully!")
    print(f"Total Records: {len(df)}")
    print(f"Columns: {list(df.columns)}")
    print(f"\nDataset Preview:")
    print(df.head())

    column_mapping = {
        'ssc_p': 'ssc_p',      
        'hsc_p': 'hsc_p',      
        'degree_p': 'degree_p', 
        'mba_p': 'mba_p',     
        'specialisation': 'specialisation',
        'workex': 'workex',
        'gender': 'gender',
        'status': 'status'
    }
    
    # Select only the columns we need
    df = df[['gender', 'ssc_p', 'hsc_p', 'degree_p', 'mba_p', 
             'specialisation', 'workex', 'status']].copy()
    
    # Add skills column (simulated based on specialization and work experience)
    df['skills'] = df.apply(lambda row: generate_skills(row), axis=1)
    
    print(f"\nProcessed Dataset:")
    print(f"- Placed: {sum(df['status'] == 'Placed')}")
    print(f"- Not Placed: {sum(df['status'] == 'Not Placed')}")
    
    return df

def generate_skills(row):
    """Generate realistic skills based on specialization and work experience"""
    base_skills = ['Communication', 'Teamwork']
    
    if row['specialisation'] == 'Mkt&Fin':
        base_skills.extend(['Excel', 'Financial Analysis', 'Data Analysis'])
    else:  
        base_skills.extend(['Leadership', 'HR Management', 'Recruitment'])
    
    if row['workex'] == 'Yes':
        base_skills.extend(['Project Management', 'Problem Solving'])
    tech_skills = ['Python', 'SQL', 'PowerPoint', 'Word']
    import random
    random.seed(int(row['ssc_p']))
    selected_tech = random.sample(tech_skills, k=random.randint(1, 3))
    base_skills.extend(selected_tech)
    
    return ', '.join(base_skills)

def preprocess_data(df):
    """
    Preprocess the dataset:
    1. Handle missing values
    2. Encode categorical variables
    3. Create feature matrix X and target vector y
    """
    df_processed = df.copy()
    categorical_cols = ['gender', 'specialisation', 'workex']
    numerical_cols = ['ssc_p', 'hsc_p', 'degree_p', 'mba_p']
    
    for col in categorical_cols:
        if df_processed[col].isnull().sum() > 0:
            df_processed[col].fillna(df_processed[col].mode()[0], inplace=True)

    for col in numerical_cols:
        if df_processed[col].isnull().sum() > 0:
            df_processed[col].fillna(df_processed[col].median(), inplace=True)
    
    label_encoders = {}
    label_encoders['gender'] = LabelEncoder()
    df_processed['gender_encoded'] = label_encoders['gender'].fit_transform(df_processed['gender'])
    label_encoders['specialisation'] = LabelEncoder()
    df_processed['specialisation_encoded'] = label_encoders['specialisation'].fit_transform(df_processed['specialisation'])
    label_encoders['workex'] = LabelEncoder()
    df_processed['workex_encoded'] = label_encoders['workex'].fit_transform(df_processed['workex'])
    df_processed['skills_count'] = df_processed['skills'].apply(lambda x: len(str(x).split(',')) if pd.notna(x) else 0)
    feature_columns = ['gender_encoded', 'ssc_p', 'hsc_p', 'degree_p', 'mba_p', 
                       'specialisation_encoded', 'workex_encoded', 'skills_count']
    
    X = df_processed[feature_columns]
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
    
    # Load REAL Campus Recruitment Dataset
    print("\n[1/5] Loading Campus Recruitment Dataset...")
    df = load_campus_recruitment_dataset()
    
    if df is None:
        print("\nFailed to load dataset. Exiting...")
        return None
    
    print(f"\nDataset loaded with {len(df)} records and {len(df.columns)} features")
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
