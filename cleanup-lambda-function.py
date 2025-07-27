#!/usr/bin/env python3
"""
Script to clean up the lambda function directory by removing library packages
that should be in the Lambda layer instead.
"""

import os
import shutil
import sys

def cleanup_lambda_function():
    """Remove library packages from line-bot-deployment directory"""
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    lambda_dir = os.path.join(base_dir, "line-bot-deployment")
    
    # Files that should REMAIN in the lambda function directory
    keep_files = {
        "lambda_function.py",
        "funcs.py", 
        "weekly-notify.py",
        "__pycache__"  # Will be regenerated anyway
    }
    
    # Get all items in the lambda directory
    items_to_remove = []
    
    if not os.path.exists(lambda_dir):
        print(f"Error: {lambda_dir} does not exist")
        return False
        
    for item in os.listdir(lambda_dir):
        if item not in keep_files:
            items_to_remove.append(item)
    
    print(f"Found {len(items_to_remove)} library packages to remove from lambda function directory:")
    for item in sorted(items_to_remove):
        print(f"  - {item}")
    
    # Ask for confirmation
    response = input("\nDo you want to proceed with removing these items? (y/N): ")
    if response.lower() != 'y':
        print("Operation cancelled")
        return False
    
    # Remove the items
    removed_count = 0
    failed_count = 0
    
    for item in items_to_remove:
        item_path = os.path.join(lambda_dir, item)
        try:
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)
            else:
                os.remove(item_path)
            print(f"Removed: {item}")
            removed_count += 1
        except Exception as e:
            print(f"Failed to remove {item}: {e}")
            failed_count += 1
    
    print(f"\nCleanup completed:")
    print(f"  - Successfully removed: {removed_count} items")
    print(f"  - Failed to remove: {failed_count} items")
    
    # Show remaining files
    remaining_files = [f for f in os.listdir(lambda_dir) if os.path.isfile(os.path.join(lambda_dir, f))]
    print(f"\nRemaining files in lambda function directory:")
    for file in sorted(remaining_files):
        print(f"  - {file}")
    
    return True

def calculate_directory_size(directory):
    """Calculate the total size of a directory in MB"""
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(directory):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            try:
                total_size += os.path.getsize(filepath)
            except (OSError, FileNotFoundError):
                pass
    return total_size / (1024 * 1024)  # Convert to MB

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    lambda_dir = os.path.join(base_dir, "line-bot-deployment")
    
    # Show current size
    if os.path.exists(lambda_dir):
        current_size = calculate_directory_size(lambda_dir)
        print(f"Current lambda function directory size: {current_size:.2f} MB")
    
    success = cleanup_lambda_function()
    
    # Show new size after cleanup
    if success and os.path.exists(lambda_dir):
        new_size = calculate_directory_size(lambda_dir)
        print(f"New lambda function directory size: {new_size:.2f} MB")
        print(f"Size reduction: {current_size - new_size:.2f} MB")
