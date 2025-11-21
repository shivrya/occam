# OCCAM Project Architecture and Migration Overview

## Directory Structure Overview
- cpp/ – Core engine written in C++; computational heart of OCCAM.
- include/ – Interface definitions for all C++ classes.
- py/ – Python wrappers, scripts, and the new Flask-based web application.
- html/ – Web interface files (HTML templates and legacy CGI entry points).
- examples/ – Example data files for testing and learning.
- docs/ – User manuals, technical documents, and images.
- tests/ – Unit tests and test datasets.
- podman/ – Docker/Podman container configuration.

## Component Relationships
1. cpp/ contains the core algorithms; include/ defines their interfaces.
2. py/ wraps cpp/ functionality for easier use from Python.
3. html/ provides the web interface that calls into py/.
4. examples/ provides test data.
5. tests/ validates C++ functionality.
6. podman/ builds deployment containers.
7. docs/ documents the system.

## Original System (CGI + Apache)
- Entry Point: html/weboccam.cgi  
- Backend: py/weboccam.py (Python 2.7)  
- Interface: CGI

### Original Execution Flow
1. User submits form → HTTP POST  
2. Apache receives request and sees `.cgi`  
3. Apache executes CGI script  
4. CGI invokes Python script  
5. Python prints HTML to stdout  
6. Apache sends output back to browser

### Direct Execution from UI
#! /bin/sh  
/usr/bin/python2 weboccam.py 2>&1 | /usr/bin/tee mostRecentRun.txt

## Docker Version (Legacy)
Apache HTTP Server (port 80)  
↓  
CGI Handler  
↓  
weboccam.cgi → py/weboccam.py  
↓  
ocutils.py → occam.so (C++ library)  
↓  
RA computations

## Migration: Replacing CGI with Flask
Goal: Replace Apache/CGI with a modern Flask server while keeping backend logic unchanged.

### Changes Made
- Added py/app.py: Flask server exposing /occam; launches legacy weboccam.py using CGI-like env.
- Updated html/index.html: Changed link from weboccam.cgi to /occam.
- Updated html/switchform.html: Updated all onClick URLs from weboccam.cgi?... to /occam?... .
- Updated py/jobcontrol.py: Updated kill-job links from weboccam.cgi?action=jobcontrol&pid=... to /occam?action=jobcontrol&pid=....

## Running Flask Version
python3 -m venv venv  
source venv/bin/activate  
pip install -r requirements.txt  
python3 app.py  

Access in browser:  
http://localhost:5002/

## Python 2 vs Python 3 Issue
weboccam.py is Python 2–only.  
Running it under Python 3 causes SyntaxError (e.g., invalid octal literal 0660).

Fix:  
Install python2 and ensure Flask spawns weboccam.py with python2.

Example message:  
"Legacy weboccam.py requires Python 2.x. Please install python2 and ensure it is on PATH."

## Summary
You replaced Apache CGI with Flask while keeping legacy Python 2 and C++ computation intact. Flask routes requests to legacy weboccam.py, ensuring identical UI and output with a modern web server foundation.
