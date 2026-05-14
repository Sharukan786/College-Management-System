import os
import re

def fix_imports_in_file(file_path):
    """Fix imports in a single file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace all 'from backend.' with 'from '
        content = re.sub(r'from backend\.', 'from ', content)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"Fixed imports in: {file_path}")
        return True
    except Exception as e:
        print(f"Error fixing {file_path}: {e}")
        return False

def fix_all_imports():
    """Fix imports in all Python files in routes directory"""
    routes_dir = 'routes'
    
    for root, dirs, files in os.walk(routes_dir):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                fix_imports_in_file(file_path)

if __name__ == "__main__":
    fix_all_imports()
    print("Import fixing complete!")
