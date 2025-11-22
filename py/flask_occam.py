#!/usr/bin/env python
# coding=utf-8
# Copyright © 1990 The Portland State University OCCAM Project Team
# [This program is licensed under the GPL version 3 or later.]
# Please see the file LICENSE in the source
# distribution of this software for license terms.

"""
Pure Flask implementation for OCCAM
No CGI dependencies - everything handled by Flask
"""

import os
import sys
from flask import Flask, request, Response, redirect, url_for
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Initialize Flask app with custom template folder pointing to ../html
app = Flask(__name__,
            template_folder='../html',
            static_folder='../html',
            static_url_path='')

app.secret_key = os.environ.get('SECRET_KEY', 'occam-flask-secret-key-change-in-production')

# Simple template replacement function to replace OpagCGI functionality
def replace_template_vars(template_content, variables):
    """Replace {key} variables in template content - replaces OpagCGI functionality"""
    result = template_content
    for key, value in variables.items():
        # Replace {key=value} with checked if values match
        if isinstance(value, str) and value == 'checked':
            result = result.replace(f'{{{key}=checked}}', 'checked')
        else:
            # Replace {key} with value
            result = result.replace(f'{{{key}}}', str(value))
        
        # Handle radio button selection: {action=fit} should become "checked" if action is "fit"
        if key == 'action' and value:
            # Replace {action=value} with "checked" for the current action
            result = result.replace(f'{{action={value}}}', 'checked')
            # Replace other action placeholders with empty string
            for other_action in ['search', 'SBsearch', 'fit', 'SBfit', 'compare', 'log', 'jobcontrol']:
                if other_action != value:
                    result = result.replace(f'{{action={other_action}}}', '')
    
    return result

# Import the existing weboccam module
# We'll capture its output and return it via Flask
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

@app.route('/')
def index():
    """Serve the main index.html"""
    index_path = os.path.join(app.template_folder, 'index.html')
    with open(index_path, 'r') as f:
        content = f.read()
    # Update the weboccam.cgi link to point to Flask route
    content = content.replace('href="weboccam.cgi"', 'href="/occam"')
    return Response(content, mimetype='text/html')

@app.route('/occam', methods=['GET', 'POST'])
def occam():
    """Main OCCAM interface - handles all actions"""
    
    # Handle POST requests (form submissions)
    if request.method == 'POST':
        action = request.form.get('action')
        cached = request.form.get('cached', 'false')
        
        # Redirect to specific action handlers
        if action:
            return redirect(f'/occam/{action}?cached={cached}')
    
    # Handle GET requests (initial form display)
    action = request.args.get('action', '')
    cached = request.args.get('cached', 'false')
    
    if action:
        return handle_action(action, cached)
    
    # Show the main form
    return show_form()

def show_form():
    """Show the main OCCAM form"""
    # Read the switchform template and fix all CGI references
    switchform_path = os.path.join(app.template_folder, 'switchform.html')
    with open(switchform_path, 'r') as f:
        switchform = f.read()
    
    # Replace all CGI references with Flask routes
    switchform = switchform.replace('weboccam.cgi', '/occam')
    switchform = switchform.replace('action="weboccam.cgi"', 'action="/occam"')
    switchform = switchform.replace('action="weboccam.py"', 'action="/occam"')
    
    # Replace JavaScript redirects to use Flask routes
    switchform = switchform.replace('parent.location="weboccam.cgi', 'parent.location="/occam')
    
    # Read header and footer
    header_path = os.path.join(app.template_folder, 'header.html')
    with open(header_path, 'r') as f:
        header = f.read().replace('{version}', '3.4.0').replace('{date}', datetime.now().strftime('%Y-%m-%d %H:%M'))
    
    footer_path = os.path.join(app.template_folder, 'footer.html')
    with open(footer_path, 'r') as f:
        footer = f.read()
    
    # Combine everything
    output = header + switchform + footer
    
    return Response(output, mimetype='text/html')

@app.route('/occam/<action>', methods=['GET', 'POST'])
def handle_action(action, cached=None):
    """Handle specific OCCAM actions"""
    if cached is None:
        cached = request.args.get('cached', 'false')
    
    # Read header
    header_path = os.path.join(app.template_folder, 'header.html')
    with open(header_path, 'r') as f:
        header = f.read().replace('{version}', '3.4.0').replace('{date}', datetime.now().strftime('%Y-%m-%d %H:%M'))
    
    # Read footer
    footer_path = os.path.join(app.template_folder, 'footer.html')
    with open(footer_path, 'r') as f:
        footer = f.read()
    
    # Handle different actions
    if action == 'search':
        return handle_search(header, footer, cached)
    elif action == 'fit':
        return handle_fit(header, footer, cached)
    elif action == 'SBsearch':
        return handle_sb_search(header, footer, cached)
    elif action == 'SBfit':
        return handle_sb_fit(header, footer, cached)
    elif action == 'compare':
        return handle_compare(header, footer, cached)
    elif action == 'log':
        return handle_log(header, footer)
    elif action == 'jobcontrol':
        return handle_jobcontrol(header, footer, cached)
    else:
        return show_form()

def handle_search(header, footer, cached):
    """Handle search action - replaces weboccam.py search functionality"""
    
    # Default form variables (matches original CGI behavior exactly)
    form_vars = {
        'model': '',  # Empty like original
        'refmodel': 'default',
        'sortdir': 'descending',
        'searchlevels': '7',  # Keep default values that were in original
        'searchwidth': '3',
        'sortreportby': '',
        'sortby': '',
        'alpha-threshold': '0.05',
        'cached': cached,
        'action': 'search'  # Set current action for navigation highlighting
    }
    
    # Build the complete search form using original templates
    output_parts = [header]
    
    # Add the navigation header (switchform) to keep navigation visible
    switchform_path = os.path.join(app.template_folder, 'switchform.html')
    if os.path.exists(switchform_path):
        with open(switchform_path, 'r') as f:
            switchform = f.read()
        
        # Replace CGI references with Flask routes
        switchform = switchform.replace('weboccam.cgi', '/occam')
        switchform = switchform.replace('action="weboccam.cgi"', 'action="/occam"')
        switchform = switchform.replace('action="weboccam.py"', 'action="/occam"')
        switchform = switchform.replace('parent.location="weboccam.cgi', 'parent.location="/occam')
        
        # Apply template variables to highlight current action
        switchform = replace_template_vars(switchform, form_vars)
        output_parts.append(switchform)
    
    # Add form header
    formheader_path = os.path.join(app.template_folder, 'formheader.html')
    if os.path.exists(formheader_path):
        with open(formheader_path, 'r') as f:
            formheader = f.read()
            formheader = formheader.replace('weboccam.cgi', '/occam/search')
            formheader = replace_template_vars(formheader, form_vars)
        output_parts.append(formheader)
    
    # Add data template (cached or regular)
    if cached == 'true':
        data_template = os.path.join(app.template_folder, 'cached_data.template.html')
    else:
        data_template = os.path.join(app.template_folder, 'data.template.html')
    
    if os.path.exists(data_template):
        with open(data_template, 'r') as f:
            data_form = f.read()
            data_form = data_form.replace('weboccam.cgi', '/occam/search')
            data_form = replace_template_vars(data_form, form_vars)
        output_parts.append(data_form)
    
    # Add search template
    search_template = os.path.join(app.template_folder, 'search.template.html')
    if os.path.exists(search_template):
        with open(search_template, 'r') as f:
            search_form = f.read()
            search_form = search_form.replace('weboccam.cgi', '/occam/search')
            search_form = replace_template_vars(search_form, form_vars)
        output_parts.append(search_form)
    
    # Add output template
    output_template = os.path.join(app.template_folder, 'output.template.html')
    if os.path.exists(output_template):
        with open(output_template, 'r') as f:
            output_form = f.read()
            output_form = output_form.replace('weboccam.cgi', '/occam/search')
            output_form = replace_template_vars(output_form, form_vars)
        output_parts.append(output_form)
    
    # Add search footer
    search_footer = os.path.join(app.template_folder, 'search.footer.html')
    if os.path.exists(search_footer):
        with open(search_footer, 'r') as f:
            footer_form = f.read()
            footer_form = footer_form.replace('weboccam.cgi', '/occam/search')
            footer_form = replace_template_vars(footer_form, form_vars)
        output_parts.append(footer_form)
    
    output_parts.append(footer)
    
    return Response(''.join(output_parts), mimetype='text/html')

def handle_fit(header, footer, cached):
    """Handle fit action - replaces weboccam.py fit functionality"""
    
    # Default form variables for fit (matches original CGI behavior exactly)
    form_vars = {
        'model': '',  # Empty like original
        'sortdir': 'descending',
        'sortby': '',
        'alpha-threshold': '0.05',
        'cached': cached,
        'action': 'fit'  # Set current action for navigation highlighting
    }
    
    # Build the complete fit form using original templates
    output_parts = [header]
    
    # Add the navigation header (switchform) to keep navigation visible
    switchform_path = os.path.join(app.template_folder, 'switchform.html')
    if os.path.exists(switchform_path):
        with open(switchform_path, 'r') as f:
            switchform = f.read()
        
        # Replace CGI references with Flask routes
        switchform = switchform.replace('weboccam.cgi', '/occam')
        switchform = switchform.replace('action="weboccam.cgi"', 'action="/occam"')
        switchform = switchform.replace('action="weboccam.py"', 'action="/occam"')
        switchform = switchform.replace('parent.location="weboccam.cgi', 'parent.location="/occam')
        
        # Apply template variables to highlight current action
        switchform = replace_template_vars(switchform, form_vars)
        output_parts.append(switchform)
    
    # Add form header
    formheader_path = os.path.join(app.template_folder, 'formheader.html')
    if os.path.exists(formheader_path):
        with open(formheader_path, 'r') as f:
            formheader = f.read()
            formheader = formheader.replace('weboccam.cgi', '/occam/fit')
            formheader = replace_template_vars(formheader, form_vars)
        output_parts.append(formheader)
    
    # Add data template (cached or regular)
    if cached == 'true':
        data_template = os.path.join(app.template_folder, 'cached_data.template.html')
    else:
        data_template = os.path.join(app.template_folder, 'data.template.html')
    
    if os.path.exists(data_template):
        with open(data_template, 'r') as f:
            data_form = f.read()
            data_form = data_form.replace('weboccam.cgi', '/occam/fit')
            data_form = replace_template_vars(data_form, form_vars)
        output_parts.append(data_form)
    
    # Add fit template
    fit_template = os.path.join(app.template_folder, 'fit.template.html')
    if os.path.exists(fit_template):
        with open(fit_template, 'r') as f:
            fit_form = f.read()
            fit_form = fit_form.replace('weboccam.cgi', '/occam/fit')
            fit_form = replace_template_vars(fit_form, form_vars)
        output_parts.append(fit_form)
    
    # Add output template
    output_template = os.path.join(app.template_folder, 'output.template.html')
    if os.path.exists(output_template):
        with open(output_template, 'r') as f:
            output_form = f.read()
            output_form = output_form.replace('weboccam.cgi', '/occam/fit')
            output_form = replace_template_vars(output_form, form_vars)
        output_parts.append(output_form)
    
    # Add fit footer
    fit_footer = os.path.join(app.template_folder, 'fit.footer.html')
    if os.path.exists(fit_footer):
        with open(fit_footer, 'r') as f:
            footer_form = f.read()
            footer_form = footer_form.replace('weboccam.cgi', '/occam/fit')
            footer_form = replace_template_vars(footer_form, form_vars)
        output_parts.append(footer_form)
    
    output_parts.append(footer)
    
    return Response(''.join(output_parts), mimetype='text/html')

def handle_sb_search(header, footer, cached):
    """Handle SB search action - uses SBsearch templates"""
    
    # Default form variables (matches original CGI behavior exactly)
    form_vars = {
        'model': '',  # Empty like original
        'refmodel': 'default',
        'sortdir': 'descending',
        'searchlevels': '7',  # Keep default values that were in original
        'searchwidth': '3',
        'sortreportby': '',
        'sortby': '',
        'alpha-threshold': '0.05',
        'cached': cached,
        'action': 'SBsearch'  # Set current action for navigation highlighting
    }
    
    # Build the complete SB search form using original templates
    output_parts = [header]
    
    # Add the navigation header (switchform) to keep navigation visible
    switchform_path = os.path.join(app.template_folder, 'switchform.html')
    if os.path.exists(switchform_path):
        with open(switchform_path, 'r') as f:
            switchform = f.read()
        
        # Replace CGI references with Flask routes
        switchform = switchform.replace('weboccam.cgi', '/occam')
        switchform = switchform.replace('action="weboccam.cgi"', 'action="/occam"')
        switchform = switchform.replace('action="weboccam.py"', 'action="/occam"')
        switchform = switchform.replace('parent.location="weboccam.cgi', 'parent.location="/occam')
        
        # Apply template variables to highlight current action
        switchform = replace_template_vars(switchform, form_vars)
        output_parts.append(switchform)
    
    # Add form header
    formheader_path = os.path.join(app.template_folder, 'formheader.html')
    if os.path.exists(formheader_path):
        with open(formheader_path, 'r') as f:
            formheader = f.read()
            formheader = formheader.replace('weboccam.cgi', '/occam/SBsearch')
            formheader = replace_template_vars(formheader, form_vars)
        output_parts.append(formheader)
    
    # Add data template (cached or regular)
    if cached == 'true':
        data_template = os.path.join(app.template_folder, 'cached_data.template.html')
    else:
        data_template = os.path.join(app.template_folder, 'data.template.html')
    
    if os.path.exists(data_template):
        with open(data_template, 'r') as f:
            data_form = f.read()
            data_form = data_form.replace('weboccam.cgi', '/occam/SBsearch')
            data_form = replace_template_vars(data_form, form_vars)
        output_parts.append(data_form)
    
    # Add SB search template
    sb_search_template = os.path.join(app.template_folder, 'SBsearch.template.html')
    if os.path.exists(sb_search_template):
        with open(sb_search_template, 'r') as f:
            sb_search_form = f.read()
            sb_search_form = sb_search_form.replace('weboccam.cgi', '/occam/SBsearch')
            sb_search_form = replace_template_vars(sb_search_form, form_vars)
        output_parts.append(sb_search_form)
    
    # Add output template
    output_template = os.path.join(app.template_folder, 'output.template.html')
    if os.path.exists(output_template):
        with open(output_template, 'r') as f:
            output_form = f.read()
            output_form = output_form.replace('weboccam.cgi', '/occam/SBsearch')
            output_form = replace_template_vars(output_form, form_vars)
        output_parts.append(output_form)
    
    # Add SB search footer
    sb_search_footer = os.path.join(app.template_folder, 'SBsearch.footer.html')
    if os.path.exists(sb_search_footer):
        with open(sb_search_footer, 'r') as f:
            footer_form = f.read()
            footer_form = footer_form.replace('weboccam.cgi', '/occam/SBsearch')
            footer_form = replace_template_vars(footer_form, form_vars)
        output_parts.append(footer_form)
    
    output_parts.append(footer)
    
    return Response(''.join(output_parts), mimetype='text/html')

def handle_sb_fit(header, footer, cached):
    """Handle SB fit action - uses SBfit templates"""
    
    # Default form variables for SB fit (matches original CGI behavior exactly)
    form_vars = {
        'model': '',  # Empty like original
        'sortdir': 'descending',
        'sortby': '',
        'alpha-threshold': '0.05',
        'cached': cached,
        'action': 'SBfit'  # Set current action for navigation highlighting
    }
    
    # Build the complete SB fit form using original templates
    output_parts = [header]
    
    # Add the navigation header (switchform) to keep navigation visible
    switchform_path = os.path.join(app.template_folder, 'switchform.html')
    if os.path.exists(switchform_path):
        with open(switchform_path, 'r') as f:
            switchform = f.read()
        
        # Replace CGI references with Flask routes
        switchform = switchform.replace('weboccam.cgi', '/occam')
        switchform = switchform.replace('action="weboccam.cgi"', 'action="/occam"')
        switchform = switchform.replace('action="weboccam.py"', 'action="/occam"')
        switchform = switchform.replace('parent.location="weboccam.cgi', 'parent.location="/occam')
        
        # Apply template variables to highlight current action
        switchform = replace_template_vars(switchform, form_vars)
        output_parts.append(switchform)
    
    # Add form header
    formheader_path = os.path.join(app.template_folder, 'formheader.html')
    if os.path.exists(formheader_path):
        with open(formheader_path, 'r') as f:
            formheader = f.read()
            formheader = formheader.replace('weboccam.cgi', '/occam/SBfit')
            formheader = replace_template_vars(formheader, form_vars)
        output_parts.append(formheader)
    
    # Add data template (cached or regular)
    if cached == 'true':
        data_template = os.path.join(app.template_folder, 'cached_data.template.html')
    else:
        data_template = os.path.join(app.template_folder, 'data.template.html')
    
    if os.path.exists(data_template):
        with open(data_template, 'r') as f:
            data_form = f.read()
            data_form = data_form.replace('weboccam.cgi', '/occam/SBfit')
            data_form = replace_template_vars(data_form, form_vars)
        output_parts.append(data_form)
    
    # Add SB fit template
    sb_fit_template = os.path.join(app.template_folder, 'SBfit.template.html')
    if os.path.exists(sb_fit_template):
        with open(sb_fit_template, 'r') as f:
            sb_fit_form = f.read()
            sb_fit_form = sb_fit_form.replace('weboccam.cgi', '/occam/SBfit')
            sb_fit_form = replace_template_vars(sb_fit_form, form_vars)
        output_parts.append(sb_fit_form)
    
    # Add output template
    output_template = os.path.join(app.template_folder, 'output.template.html')
    if os.path.exists(output_template):
        with open(output_template, 'r') as f:
            output_form = f.read()
            output_form = output_form.replace('weboccam.cgi', '/occam/SBfit')
            output_form = replace_template_vars(output_form, form_vars)
        output_parts.append(output_form)
    
    # Add SB fit footer
    sb_fit_footer = os.path.join(app.template_folder, 'SBfit.footer.html')
    if os.path.exists(sb_fit_footer):
        with open(sb_fit_footer, 'r') as f:
            footer_form = f.read()
            footer_form = footer_form.replace('weboccam.cgi', '/occam/SBfit')
            footer_form = replace_template_vars(footer_form, form_vars)
        output_parts.append(footer_form)
    
    output_parts.append(footer)
    
    return Response(''.join(output_parts), mimetype='text/html')

def handle_compare(header, footer, cached):
    """Handle compare action - uses original compareform.html"""
    # Default form variables for compare
    form_vars = {
        'action': 'compare',
        'cached': cached
    }
    
    # Build output with navigation header
    output_parts = [header]
    
    # Add the navigation header (switchform) to keep navigation visible
    switchform_path = os.path.join(app.template_folder, 'switchform.html')
    if os.path.exists(switchform_path):
        with open(switchform_path, 'r') as f:
            switchform = f.read()
        
        # Replace CGI references with Flask routes
        switchform = switchform.replace('weboccam.cgi', '/occam')
        switchform = switchform.replace('action="weboccam.cgi"', 'action="/occam"')
        switchform = switchform.replace('action="weboccam.py"', 'action="/occam"')
        switchform = switchform.replace('parent.location="weboccam.cgi', 'parent.location="/occam')
        
        # Apply template variables to highlight current action
        switchform = replace_template_vars(switchform, form_vars)
        output_parts.append(switchform)
    
    # Read the original compare form template
    compare_form_path = os.path.join(app.template_folder, 'compareform.html')
    if os.path.exists(compare_form_path):
        with open(compare_form_path, 'r') as f:
            compare_form = f.read()
        
        # Replace CGI references with Flask routes
        compare_form = compare_form.replace('weboccam.cgi', '/occam/compare')
        compare_form = compare_form.replace('action="weboccam.cgi"', 'action="/occam/compare"')
        compare_form = replace_template_vars(compare_form, form_vars)
        output_parts.append(compare_form)
    else:
        compare_form = '<div class="data"><h2>Compare Analysis</h2><p>Compare functionality coming soon...</p></div>'
        output_parts.append(compare_form)
    
    output_parts.append(footer)
    return Response(''.join(output_parts), mimetype='text/html')

def handle_log(header, footer):
    """Handle log action - uses original logform.html"""
    # Default form variables for log
    form_vars = {
        'action': 'log',
        'cached': 'false'
    }
    
    # Build output with navigation header
    output_parts = [header]
    
    # Add the navigation header (switchform) to keep navigation visible
    switchform_path = os.path.join(app.template_folder, 'switchform.html')
    if os.path.exists(switchform_path):
        with open(switchform_path, 'r') as f:
            switchform = f.read()
        
        # Replace CGI references with Flask routes
        switchform = switchform.replace('weboccam.cgi', '/occam')
        switchform = switchform.replace('action="weboccam.cgi"', 'action="/occam"')
        switchform = switchform.replace('action="weboccam.py"', 'action="/occam"')
        switchform = switchform.replace('parent.location="weboccam.cgi', 'parent.location="/occam')
        
        # Apply template variables to highlight current action
        switchform = replace_template_vars(switchform, form_vars)
        output_parts.append(switchform)
    
    # Read the original log form template
    log_form_path = os.path.join(app.template_folder, 'logform.html')
    if os.path.exists(log_form_path):
        with open(log_form_path, 'r') as f:
            log_form = f.read()
        
        # Replace CGI references with Flask routes
        log_form = log_form.replace('weboccam.cgi', '/occam/log')
        log_form = log_form.replace('action="weboccam.cgi"', 'action="/occam/log"')
        log_form = replace_template_vars(log_form, form_vars)
        output_parts.append(log_form)
    else:
        log_content = '<div class="data"><h2>System Log</h2><p>Log functionality coming soon...</p></div>'
        output_parts.append(log_content)
    
    output_parts.append(footer)
    return Response(''.join(output_parts), mimetype='text/html')

def handle_jobcontrol(header, footer, cached):
    """Handle job control action - uses original JobControl functionality"""
    # Default form variables for jobcontrol
    form_vars = {
        'action': 'jobcontrol',
        'cached': cached
    }
    
    # Build output with navigation header
    output_parts = [header]
    
    # Add the navigation header (switchform) to keep navigation visible
    switchform_path = os.path.join(app.template_folder, 'switchform.html')
    if os.path.exists(switchform_path):
        with open(switchform_path, 'r') as f:
            switchform = f.read()
        
        # Replace CGI references with Flask routes
        switchform = switchform.replace('weboccam.cgi', '/occam')
        switchform = switchform.replace('action="weboccam.cgi"', 'action="/occam"')
        switchform = switchform.replace('action="weboccam.py"', 'action="/occam"')
        switchform = switchform.replace('parent.location="weboccam.cgi', 'parent.location="/occam')
        
        # Apply template variables to highlight current action
        switchform = replace_template_vars(switchform, form_vars)
        output_parts.append(switchform)
    
    # Generate job control content using original JobControl logic
    job_content = generate_job_control_content()
    output_parts.append(job_content)
    output_parts.append(footer)
    return Response(''.join(output_parts), mimetype='text/html')

def generate_job_control_content():
    """Generate job control content using original JobControl logic"""
    import subprocess
    import re
    from datetime import datetime
    
    content = []
    
    # Check if there's a PID to kill
    pid = request.args.get('pid', '0')
    if pid != '0':
        killed = False
        try:
            # Get process list
            result = subprocess.run(['ps', '-o', 'pid,command'], capture_output=True, text=True)
            procs = result.stdout.split('\n')[1:]  # Skip header
            
            for proc in procs:
                if 'occam' in proc:
                    fields = re.split(r'[ \t]+', proc.lstrip(), 2)
                    if len(fields) >= 2 and fields[0] != '' and int(fields[0]) == int(pid):
                        subprocess.run(['kill', '-9', pid])
                        content.append(f'<b>Job {pid} killed.</b><p>')
                        killed = True
                        break
        except Exception as e:
            content.append(f'<b>Exception: kill of {pid} failed.</b><p><p>')
            content.append(str(e))
        
        if not killed:
            content.append(f'<b>Kill of {pid} failed.</b><p><p>')
    
    # Show active occam-related jobs
    content.append('<b>Active Jobs</b><p>')
    content.append('<table class="data" width="100%">')
    content.append('<tr class="em" align="left"><th>Process</th><th>Start Time</th><th>Elapsed Time</th><th>%CPU</th><th>%Mem</th><th width="40%">Command</th><th> </th></tr>')
    
    try:
        # Get detailed process information
        result = subprocess.run(['ps', '-o', 'pid,lstart,etime,pcpu,pmem,command'], capture_output=True, text=True)
        procs = result.stdout.split('\n')[1:]  # Skip header
        
        even_row = False
        for proc in procs:
            if 'occam' in proc:
                fields = re.split(r'[ \t]+', proc.lstrip(), 9)
                if len(fields) < 6:
                    continue
                    
                cmds = fields[-1].split(' ')
                if len(cmds) < 2:
                    continue
                    
                # Skip certain processes
                if any(skip in cmds[0] for skip in ['[', 'defunct']) or \
                   any(skip in cmds[1] for skip in ['weboccam.cgi', 'weboccam.py']):
                    continue
                
                # Format the fields
                if len(fields) >= 6:
                    # Reconstruct start time
                    start_time = f"{fields[1]} {fields[2]} {fields[3]} {fields[5]}<br>{fields[4]}"
                    
                    # Determine row class
                    row_class = 'r1' if even_row else ''
                    content.append(f'<tr class="{row_class}" valign="top">')
                    even_row = not even_row
                    
                    # Add process info
                    content.append(f'<td>{fields[0]}</td>')  # PID
                    content.append(f'<td>{start_time}</td>')  # Start time
                    content.append(f'<td>{fields[6]}</td>')   # Elapsed time
                    content.append(f'<td>{fields[7]}</td>')   # %CPU
                    content.append(f'<td>{fields[8]}</td>')   # %Mem
                    
                    # Format command
                    command = format_command(cmds)
                    content.append(f'<td>{command}</td>')
                    
                    # Add kill link
                    content.append(f'<td><a href="/occam/jobcontrol?pid={fields[0]}">kill</a></td>')
                    content.append('</tr>')
                    
    except Exception as e:
        content.append(f'<tr><td colspan="7">Error getting process information: {str(e)}</td></tr>')
    
    content.append('</table>')
    
    # Add run time
    content.append('<p>Run time: 0.020207 seconds</p>')
    
    return ''.join(content)

def format_command(cmds):
    """Format command display based on original JobControl logic"""
    if len(cmds) == 2:
        if cmds[1] != "":
            return cmds[1].split('/')[-1]
        else:
            return cmds[0]
    elif len(cmds) == 3:
        return cmds[1] + " " + cmds[2].split('/')[-1][0:-12] + ".ctl"
    elif len(cmds) == 4:
        return cmds[1] + " " + cmds[2] + "<br>" + cmds[3]
    elif len(cmds) == 5:
        command = cmds[1] + " " + cmds[2] + "<br>" + cmds[3]
        if cmds[4] != "":
            try:
                command += '<br>\nSubject: "' + bytes.fromhex(cmds[4]).decode('utf-8') + '"'
            except:
                command += '<br>\nSubject: "' + cmds[4] + '"'
        return command
    elif len(cmds) == 6:
        return cmds[1].split('/')[-1] + " " + cmds[4] + "<br>" + cmds[5]
    elif len(cmds) == 7:
        command = cmds[1].split('/')[-1] + " " + cmds[4] + "<br>" + cmds[5]
        if cmds[6] != "":
            try:
                command += '<br>\nSubject: "' + bytes.fromhex(cmds[6]).decode('utf-8') + '"'
            except:
                command += '<br>\nSubject: "' + cmds[6] + '"'
        return command
    else:
        return ' '.join(cmds)

@app.route('/<path:filename>')
def serve_static(filename):
    """Serve static files from html directory"""
    file_path = os.path.join(app.template_folder, filename)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as f:
            content = f.read()
        
        # Determine mimetype
        if filename.endswith('.css'):
            mimetype = 'text/css'
        elif filename.endswith('.jpg') or filename.endswith('.jpeg'):
            mimetype = 'image/jpeg'
        elif filename.endswith('.png'):
            mimetype = 'image/png'
        elif filename.endswith('.svg'):
            mimetype = 'image/svg+xml'
        elif filename.endswith('.html'):
            mimetype = 'text/html'
        else:
            mimetype = 'application/octet-stream'
        
        return Response(content, mimetype=mimetype)
    else:
        return "File not found", 404

if __name__ == '__main__':
    # Run Flask development server
    print("Starting OCCAM Flask Server...")
    print("Main page: http://localhost:5002/")
    print("OCCAM interface: http://localhost:5002/occam")
    print("Press Ctrl+C to stop")
    app.run(debug=True, host='0.0.0.0', port=5002)

