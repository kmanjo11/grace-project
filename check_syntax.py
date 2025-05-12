import os
import py_compile
import traceback

def check_syntax(directory):
    """Check Python files for syntax errors."""
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    compile(content, filepath, 'exec')
                    print(f"✓ {filepath}")
                except Exception as e:
                    print(f"\n❌ Error in {filepath}:")
                    print(traceback.format_exc())
                    print()

if __name__ == '__main__':
    # Change this to your project's src directory
    project_dir = os.path.join(os.path.dirname(__file__), 'src')
    check_syntax(project_dir)