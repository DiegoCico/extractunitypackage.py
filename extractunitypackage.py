#!/usr/bin/env python3
import os
import stat
import shutil
import sys
import tarfile
import tkinter as tk
from tkinter import filedialog

#runner
def main():
	root = tk.Tk()
	root.withdraw()

	# Getting the Unity package file and output directory from the user
	input_file = filedialog.askopenfilename(title='Select a Unity package file', filetypes=[('Unity package files', '*.unitypackage')])
	if not input_file:
		print("No file selected. Exiting.")
		sys.exit(1)

	outputDir = filedialog.askdirectory(title='Select output directory')
	if not outputDir:
		outputDir = os.path.dirname(input_file) # Default output directory is the same as input file's directory

	# Printing the paths for debugging
	print(f"Input file: {input_file}")
	print(f"Output directory: {outputDir}")

	name, extension = os.path.splitext(input_file)
	if extension.lower() != '.unitypackage':
		print("Error: Input file must be a .unitypackage")
		sys.exit(1)

	outputDir = os.path.join(outputDir, os.path.basename(name))

	workingDir = './.working'

	if os.path.exists(outputDir):
		print(f'Output dir "{outputDir}" already exists. Please choose a different directory.')
		sys.exit(1)

	if os.path.exists(workingDir):
		shutil.rmtree(workingDir)

	# Extracting the .unitypackage
	try:
		tar = tarfile.open(input_file, 'r:gz')
		tar.extractall(workingDir)
		tar.close()
		print(f"Extraction successful.")
	except Exception as e:
		print(f"Error extracting {input_file}: {e}")
		shutil.rmtree(workingDir)
		sys.exit(1)

	mapping = {}
	for i in os.listdir(workingDir):
		rootFile = os.path.join(workingDir, i)
		if os.path.isdir(rootFile):
			realPath = ''
			hasAsset = False
			for j in os.listdir(rootFile):
				if j == 'pathname':
					with open(os.path.join(rootFile, j), 'r') as file:
						realPath = file.readline(5_000_000).strip()
				elif j == 'asset':
					hasAsset = True

			if hasAsset and realPath:
				mapping[i] = realPath

	os.makedirs(outputDir, exist_ok=True)

	for asset, realPath in mapping.items():
		destDir, filename = os.path.split(realPath)
		destDir = os.path.join(outputDir, destDir)
		destFile = os.path.join(destDir, filename)
		source = os.path.join(workingDir, asset, 'asset')

		os.makedirs(destDir, exist_ok=True)
		shutil.move(source, destFile)
		os.chmod(destFile, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)
		print(f'{asset} => {realPath}')

	shutil.rmtree(workingDir)
	print("Extraction and exporting completed successfully.")

if __name__ == "__main__":
	main()
