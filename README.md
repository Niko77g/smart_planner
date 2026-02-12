# Smart Planner
## 1. Overview
**Smart Planner** is an ML-powered tool that helps students prepare more effectively for exams. It uses machine learning to estimate the time needed to learn specific material and automatically schedules study blocks in Google Calendar.
The project is built on a simple web interface that provides students with fast, data-driven time estimates for exam preparation.
## 2. Motivation
Students often struggle with estimating the time needed to prepare for exams, which leads to
**underestimating difficulty** and late preparation. Increase **stress** from inadequate preparation.
**Smart planner** solves these problems using **machine learning** to:
- **Estimate realistic time** required to learn the material
- **Reduce cognitive load** - students can focus on learning, not planning
## 3. Feature 
#### Version 1.0:
**Time predition**:
     
- ML-powered estimation of study time required
- Based on subject difficulty, student experience and available time

**Google Calendar API**

- Create event in Google Calendar
- View existing calendar events

**Two models**

- predict only: get time without calendar event
- full predict with events: predict time and create event

**Web interface**

- Simple web interface and user form

## 4.Tech Stack
- **Google Calendar API**- vybral som konkretne tuto API aby som sa naučil pracovať s API technologiami.
- **FastAPI** - kvoli podpore ML modelu aby bolo možné volať endpointy napriklad /predict
- **OOP Python**- na lepšiu organizaciu štruktury kodu.
- **ML scikitlearn** - vytvorenie Machine Learning modelu načo najpresnejšiu predikciu času pri jednotlivych parametrach učenia.
## 5. Architecture
The application follows a **layered architecture** with clear separation of concerns:
```
User -> Web UI -> FastAPI -> Predictor -> Calendar bridge -> Google Calendar API
```
#### Web interface

- HTML/CSS/JavaScript
- Collects user input [subject, difficulty, experience]
- Display prediction time

#### FastAPI
- REST API with endpoints:
    
    - `/predict` - Get study time prediction
    - `/events` - Manage calendar events
#### ML Predictor

- Scikit-learn Random forest model and Linear Regression model
- Estamates study time 
- Returns prediction in minutes 

#### Calendar Bridge

- Connects ML predictions to Google Calendar
- Formats prediction data into Google calendar events
#### Google Calendar API

- Creates and manages study events
## 6. Installation
### Prerequisites
- Docker Desktop
- Git
- Google account for Google Calendar API

### Postup inštalacie. 
 #### 1. Clone the repository
```bash
    git clone https://github.com/Niko77g/smart_planner.git
 ```
#### 2. Obtain Google Calendar API Credentials
   1. Go to Google Cloud Console
      - Visit: https://console.cloud.google.com/
      - Sign in with your Google account 
   2. Create a New Project
      - Click on the project dropdown (top left)
      - Click **"New Project"**
      - Enter project name: Smart Planner (or any name)
      - Click **"Create"**

   3. Enable Google Calendar API 
      - In the left sidebar, go to: APIs & Services → Library
      - Search for: Google Calendar API
      - Click on it and press **"Enable"**
   4. Create OAuth 2.0 Credentials
      - Go to: APIs & Services → Credentials
      - Click "+ CREATE CREDENTIALS" → select "OAuth client ID"
      - If prompted, configure the OAuth consent screen:
          - User Type: External
          - App name: Smart Planner
          - User support email: your email
          - Developer contact: your email
          - Click "Save and Continue" through the steps
      - Back to Create OAuth client ID:
          - Application type: Desktop app
          - Name: Smart Planner Desktop
          - Click **"Create"**
   5. Download Credentials
      - A popup will appear with your credentials
      - Click **"Download JSON"**
      - The file will be named something like client_secret_XXXXX.json
      - Rename it to: credentials.json
   6. Place Credentials in Project
      - create folder credentials in smart_planner folder(no in app)
      ```bash
      mkdir credentials
      ```
#### 3. Create token.json
    
- To use the Google Calendar API, the token.json file must be generated locally using generate_token.py:
```bash
    python generate_token.py
``` 

#### 4. Build Docker image      
```bash
    docker build -t smart_planner .
```    
#### 5. Run Docker image and volume

##### PowerShell:
```bash
    docker run -p 8000:8000 -v ${PWD}/credentials:/app/credentials -v ${PWD}/token.json:/app/token.json smart_planner:1.0
```
#### Linux:
```bash
docker run -p 8000:8000 -v $(pwd)/credentials:/app/credentials -v $(pwd)/token.json:/app/token.json smart_planner:1.0

```

      