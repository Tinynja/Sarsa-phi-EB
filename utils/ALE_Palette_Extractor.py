# Built-in libraries
import pickle
import subprocess
from argparse import ArgumentParser
from pathlib import Path
from math import ceil, sqrt

# Pypi libraries
from ale_py import ALEInterface
import ale_py.roms as ROMS
import torch
import matplotlib.pyplot as plt


def get_color_palette(rom):
	res = subprocess.run(['python_pipenv.cmd', '-c', f'from ale_py import ALEInterface; from ale_py.roms import {rom}; ALEInterface().loadROM({rom})'], capture_output=True)
	return res.stderr.decode().splitlines()[6].strip().split()[-1]


parser = ArgumentParser()
parser.add_argument('DISPLAY_FORMAT', help='the display_format for which to generate a palette')
args = parser.parse_args()


ale = ALEInterface()
unique_colors = torch.empty((0,3), dtype=torch.int32)

for rom in ROMS._RESOLVED_ROMS:
	try:
		if get_color_palette(rom) == args.DISPLAY_FORMAT:
			ale.loadROM(getattr(ROMS, rom))
			img = torch.from_numpy(ale.getScreenRGB())
			unique_colors = torch.cat((unique_colors, img.reshape(-1,3)), axis=0).unique(dim=0)
			nb_unique = unique_colors.shape[0]
			print(f'Found {nb_unique} unique colors so far...')
	except:
		pass

# Print the palette
print('Here is the gathered palette:')
print(unique_colors)
print(f'Shape of the palette: {unique_colors.shape}, {unique_colors.dtype}')

# Save the palette as pickle
export_path = Path(__file__).resolve().parent.parent.joinpath('palettes', f'{args.DISPLAY_FORMAT}_Palette.pickle')
with open(export_path, 'wb') as file:
	pickle.dump(unique_colors, file)

# Show the palette
side_size = int(ceil(sqrt(nb_unique)))
nb_fillblack = side_size**2 - nb_unique

unique_colors = torch.cat((unique_colors, torch.zeros((nb_fillblack, 3), dtype=int)), axis=0)
unique_colors = unique_colors.reshape(side_size, side_size, 3)

plt.imshow(unique_colors)
plt.show()
