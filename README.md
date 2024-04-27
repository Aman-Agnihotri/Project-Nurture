# Minor_2
Project Nurture: Malnutrition Watch

The project link on vercel - https://vercel.com/aman-agnihotris-projects/minor-2

Instructions for running the app - 

Step 1: Clone the repository in the any suitable directory using this command - 

git clone https://github.com/Aman-Agnihotri/Minor_2

Step 2: Change directory to the project_nurture folder - 

cd project_nurture

Step 3: Make sure you have node installed on your system, at least node version 20.x.

Step 4: Install all the dependencies - 

npm i

Step 5: Now run the command to launch the app - 

npm run dev

The app is operational now on the address - http://localhost:5173/

Now, in order to see the random forest model interact with the app interface, you need to run the flask server that is in the python_backend folder. Make sure that python is properly installed on the system. Here's how to run the flask server - 

Step 1: Change directory to python_backend - 

cd python_backend

Step 2: Create a python virtual environment - 

For Linux and Mac - python -m venv .venv

For Windows - python -m venv venv

Step 3: Activate the virtual environment to work with the terminal - 

For Linux - 
1. With bash shell - source .venv/bin/activate
2. With fish shell - source .venv/bin/activate.fish

For Mac - source venv/bin/activate

For Windows - 
1. With Windows Powershell - .\venv\Scripts\Activate.ps1
2. With CMD - venv/Scripts/activate

Step 4: Install the python package dependencies - 

pip install -r requirements.txt

Step 5: Now the other scripts besides the flask app can be run directly, just as you would run any python program. Now, before running the flask server, you would need to run the random_forest.py script, so that the model is created first and is ready to be served by the flask server. Now, to run the flask app, you need to just run this command - 

flask run

And Voila! The server now runs on the port 8000. Now, every functionality of the app is working as intended.
