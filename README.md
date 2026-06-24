# Student Placement Prediction Portal

## Overview

The Student Placement Prediction Portal is a Machine Learning-based web application that predicts whether a student is likely to be placed or not based on academic performance and skill level. The system uses a Logistic Regression model to analyze student data and provide placement predictions along with probability scores.

## Problem Statement

Many students are uncertain about their placement opportunities and lack a clear understanding of their current readiness. This project aims to provide a simple and effective solution by predicting placement outcomes using key student attributes.

## Objectives

* Predict student placement status (Placed / Not Placed)
* Use CGPA and Skills as input features
* Provide probability-based prediction results
* Demonstrate the practical application of Machine Learning in education

## Features

* User Registration and Login
* Student Profile Management
* Placement Prediction System
* Prediction Probability Display
* Prediction History Tracking
* Responsive User Interface

## Technology Stack

### Frontend

* HTML
* CSS
* JavaScript

### Backend

* Python
* Flask

### Machine Learning

* Scikit-learn
* Logistic Regression

### Data Processing

* Pandas
* NumPy

### Database

* SQL Database

## Dataset Details

Dataset: `Placement_Data_Full_Class.csv`

### Input Features

* CGPA (Academic Performance)
* Skills (Technical Skill Rating)

### Target Variable

* Placement Status

  * 1 = Placed
  * 0 = Not Placed

## System Workflow

1. User logs into the system.
2. User enters required details.
3. Input data is sent to the backend.
4. Logistic Regression model processes the data.
5. Placement prediction and probability are generated.
6. Results are displayed and stored in prediction history.

## Machine Learning Model

This project uses **Logistic Regression**, a supervised machine learning algorithm designed for binary classification problems.

### Why Logistic Regression?

* Suitable for binary classification
* Fast and efficient
* Easy to implement
* Provides probability scores
* Works well with structured datasets

## Project Structure

```text
Student-Placement-Prediction-Portal/
│
├── app.py
├── train_model.py
├── model.pkl
├── requirements.txt
├── templates/
├── static/
├── database/
└── Placement_Data_Full_Class.csv
```

## Installation

Clone the repository:

```bash
git clone https://github.com/Yaminidesula/-Student-Placement-Prediction-Portal.git
```

Navigate to the project directory:

```bash
cd Student-Placement-Prediction-Portal
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the application:

```bash
python app.py
```

Open the application in your browser:

```text
http://localhost:5000
```

## Results

The system successfully predicts student placement status based on CGPA and skills. It provides quick and reliable predictions along with probability scores, helping users better understand their placement chances.

## Limitations

* Uses only CGPA and skills as input features
* Does not consider internships, communication skills, or aptitude scores
* Prediction accuracy depends on the quality of training data

## Future Enhancements

* Add more placement-related features
* Improve model accuracy with larger datasets
* Resume Analysis Module
* Company Recommendation System
* Advanced Machine Learning Models

## Author

**Yamini Desula**
B.Tech – Information Technology
Student Placement Prediction Portal Project
