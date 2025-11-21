
ORIGINAL PROJECT RUN:

cd /Users/shivrajkhose/Downloads/occam/podman
docker build -t occam_local .
docker run -d -p 8080:80 --name occam_local occam_local

![image.png](attachment:c78315e0-f695-4974-aaad-0e44ccb3f4af:image.png)

![image.png](attachment:040091b0-f164-4945-8258-7d7155de9d5e:image.png)

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

![image.png](attachment:43bda1b9-ff8b-4a6d-a546-b17254776302:image.png)

![image.png](attachment:5cfa24d5-405d-494e-b8c2-dc04824a9403:image.png)