import sys
import importlib

# Ensure project package root is on sys.path when running from other cwd
sys.path.insert(0, r"C:\code\gplm\Open-AutoGLM")

mods = [
    'phone_agent.adb.screenshot',
    'phone_agent.adb.input',
    'phone_agent.actions.handler',
]

for m in mods:
    try:
        importlib.import_module(m)
        print(m + ' OK')
    except Exception as e:
        print(m + ' ERROR', e)
