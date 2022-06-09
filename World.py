import pygame
import numpy as np


class Background:
	def __init__(self, n_repeats, scroll_speeds, rects, sprites):
		self.scroll_speeds = scroll_speeds
		self.sprites = sprites
		# nested rects of repeats
		self.rects = []
		for i in range(n_repeats):
			temp_list = []
			for rect in rects:
				rect_copy = rect.copy()
				rect_copy[0] = i*rect_copy[3]
				temp_list.append(rect_copy)
			self.rects.append(temp_list)

	def draw(self, screen, dx, dy, offset):
		# blit sprites and rects
		for rects in self.rects:
			for rect, sprite, scroll_speed in zip(rects, self.sprites, self.scroll_speeds):
				rect[0] -= np.sign(dx)*scroll_speed
				screen.blit(sprite, rect)

class Item(pygame.sprite.Sprite):
	def __init__(self, item_key, x, y, sprites):
		super().__init__()
		self.item_key = item_key
		self.frame_index = 0
		self.sprites = sprites
		self.image = self.sprites[self.frame_index]
		self.rect = pygame.Rect(x,y,self.image.get_width(),self.image.get_height())

	def update_animation(self):
		pass

	def update(self, screen, player_rect, dx, dy, offset):
		offset_rect = self.rect.move(-offset[0], -offset[1])
		moved_rect = player_rect.move(dx, dy)
		if moved_rect.colliderect(offset_rect):
			self.kill()
			return self.item_key
		else:
			screen.blit(self.image, offset_rect)









	

