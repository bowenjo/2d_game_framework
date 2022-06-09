import pygame
import json
import numpy as np
from Level import SpriteSheet
from Buttons import LoadButton, SaveButton, ImageButton, BoolButton, ValueButton


class LevelEditor:
	def __init__(self, screen_size, game_scale=4):
		# UI 
		self.screen_size = screen_size
		ed_scale = .75
		ed_size = (int(ed_scale*screen_size[0]), int(ed_scale*screen_size[1]))
		self.ed_rect = pygame.Rect([screen_size[0] - ed_size[0], 0, ed_size[0], ed_size[1]])
		self.ui_font = pygame.font.SysFont('freesans',18)
		self.ui_font.underline=True

		# Buttons
		# tools
		self.Eraser = BoolButton(x=10,y=40,text='Eraser ',
								font_type='freesans',font_size=14,font_color=(0,0,0))

		# sprites
		self.sprite_buttons = None
		self.LoadSprite = LoadButton(x=10,y=300,text='Open Spritesheet...',
									font_type='freesans',font_size=18,font_color=(0,0,0))
		self.SpriteTypeSelect = ValueButton(['Tile','Item'], ['Tile', 'Item'], "Background",
											x=10, y=self.LoadSprite.rect.y-80)
		self.CollisionCheck = BoolButton(x=10,y=self.LoadSprite.rect.y-30, text='Collide ',
										font_type='freesans',font_size=14,font_color=(0,0,0))
		self.ShowSpriteType = BoolButton(x=self.CollisionCheck.rect.right+10,y=self.LoadSprite.rect.y-30,
		          						 text='Show all ', font_type='freesans',font_size=14,font_color=(0,0,0))
		self.LayerSelect = ValueButton(['Layer0', 'Layer1','Layer2'], ['Layer0', 'Layer1','Layer2'], "Background",
											x=240, y=self.LoadSprite.rect.y-80)
		self.HideLayers = BoolButton(x=240, y=self.LoadSprite.rect.y-30, text='Show only ',
									  font_type='freesans',font_size=14,font_color=(0,0,0))
		# level
		self.LoadLevel = LoadButton(x=self.ed_rect.left,y=860, text = 'Open Level...',
									font_type='freesans',font_size=18,font_color=(0,0,0))
		self.SaveLevel = SaveButton(x=self.ed_rect.left,y=910, text = 'Save Level as...',
									font_type='freesans',font_size=18,font_color=(0,0,0))
		# grid
		self.GridSelect = ValueButton([None,8,16,32], ["None","8x8","16x16","32x32"], "000x000",
									  x=self.ed_rect.x+200, y=860)

		# Sprite attributes
		self.game_scale = game_scale
		self.ed_sprite_scale = self.game_scale * ed_scale
		self.sprite_buttons = None
		self.active_sprite_name = None
		self.active_sprite = None
		self.sprites = {}
		self.curent_sprite_type = None
		self.show_sprite_type = False
		self.is_collision = False

		# Sprite thumbnails 
		self.thumbnail_spacing = 2*64
		self.thumbnail_rect = pygame.Rect([100,self.LoadSprite.rect.y+100,64,64])
		self.thumbnail_font = pygame.font.SysFont('freesans', 14)
		print(pygame.font.get_fonts())

		# Editor 
		self.placement_cooldown = 100 # miliseconds
		self.placement_counter = pygame.time.get_ticks()
		self.current_layer = 'Layer0'
		self.hide_layer = False

		# Tools
		self.is_eraser = False

		# Grid
		self.grid_points = None

		# level data
		self.ed_data = {}
		self.level_data = {}

	def draw_ui_text(self,screen,font,x,y,text):
		text_surf = font.render(text, True, (0,0,0))
		w,h = text_surf.get_size()
		rect = pygame.Rect(x,y,w,h)
		screen.blit(text_surf, rect)

	def load_spritesheet(self, screen, **kwargs):
		spritesheet_data_file = self.LoadSprite.update(screen, kwargs['is_pressed'])
		if spritesheet_data_file is not None:
			# load spritesheets
			spritesheet_data = json.load(open(spritesheet_data_file, 'r'))
			spritesheet_img = pygame.image.load(spritesheet_data['filename']).convert()
			sheet = SpriteSheet(spritesheet_img, spritesheet_data) 

			# get sprites and place sprite buttons
			self.sprite_buttons = []
			row=0
			for i, name in enumerate(sheet.data):
				# set sprites
				sprite = sheet.parse_spritesheet(name)[0]
				w,h = sprite.get_size()
				self.sprites.update({name:pygame.transform.scale(sprite,
								    (w*self.ed_sprite_scale, h*self.ed_sprite_scale)).convert()})
				# set buttons
				button = ImageButton(name, sprite, self.thumbnail_rect) 
				button.rect.x = self.thumbnail_rect.x + self.thumbnail_spacing * (i%2) 
				button.rect.y = self.thumbnail_rect.y + self.thumbnail_spacing * row
				if i%2 == 0 and i != 0:
					row+=1
				self.sprite_buttons.append(button)

	def check_sprite_buttons(self, screen, **kwargs):
		if self.sprites:
			for button in self.sprite_buttons:
				self.set_active_sprite(button.update(screen, kwargs['is_pressed']))

	def set_active_sprite(self, name):
		if name is not None:
			self.active_sprite_name = name
			self.active_sprite = self.sprites[name]
			if self.is_eraser:
				self.is_eraser = False
				self.Eraser.bool_val = False

	def add_editor_data(self, data, rect):
		if (pygame.time.get_ticks() - self.placement_counter) > self.placement_cooldown:
			if self.active_sprite_name not in data:
				data[self.active_sprite_name] = {}
				data[self.active_sprite_name]['locs'] = [rect]
				data[self.active_sprite_name]['layer'] = [self.current_layer]
				data[self.active_sprite_name]['type'] = self.current_sprite_type
				if data[self.active_sprite_name]['type'] == 'Tile':
					data[self.active_sprite_name]['collision'] = [self.is_collision]
			else:
				data[self.active_sprite_name]['locs'].append(rect)
				data[self.active_sprite_name]['layer'].append(self.current_layer)
				if data[self.active_sprite_name]['type'] == 'Tile':
					data[self.active_sprite_name]['collision'].append(self.is_collision)

			self.placement_counter = pygame.time.get_ticks()

	def delete_editor_data(self, data):
		for name, d in data.items():
			for i, rect in enumerate(d['locs'].copy()):
				if rect.collidepoint(pygame.mouse.get_pos()):
					data[name]['locs'].pop(i)
					data[name]['layer'].pop(i)
					if data[name]['type'] == 'Tile':
						data[name]['collision'].pop(i)
					break

	def bounding_rect(self, sprite):
		surf = pygame.Surface(sprite.get_size())
		surf.blit(sprite, surf.get_rect())
		pygame.draw.rect(surf, (255,255,255), surf.get_rect(), width=2)
		return surf

	def draw_editor_data(self, screen):
		if self.sprites:
			for name, sprite in self.sprites.items():
				if name in self.ed_data:
					for i, rect in enumerate(self.ed_data[name]['locs']):
						surf = sprite.copy()
						# display only the current layer
						if self.hide_layer and self.ed_data[name]['layer'][i] != self.current_layer:
							continue
						if self.show_sprite_type and self.ed_data[name]['type'] == self.current_sprite_type:
							if self.current_sprite_type == 'Tile' and self.is_collision:
								if self.ed_data[name]['collision'][i]:
									surf = self.bounding_rect(surf)
							else:
								surf = self.bounding_rect(surf)

						screen.blit(surf, rect)

	def update_editor(self, screen, **kwargs):
		mouse_x, mouse_y = pygame.mouse.get_pos()
		if self.ed_rect.collidepoint(mouse_x,mouse_y):
			if self.active_sprite_name is not None:
				# track sprite location
				pygame.mouse.set_visible(False)
				w,h = self.active_sprite.get_size()
				if self.grid_points is not None:
					point = self.get_grid_point(mouse_x,mouse_y)
					ed_sprite_rect = pygame.Rect(point[0], point[1], w, h)
				else:
					ed_sprite_rect = pygame.Rect(mouse_x, mouse_y, w, h)
				screen.blit(self.active_sprite, ed_sprite_rect)
				# add the clicked location
				if kwargs['is_pressed']:
					self.add_editor_data(self.ed_data, ed_sprite_rect)
			else:
				pygame.mouse.set_visible(True)
				# erase the clicked location
				if self.is_eraser and kwargs['is_pressed']:
					self.delete_editor_data(self.ed_data)
		else:
			pygame.mouse.set_visible(True)

		self.draw_editor_data(screen)


	def get_grid_point(self, mouse_x, mouse_y):
		dist = np.sqrt((mouse_x - self.grid_points[:,0])**2 + (mouse_y - self.grid_points[:,1])**2)
		return self.grid_points[np.argmin(dist)].tolist()

	def set_grid(self,screen,grid_spacing):
		if grid_spacing is not None:
			grid_spacing_scaled = grid_spacing*self.ed_sprite_scale
			n_w = int(np.ceil(self.ed_rect.w / grid_spacing_scaled))
			n_h = int(np.ceil(self.ed_rect.h / grid_spacing_scaled))

			# draw grid lines
			# vertical grid
			x = self.ed_rect.x
			for i in range(n_w):
				start_pos = (x+grid_spacing_scaled*i, self.ed_rect.top)
				end_pos = (x+grid_spacing_scaled*i, self.ed_rect.bottom)
				pygame.draw.line(screen,(255//3,)*3, start_pos, end_pos)

			# horizontal grid
			y = self.ed_rect.bottom
			for i in range(n_h):
				start_pos = (self.ed_rect.left, y-grid_spacing_scaled*i)
				end_pos = (self.ed_rect.right, y-grid_spacing_scaled*i)
				pygame.draw.line(screen,(255//3,)*3, start_pos, end_pos)

			# grid points
			xx, yy = np.mgrid[0:n_w, 1:n_h]
			xx = x + grid_spacing_scaled*xx
			yy = y - grid_spacing_scaled*yy
			self.grid_points = np.concatenate((xx.reshape(-1,1),yy.reshape(-1,1)),axis=1)
		else:
			self.grid_points = None

	def load_level(self):
		pass
	def save_level(self):
		# clean up empty dict keys
		# need to do some mapping to get the scale right
		pass

	def update(self, screen, **kwargs):
		# editor
		screen.fill((45,)*3, self.ed_rect)
		self.update_editor(screen, **kwargs)
		# draw basic ui
		screen.fill((255//2,)*3, [0,0,self.ed_rect.left,self.screen_size[1]])
		screen.fill((255//2,)*3, [self.ed_rect.left,self.ed_rect.bottom,
								  self.screen_size[0]-self.ed_rect.left,
								  self.screen_size[1]-self.ed_rect.bottom])
		self.draw_ui_text(screen,self.ui_font,10,10,'Tools:')
		self.draw_ui_text(screen,self.ui_font,10,self.LoadSprite.rect.y-130, 'Sprites:')
		self.draw_ui_text(screen,self.thumbnail_font,10,self.SpriteTypeSelect.rect.y-20,'type/collision')
		self.draw_ui_text(screen,self.thumbnail_font,240,self.SpriteTypeSelect.rect.y-20,'layers')
		self.draw_ui_text(screen,self.ui_font,self.ed_rect.x,self.ed_rect.bottom+10, 'Level:')
		self.draw_ui_text(screen,self.ui_font,self.ed_rect.x+200,self.ed_rect.bottom+10, 'Grid:')
		# buttons
		# tools
		self.is_eraser = self.Eraser.update(screen, **kwargs)
		if self.is_eraser:
			self.active_sprite_name = None
		# sprite 
		self.current_sprite_type = self.SpriteTypeSelect.update(screen, **kwargs)
		self.is_collision = self.CollisionCheck.update(screen, **kwargs)
		self.show_sprite_type = self.ShowSpriteType.update(screen, **kwargs)
		self.current_layer = self.LayerSelect.update(screen, **kwargs)
		self.hide_layer = self.HideLayers.update(screen, **kwargs)
		self.load_spritesheet(screen, **kwargs)
		self.check_sprite_buttons(screen, **kwargs)
		# grid
		grid_spacing = self.GridSelect.update(screen, **kwargs)
		self.set_grid(screen,grid_spacing)
		# load/save level
		self.LoadLevel.update(screen, **kwargs)
		self.SaveLevel.update(screen, **kwargs)
		print(self.ed_data)

if __name__ == "__main__":

	pygame.init()
	pygame.font.init()

	screen_size = (1920,1080)
	screen = pygame.display.set_mode(screen_size) #, flags=pygame.FULLSCREEN)
	pygame.display.set_caption('Level Editor')

	# frame clock
	clock = pygame.time.Clock()
	FPS = 60

	# cursor variables
	is_pressed = False

	# initialize game objects
	Editor = LevelEditor(screen_size)

	# game loop
	run = True
	while run:
		# clock.tick(60)

		# fill screen/editor windows
		Editor.update(screen, is_pressed=is_pressed)
		pygame.display.flip()

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False

			if event.type == pygame.MOUSEBUTTONDOWN:
				left, middle, right = pygame.mouse.get_pressed()
				if left:
					is_pressed = True
			if event.type == pygame.MOUSEBUTTONUP:
				is_pressed = False

	pygame.quit()