# Gachi-backend

This project is initial setup of the Gachi project backend. The following instructions will guide you through setting up the Django development environment and configuring it with Supabase.

## Requirements
- Python Version 3.11.10
- pip
- Virtual environment (venv)

---

## Setup Instructions

### 1.Clone the Reporsitory

### 2.Create and Activate a Virtual Environment

1. Open your terminal and navigate to the project directory.
2.  Run the following command to create a new virtual environment:
    
#### Create the virtual environment

```bash
# Create a new virtual environment
python3 -m venv venv
#MacOS/Linus
source venv/bin/activate 
#Windows
venv\Scripts\activate
```

### 3.Install Dependencies

Install the required packages listed in the **requirements.txt** file.

`pip install -r requirements.txt`
 
### 4.Set Up the *.env* File

Create a **.env** file in the project root directory to manage environment variables. Copy the **.env.example** file and rename it to **.env**, then add the required environment variables

`cp .env.example .env`

#### Example contents for *.env*:

```bash
DJANGO_SECRET_KEY=your-secret-key
SUPABASE_URL=your-supabase-url
SUPABASE_KEY=your-supabase-anon-key
```

:warning: ***Note***: The **.env** file contains sensitive information, so make sure it’s listed in **.gitignore** to avoid versioning it in your Git repository.

### 5.Start the Development Server

`python manage.py runserver`

---

## How to Create the Django Project and App

- Creating the Django Project
    `django-admin startproject mysite .`
- Creating the Django App
    `python manage.py startapp myapp`

---

## How Supabase is Integrated in the Django Project

### 1. Configure *.env* file
### 2. Load *.env* Variables in *settings.py* in 'gachi_backend' project folder:

```python
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY")
```

### 3. Use Supabase in the 'gachi' App
- In **'views.py'** within the **'gachi' app**: 
    Import Supabase using the variables set in **'settings.py'**.
- In **'urls.py'** within the **'gachi' app**: 
    Define paths in the `urlpatterns`.
- In **'urls.py'** within the **'gachi_backend' project** folder: 
    Finally, include the **'gachi' app**’s URL configuration here so that it is accessible from the **main project URL patterns**.