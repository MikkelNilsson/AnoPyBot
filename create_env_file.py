import os

file_content = []
for var in filter(lambda x : x.lower().startswith("anobot_"), os.environ.keys()):
    value = os.getenv(var)
    if not value:
        print(f"Environment variable {var[7:]} is empty or not configured!")
    else:
        file_content.append(f"{var[7:]}=\"{value}\"")

with open("./.env", "w") as f:
    f.write("\n".join(file_content))