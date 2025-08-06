#!/usr/bin/env python3
"""
Generate requirements.txt from current virtual environment
This ensures all exact versions are captured for Docker builds
"""

import subprocess
import sys
import os

def generate_requirements():
    """Generate requirements.txt from current environment"""
    
    print("🔍 Generating requirements.txt from virtual environment...")
    
    # Check if we're in a virtual environment
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠️  Warning: Not in a virtual environment!")
        print("   Please activate your virtual environment first:")
        print("   source .myenv/bin/activate")
        return False
    
    try:
        # Generate requirements with exact versions using .myenv pip
        print("📦 Capturing installed packages from .myenv...")

        # Use the virtual environment's pip directly
        venv_pip = ".myenv/bin/pip"
        if not os.path.exists(venv_pip):
            print("❌ .myenv/bin/pip not found!")
            print("   Please ensure .myenv virtual environment exists")
            return False

        result = subprocess.run(
            [venv_pip, "freeze"],
            capture_output=True,
            text=True,
            check=True
        )
        
        # Filter out unnecessary packages and add header
        packages = result.stdout.strip().split('\n')
        
        # Filter out development packages and local packages
        filtered_packages = []
        skip_packages = {
            'pip', 'setuptools', 'wheel', 'pkg-resources'
        }
        
        for package in packages:
            if package and not package.startswith('-e '):
                package_name = package.split('==')[0].split('>=')[0].split('<=')[0]
                if package_name.lower() not in skip_packages:
                    filtered_packages.append(package)
        
        # Create requirements.txt with header
        requirements_content = f"""# =============================================================================
# MCP Memory Server - Docker Requirements (Auto-generated)
# Generated from virtual environment on {subprocess.run(['date'], capture_output=True, text=True).stdout.strip()}
# =============================================================================

# Core MCP and Memory Server Dependencies
{chr(10).join(sorted(filtered_packages))}

# =============================================================================
# Installation Notes for Docker:
# =============================================================================
# This file contains exact versions from the working virtual environment
# to ensure consistent Docker builds across different systems.
# 
# To regenerate: python generate_requirements.py
# =============================================================================
"""
        
        # Write to requirements.txt
        with open('requirements.txt', 'w') as f:
            f.write(requirements_content)
        
        print(f"✅ Generated requirements.txt with {len(filtered_packages)} packages")
        print("📄 File contents preview:")
        print("-" * 50)
        
        # Show first 10 packages
        for i, package in enumerate(sorted(filtered_packages)[:10]):
            print(f"   {package}")
        
        if len(filtered_packages) > 10:
            print(f"   ... and {len(filtered_packages) - 10} more packages")
        
        print("-" * 50)
        print("✅ requirements.txt generated successfully!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running pip freeze: {e}")
        return False
    except Exception as e:
        print(f"❌ Error generating requirements: {e}")
        return False

if __name__ == "__main__":
    print("🐳 MCP Memory Server - Docker Requirements Generator")
    print("=" * 55)
    
    success = generate_requirements()
    
    if success:
        print("\n🎉 Requirements generated successfully!")
        print("📋 Next steps:")
        print("   1. Review requirements.txt")
        print("   2. Run: docker-compose build")
        print("   3. Run: docker-compose up")
    else:
        print("\n❌ Failed to generate requirements!")
        sys.exit(1)
