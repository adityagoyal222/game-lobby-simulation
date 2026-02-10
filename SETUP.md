# Project Setup

## Configure Env File
`.env` file configured. copy contents from `.env.example` to your `.env` file (create a new one) and configure your values. Replace DB credentials with your postgres credentials. 

## Create your virtual environment 
### Using Conda
- Initialize: ```conda create -p venv python==3.12.7 -y```
- Activate: ```conda activate venv/```

### Using Python Virtual Environment (If no Conda)
#### For Windows:
- Initialize: ```python -m venv /venv```
- Activate: ```venv\Scripts\activate```

#### For Mac/Linux:
- Initialize: ```python -m venv /venv```
- Activate: ```source venv/bin/activate```

### Installing Dependencies
Run command: ```pip install -r requirements.txt```

### Initialize Database
Run command:
```python src/scripts/init_db.py```

### Populate Database
#### Run command with no arguments: 
```python src/scripts/data_gen.py```
#### Run command by specifying number of players to populate: 
```python src/scripts/data_gen.py --players 10000```
#### Run command to clear the database and repopulate: 
```python src/scripts/data_gen.py --clear```
#### Run command to clear the database only. No data entry: 
```python src/scripts/data_gen.py --clear-only```

##### Note: 
You can use a combination of these arguments together.