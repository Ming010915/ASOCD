# ASOCD Scoring Tool

## Configuration
- User names can be changed in \templates\index.html file under id="header".
- In the app.py file, the following variables need to be specified: IMAGES_FOLDER_PATH, DB_DIRECTORY, DATABASE_FILE, TABLE_NAME.
- In the final.py file, the following variables need to be specified: DB_DIRECTORY, OLD_DATABASE_FILE, OLD_TABLE_NAME, NEW_DATABASE_FILE, NEW_TABLE_NAME, CSV_OUTPUT_FILE.

## Instructions
- Create virtual environment using `python -m venv env`
- Activate the virtual environment
    - On Windows: `env\Scripts\activate.bat`
    - On Unix or MacOS: `source env/bin/activate`
- Run requirement.txt file to install all the required packages.
`pip install -r requirements.txt`
- Run the app.py file
- Open your web browser and go to http://127.0.0.1:5000/
- Choose the correct current user.
- Click on the buttons to make decisions.
- Data will be deleted after clicking "previous image" and "next image" buttons, if the user does not fully answered the questions.
- Data from the previous images will also be deleted after clicking "previous image". 
- Use the comment box to write additional feedbacks.
- All data will be stored in the .db file.
- When no more images are available, the buttons will be disabled, and a message will indicate this.
- User should close the program by using Ctrl+c in the terminal.
- After running the final.py file, the process, which includes pivoting the table, will result in the generation of a .csv file.

## About SQLite
- https://www.sqlitetutorial.net/download-install-sqlite/
- User can have a visualisation of the database by installing SQLiteStudio

## About images
- Images are auto generated by https://randomwordgenerator.com/picture.php
