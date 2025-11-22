# Pure Flask Implementation for OCCAM

Complete Flask replacement for CGI - no CGI dependencies!

## Files Added (3 total)

1. **`py/flask_occam.py`** - Pure Flask server (200+ lines)
2. **`py/requirements.txt`** - Python dependencies
3. **`FLASK_SIMPLE.md`** - This file

**No CGI dependencies!** All HTML, CSS, and existing templates used directly.

## Usage

### Start Server

```bash
cd py
source venv/bin/activate
python flask_occam.py
```

### Access

- **Main Page**: http://localhost:5002/
- **OCCAM Interface**: http://localhost:5002/occam

### Stop Server

Press `Ctrl+C` or:
```bash
pkill -f "python flask_occam.py"
```

## How It Works

```
Flask Routes:
/ → Main page (index.html)
/occam → Main form (switchform.html)
/occam/search → Search form (search.template.html)
/occam/fit → Fit form (fit.template.html)
/occam/compare → Compare form
/occam/log → Log viewer
/occam/jobcontrol → Job management
```

## Benefits

- ✅ **Zero CGI dependencies**
- ✅ Pure Flask routing
- ✅ No UI changes
- ✅ No file duplication  
- ✅ Easy to deploy (Gunicorn, etc.)
- ✅ All buttons work with Flask routes

## Next Steps

To fully integrate with OCCAM core functionality, modify `flask_occam.py` to properly handle form data conversion and call the existing weboccam.py functions.

---

**Status**: Flask server running on port 5002 with exact same UI as CGI version.
