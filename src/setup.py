from cx_Freeze import setup,Executable

print("Working")

exe = Executable(
   "flockwave/server/__main__.py", base="console", target_name="Skybrush-Server"
)

setup(
    name="Skybrush-Server",
    version=0.1,
    description="project_description",
    executables=[exe],
)