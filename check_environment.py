#!/usr/bin/env python3
"""
Script to check if conda environment has all required packages from requirements.txt
"""
import subprocess
import sys
import pkg_resources
from packaging import version

def read_requirements(file_path):
    """Read requirements from requirements.txt file"""
    requirements = []
    try:
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    requirements.append(line)
    except FileNotFoundError:
        print(f"Error: {file_path} not found")
        return []
    return requirements

def parse_requirement(req_string):
    """Parse requirement string to get package name and version"""
    if '==' in req_string:
        name, ver = req_string.split('==')
        return name.strip(), ver.strip()
    elif '>=' in req_string:
        name, ver = req_string.split('>=')
        return name.strip(), ver.strip()
    else:
        return req_string.strip(), None

def check_installed_packages(requirements):
    """Check if required packages are installed"""
    missing_packages = []
    version_mismatches = []
    installed_packages = []
    
    for req in requirements:
        pkg_name, required_version = parse_requirement(req)
        
        try:
            # Check if package is installed
            installed_pkg = pkg_resources.get_distribution(pkg_name)
            installed_version = installed_pkg.version
            
            print(f"✓ {pkg_name}: {installed_version} (required: {required_version or 'any'})")
            
            # Check version compatibility if specific version required
            if required_version and installed_version != required_version:
                version_mismatches.append((pkg_name, installed_version, required_version))
            
            installed_packages.append(f"{pkg_name}=={installed_version}")
            
        except pkg_resources.DistributionNotFound:
            print(f"✗ {pkg_name}: NOT INSTALLED (required: {required_version or 'any'})")
            missing_packages.append(req)
    
    return missing_packages, version_mismatches, installed_packages

def main():
    print("Checking conda environment packages against requirements.txt...")
    print("=" * 60)
    
    # Read requirements
    requirements = read_requirements('requirements.txt')
    if not requirements:
        print("No requirements found or file not accessible")
        return
    
    print(f"Found {len(requirements)} requirements to check")
    print("-" * 60)
    
    # Check installed packages
    missing, mismatches, installed = check_installed_packages(requirements)
    
    print("\n" + "=" * 60)
    print("SUMMARY:")
    print("=" * 60)
    
    if not missing and not mismatches:
        print("🎉 ALL PACKAGES ARE CORRECTLY INSTALLED!")
    else:
        if missing:
            print(f"❌ MISSING PACKAGES ({len(missing)}):")
            for pkg in missing:
                print(f"   - {pkg}")
        
        if mismatches:
            print(f"\n⚠️  VERSION MISMATCHES ({len(mismatches)}):")
            for pkg_name, installed_ver, required_ver in mismatches:
                print(f"   - {pkg_name}: installed {installed_ver}, required {required_ver}")
    
    print(f"\n📊 TOTAL PACKAGES CHECKED: {len(requirements)}")
    print(f"✓ INSTALLED: {len(installed)}")
    print(f"✗ MISSING: {len(missing)}")
    print(f"⚠️  VERSION ISSUES: {len(mismatches)}")
    
    # Generate install command for missing packages
    if missing:
        print("\n" + "=" * 60)
        print("TO INSTALL MISSING PACKAGES:")
        print("=" * 60)
        print("conda activate kakeibot_py311")
        print("pip install " + " ".join([f'"{pkg}"' for pkg in missing]))

if __name__ == "__main__":
    main()
