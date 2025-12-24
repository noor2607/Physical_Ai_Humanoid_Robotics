
import sys
import os

# Add paths to sys.path
sys.path.insert(0, os.path.abspath('.'))      # backend dir
sys.path.insert(0, os.path.abspath('..'))     # root dir for connection module
sys.path.insert(0, os.path.abspath('./src'))  # src dir for imports

import uvicorn
from main import app

print("Starting server on http://localhost:8000")
print("Available routes:")
for route in app.routes:
    methods = ', '.join(list(route.methods))
    print(f"  {{methods}} {{route.path}}")

uvicorn.run(app, host="0.0.0.0", port=8000)
