#!/usr/bin/env python3
"""
Live Server Deployment Verification Script
This script helps verify your live server deployment step by step
"""

import json
import sys
import os
from pathlib import Path

def check_live_server_files():
    """Check if all required files exist for deployment"""
    print("=== Checking Required Files for Live Server ===")
    
    required_files = [
        "app/main.py",
        "app/routes/auth.py", 
        "app/schemas/auth_schema.py",
        "app/services/auth_service.py",
        "app/core/database.py",
        "app/core/security.py",
        "app/crud/crud.py",
        "app/models/password_reset_token.py",
        "requirements.txt",
        ".env"  # This might not exist locally but needed on live server
    ]
    
    missing_files = []
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✓ {file_path}")
        else:
            print(f"✗ {file_path} - MISSING")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n❌ Missing files: {missing_files}")
        return False
    
    print("\n✅ All required files found")
    return True

def generate_deployment_commands():
    """Generate commands to run on live server"""
    print("\n=== Commands to Run on Your Live Server ===")
    
    commands = [
        "# 1. Check Python version (should be 3.9+)",
        "python --version",
        "",
        "# 2. Install/update dependencies", 
        "pip install -r requirements.txt",
        "",
        "# 3. Test imports",
        'python -c "from app.main import app; print(\'✅ App imports successfully\')"',
        "",
        "# 4. Verify auth routes",
        'python -c "from app.routes.auth import router; print(f\'✅ Found {len(router.routes)} auth routes\')"',
        "",
        "# 5. Check routes in main app",
        'python -c "from app.main import app; auth_routes = [r for r in app.routes if hasattr(r, \'path\') and \'/auth\' in r.path]; print(f\'✅ Auth routes in app: {len(auth_routes)}\')"',
        "",
        "# 6. Start server (replace with your production command)",
        "uvicorn app.main:app --host 0.0.0.0 --port 8000",
        "",
        "# 7. Test endpoints (run in another terminal)",
        "curl http://your-server:8000/docs",
        "curl http://your-server:8000/v1/auth/send-otp"
    ]
    
    for cmd in commands:
        print(cmd)

def create_deployment_files():
    """Create files needed for deployment"""
    
    # Create a simple deployment test script
    deployment_test = '''#!/usr/bin/env python3
"""Quick test script for live server"""
import sys

try:
    from app.main import app
    from app.routes.auth import router
    
    print(f"✅ FastAPI app created successfully")
    print(f"✅ Auth router has {len(router.routes)} routes")
    
    # Check if auth routes are in main app
    auth_routes = [r for r in app.routes if hasattr(r, 'path') and '/auth' in r.path]
    print(f"✅ Main app has {len(auth_routes)} auth routes")
    
    if len(auth_routes) == 6:
        print("🎉 SUCCESS: All auth routes are properly loaded!")
        sys.exit(0)
    else:
        print("❌ ERROR: Missing auth routes in main app")
        sys.exit(1)
        
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
'''
    
    with open("live_server_test.py", "w") as f:
        f.write(deployment_test)
    
    print(f"\n✅ Created: live_server_test.py")
    print("   → Upload this file to your live server and run: python live_server_test.py")

def check_git_status():
    """Check if there are uncommitted changes that need to be deployed"""
    print("\n=== Git Status Check ===")
    
    try:
        import subprocess
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True, cwd='.')
        
        if result.returncode == 0:
            changes = result.stdout.strip()
            if changes:
                print("⚠️  You have uncommitted changes:")
                print(changes)
                print("\n📝 Make sure to commit and push these changes to your live server:")
                print("git add .")
                print("git commit -m 'Fix Pydantic v2 compatibility and auth routes'")
                print("git push origin main")
            else:
                print("✅ No uncommitted changes - your code is ready for deployment")
        else:
            print("ℹ️  Not a git repository or git not available")
    except Exception as e:
        print(f"ℹ️  Could not check git status: {e}")

def main():
    print("🚀 CredoSafe Live Server Deployment Verification")
    print("=" * 60)
    
    # Run all checks
    files_ok = check_live_server_files()
    check_git_status()
    create_deployment_files()
    generate_deployment_commands()
    
    print("\n" + "=" * 60)
    print("📋 DEPLOYMENT STEPS:")
    print("1. Ensure all files are uploaded to your live server")
    print("2. Run the commands shown above on your live server")
    print("3. Upload and run live_server_test.py on your live server")
    print("4. Check /docs endpoint on your live server")
    print("5. If still missing, check server logs for errors")
    
    if files_ok:
        print("\n✅ Local files look good - the issue is likely on the live server deployment")
    else:
        print("\n❌ Missing files locally - fix these before deploying")

if __name__ == "__main__":
    main()