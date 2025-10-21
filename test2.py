import os

# Get all files (not directories) in the current directory
files = [f for f in os.listdir('.') if os.path.isfile(f)]

print(files)
