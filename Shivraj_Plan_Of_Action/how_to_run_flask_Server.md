
ORIGINAL PROJECT RUN:

cd /Users/shivrajkhose/Downloads/occam/podman
docker build -t occam_local .
docker run -d -p 8080:80 --name occam_local occam_local

<img width="1636" height="618" alt="image" src="https://github.com/user-attachments/assets/068c2f4a-748d-4412-96cc-ba72291891f1" />

<img width="1574" height="660" alt="image" src="https://github.com/user-attachments/assets/50343fbd-b108-48bf-8bd0-7e99accede58" />


# Run From Python (Flask Version You Are Modifying)

1. Navigate to the Python directory:
cd /Users/shivrajkhose/Downloads/occam/py

2. Activate the virtual environment:
source venv/bin/activate

3. Install dependencies (if not already installed):
pip install -r requirements.txt

4. Run the Flask server:
python flask_occam.py

5. Access the application:
Open your browser and go to:
Main page: http://localhost:5002/

<img width="1548" height="634" alt="image" src="https://github.com/user-attachments/assets/1327c7dd-3022-43aa-b247-3a40c8f37383" />

<img width="1496" height="554" alt="image" src="https://github.com/user-attachments/assets/646627e0-e632-402d-8f32-e9426ea78ddf" />
