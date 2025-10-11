#!/usr/bin/env python3
"""
Diagnostic script to check what might be causing auth routes to not load on live server
"""

import sys
import os
import traceback

def check_imports():
    """Check if all required modules can be imported"""
    print("=== Checking Imports ===")
    
    try:
        import fastapi
        print(f"✓ FastAPI: {fastapi.__version__}")
    except ImportError as e:
        print(f"✗ FastAPI import failed: {e}")
        return False
    
    try:
        from app.routes import auth
        print("✓ Auth routes imported successfully")
    except ImportError as e:
        print(f"✗ Auth routes import failed: {e}")
        traceback.print_exc()
        return False
    
    try:
        from app.schemas.auth_schema import SendOTPSchema
        print("✓ Auth schemas imported successfully")
    except ImportError as e:
        print(f"✗ Auth schemas import failed: {e}")
        traceback.print_exc()
        return False
    
    try:
        from app.services.auth_service import AuthService
        print("✓ Auth service imported successfully")
    except ImportError as e:
        print(f"✗ Auth service import failed: {e}")
        traceback.print_exc()
        return False
    
    try:
        from app.crud import crud
        print("✓ CRUD imported successfully")
    except ImportError as e:
        print(f"✗ CRUD import failed: {e}")
        traceback.print_exc()
        return False
    
    return True

def check_auth_routes():
    """Check auth routes configuration"""
    print("\n=== Checking Auth Routes ===")
    
    try:
        from app.routes.auth import router
        routes = []
        for route in router.routes:
            routes.append(f"{list(route.methods)} {route.path}")
        
        print(f"Found {len(router.routes)} auth routes:")
        for route_info in routes:
            print(f"  {route_info}")
        
        expected_routes = [
            "/send-otp",
            "/verify-otp", 
            "/set-password",
            "/login",
            "/forgot-password",
            "/reset-password"
        ]
        
        actual_paths = [route.path for route in router.routes]
        missing = [route for route in expected_routes if route not in actual_paths]
        
        if missing:
            print(f"✗ Missing routes: {missing}")
            return False
        else:
            print("✓ All expected auth routes found")
            return True
            
    except Exception as e:
        print(f"✗ Error checking auth routes: {e}")
        traceback.print_exc()
        return False

def check_main_app():
    """Check if main app can be created"""
    print("\n=== Checking Main App ===")
    
    try:
        from app.main import app
        print("✓ Main app imported successfully")
        
        # Check if auth routes are included
        auth_routes_found = False
        for route in app.routes:
            if hasattr(route, 'path') and route.path.startswith('/v1/auth'):
                auth_routes_found = True
                break
        
        if auth_routes_found:
            print("✓ Auth routes found in main app")
            return True
        else:
            print("✗ Auth routes NOT found in main app")
            return False
            
    except Exception as e:
        print(f"✗ Error creating main app: {e}")
        traceback.print_exc()
        return False

def check_environment():
    """Check environment and dependencies"""
    print("\n=== Environment Check ===")
    print(f"Python version: {sys.version}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Python path: {sys.path}")
    
    # Check if app directory is in path
    app_dir = os.path.join(os.getcwd(), 'app')
    if os.path.exists(app_dir):
        print(f"✓ App directory exists: {app_dir}")
    else:
        print(f"✗ App directory missing: {app_dir}")

def main():
    """Run all diagnostics"""
    print("CredoSafe Server Diagnostics")
    print("=" * 50)
    
    results = []
    results.append(("Environment", check_environment()))
    results.append(("Imports", check_imports()))
    results.append(("Auth Routes", check_auth_routes()))
    results.append(("Main App", check_main_app()))
    
    print("\n" + "=" * 50)
    print("SUMMARY:")
    
    all_passed = True
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{test_name}: {status}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n🎉 All checks passed! Auth routes should work.")
    else:
        print("\n❌ Some checks failed. Fix the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    main()