import pygame
import json
from Level import LevelBuilder

scale = 4
size = (1920, 1080)




## make test data
level_data = {'background':
			  		{'locs': [[0,160,size[0],size[1]],[0,0,size[0],size[1]]],
			  		 'type': 'Background',
			  		 'n_repeats': 10,
			  		 'scroll_speeds': [0, .5]},
			  'ball':
					{'locs': [[size[0]//2 - (8*scale), size[1]//2 - (scale*8), 16*scale,16*scale]],
					 'type': 'Character'},
			  'dirt': 
					{'locs': [[i*16*scale,size[1]-2*16*scale,16*scale,16*scale] for i in range(40)],
					 'type': 'Tile',
					 'collision': [True,]*40},
			  'grass':
			  		{'locs': [[9*16*scale,size[1]-4*16*scale, 16*scale, 16*scale], [8*16*scale,size[1]-7*16*scale, 16*scale, 16*scale]],
			  		 'type': 'Tile',
			  		 'collision': [True,True]},
			  'item':
			  		{'locs': [[13*16*scale,size[1]-4*16*scale, 16*scale, 16*scale], [13*16*scale,size[1]-7*16*scale, 16*scale, 16*scale]],
			  		 'type': 'Item'}
			  }

with open('test_level.json', 'w') as f:
	json.dump(level_data, f)

# test spritesheet metadata
spritesheet_data = {'filename': 'test_sprite_sheet.png',
					'data': {'dirt': {'locs': [[0, 0, 16, 16]]},
							 'grass': {'locs': [[16, 0, 16, 16]]}
							 }
					}

with open('test_sprite_sheet.json', 'w') as f:
	json.dump(spritesheet_data, f)

ball_sheet_data = {'filname': 'test_sprite_ball.png',
				   'data': {'ball': {'locs':[[i*16*scale, 0, 16*scale, 16*scale] for i in range(4)],
									 'idle':[1,-1,-1, 0],
									 'run':[0, 1, 2, 3],
									 'jump':[-1, 1, -1, -1]}
							}
					}

with open('test_sprite_ball.json', 'w') as f:
	json.dump(ball_sheet_data, f)

world_sheet_data = {'filename': 'test_background.png',
					'data': {'background': {'locs': [[0,0,size[0],size[1]], [0,size[0],size[0],size[1]]]}
							}
					}
with open('test_sprite_background.json', 'w') as f:
	json.dump(world_sheet_data, f)

# test spritesheet metadata
item_data = {'filename': 'item.png',
			 'data': {'item': {'locs': [[0, 0, 16, 16]]}
			 		 }
			 }

with open('item.json', 'w') as f:
	json.dump(item_data, f)





# game
pygame.init()
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()
FPS = 60

left = False
right = False
up = False
down = False

# test level loading
spritesheet_files = ['test_sprite_sheet.png', 'test_sprite_ball.png', 'test_background.png', 'item.png']
spritesheet_data_files = ['test_sprite_sheet.json', 'test_sprite_ball.json', 'test_sprite_background.json', 'item.json']
level_data_file = 'test_level.json'

Level = LevelBuilder(scale, level_data_file, spritesheet_files, spritesheet_data_files)
Level.build()


run = True
while run:
	clock.tick(FPS)
	# test world
	screen.fill((150,220,255))
	Level.draw(screen, left=left, right=right, up=up, down=down)
	pygame.display.flip()


	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			run = False

		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_a:
				left = True
			if event.key == pygame.K_d:
				right = True
			if event.key == pygame.K_w:
				up = True
		if event.type == pygame.KEYUP:
			if event.key == pygame.K_a:
				left = False
			if event.key == pygame.K_d:
				right = False
			if event.key == pygame.K_w:
				up = False



pygame.quit()