#!/usr/bin/env python3
"""Quick test script for live server"""
import sys

try:
    from app.main import app
    from app.routes.auth import router
    
    print("SUCCESS: FastAPI app created successfully")
    print(f"SUCCESS: Auth router has {len(router.routes)} routes")
    
    # Check if auth routes are in main app
    auth_routes = [r for r in app.routes if hasattr(r, 'path') and '/auth' in r.path]
    print(f"SUCCESS: Main app has {len(auth_routes)} auth routes")
    
    if len(auth_routes) == 6:
        print("SUCCESS: All auth routes are properly loaded!")
        sys.exit(0)
    else:
        print("ERROR: Missing auth routes in main app")
        sys.exit(1)
        
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
