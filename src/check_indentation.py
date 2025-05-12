import os
import py_compile
import traceback

def check_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            compile(f.read(), filepath, 'exec')
        print(f"✓ {os.path.basename(filepath)}")
        return True
    except IndentationError as e:
        print(f"✗ {os.path.basename(filepath)}: {str(e)}")
        print(f"  Line {e.lineno}: {e.text.strip()}")
        return False
    except SyntaxError as e:
        print(f"✗ {os.path.basename(filepath)}: {str(e)}")
        print(f"  Line {e.lineno}: {e.text.strip()}")
        return False
    except Exception as e:
        print(f"✗ {os.path.basename(filepath)}: {str(e)}")
        return False

def main():
    src_dir = os.path.dirname(os.path.abspath(__file__))
    files = [f for f in os.listdir(src_dir) if f.endswith('.py')]
    
    print("Checking Python files for indentation errors...")
    print("-" * 50)
    
    all_good = True
    for file in files:
        if not check_file(os.path.join(src_dir, file)):
            all_good = False
            
    print("-" * 50)
    if all_good:
        print("All files passed!")
    else:
        print("Some files have indentation errors!")

if __name__ == '__main__':
    main()
