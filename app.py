# Shim entry so deployment can point to app.py while we keep the real app in app_new.py
import runpy

if __name__ == '__main__':
    runpy.run_path('app_new.py', run_name='__main__')
