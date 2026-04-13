import os

# 👉 CHANGE THIS PATH if needed
folder_path = "data/raw_images/empty"

# get all image files
files = [f for f in os.listdir(folder_path) if f.lower().endswith((".jpg", ".jpeg", ".png"))]

# sort files (important)
files.sort()

for i, filename in enumerate(files, start=1):
    old_path = os.path.join(folder_path, filename)
    new_name = f"{i}.jpg"
    new_path = os.path.join(folder_path, new_name)

    os.rename(old_path, new_path)

print("Done renaming images ✅")