import pygame
import json
import numpy as np
from Character import Character
from World import Background, Item


class SpriteSheet:
	def __init__(self, sheet, data):
		self.sheet = sheet
		self.data = data['data']

	def get_sprite(self, rectangle):
		rect = pygame.Rect(rectangle)
		surf = pygame.Surface(rect.size).convert()
		surf.blit(self.sheet, (0, 0), rect)
		surf.set_colorkey((255,255,255))
		return surf

	def parse_spritesheet(self, name):
		keys = list(self.data[name].keys())
		if len(keys) > 1: # nested animation
			locs = np.array(self.data[name]['locs'])
			keys.pop(0)
			surfaces = {}
			for key in keys:
				surfaces.update({key: []})
				animation_order = np.sort(self.data[name][key])
				animation_order_index = np.argsort(self.data[name][key])[animation_order>=0]
				for rectangle in locs[animation_order_index].tolist():
					surfaces[key].append(self.get_sprite(rectangle))
		else: # still or single animation
			surfaces = []
			for rectangle in self.data[name]['locs']:
				surfaces.append(self.get_sprite(rectangle))
		return surfaces

class LevelBuilder:
	def __init__(self, scale, level_data_file, spritesheet_files, spritesheet_data_files):
		# get spritesheet objects
		self.scroll_dist = [0,0]
		self.camera_offset = [0,0]
		self.camera_lapse = 15

		self.sheets = []
		for sheet_file, data_file in zip(spritesheet_files, spritesheet_data_files):
			sheet = pygame.image.load(sheet_file)
			w,h = sheet.get_size()
			sheet = pygame.transform.scale(sheet, (scale*w, scale*h)).convert()
			data = json.load(open(data_file, 'r'))
			self.sheets.append(SpriteSheet(sheet, data))

		# organize sprites for the level
		self.level_data = json.load(open(level_data_file, 'r')) 
		for name in self.level_data:
			for sheet in self.sheets:
				if name in sheet.data.keys():
					self.level_data[name].update({'sprites':sheet.parse_spritesheet(name)})

	def build(self):
		# build objects
		self.game_objects = {}
		self.game_objects.update({'Items': pygame.sprite.Group()})
		self.colliders = []
		extras = []
		for name, data in self.level_data.items():
			if data['type'] == 'Tile':
				extras.append(name)
				# collect colliders
				self.colliders += np.array(data['locs'])[data['collision']].tolist()

			elif data['type'] == 'Item':
				for loc in data['locs']:
					obj = Item('test', loc[0], loc[1], data['sprites'])
					self.game_objects['Items'].add(obj)

			elif data['type'] == 'Background':
				obj = Background(data['n_repeats'], data['scroll_speeds'], data['locs'], data['sprites'])
				self.game_objects.update({data['type']: obj})

			elif data['type'] == 'Character':
				obj = Character(data['locs'][0][0], data['locs'][0][1], 5, 15, data['sprites'])
				self.game_objects.update({data['type']: obj})


		[self.level_data.pop(name) for name in list(self.level_data.keys()).copy() if name not in extras]


	def draw(self, screen, **kwargs):
		# update the player
		dx,dy = self.game_objects['Character'].update(colliders=self.colliders,
													  offset=self.scroll_dist, **kwargs)
		
		# scrolling offsets
		self.scroll_dist[0] += dx 
		self.scroll_dist[1] += dy
		self.camera_offset[0] += (self.camera_lapse*dx - self.camera_offset[0])/self.camera_lapse
		self.camera_offset[1] += (self.camera_lapse*dy - self.camera_offset[1])/self.camera_lapse
		offset = [self.scroll_dist[0] - self.camera_offset[0], self.scroll_dist[1] - self.camera_offset[1]]

		# draw objects
		# self.game_objects['Background'].draw(screen,dx,dy,offset)
		player_rect = self.game_objects['Character'].draw(screen, self.camera_offset)
		self.game_objects['Items'].update(screen, player_rect, dx, dy, offset)

		# draw rest to the screen 
		for name, data in self.level_data.items():
			for loc in data['locs']:
				tile_rect = pygame.Rect(loc.copy())
				tile_rect.move_ip(-offset[0], -offset[1])
				screen.blit(data['sprites'][0], tile_rect)	

