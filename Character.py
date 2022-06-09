import pygame
import numpy as np

class Character(pygame.sprite.Sprite):
	def __init__(self, x, y, x_speed, y_speed, sprites):
		super().__init__()
		
		# character attributes
		self.alive = True

		# movement attributes
		# x-direction
		self.x_speed = x_speed
		self.x_direction = 1
		# y-direction
		self.gravity = 5
		self.y_speed = y_speed
		self.y_direction = 1

		# animation attributes
		self.frame_index = 0
		self.action = 'idle'
		self.animation_cooldown = 100 # miliseconds
		self.counter = pygame.time.get_ticks()

		# image attribtues
		self.sprites = sprites
		self.image = self.sprites['idle'][self.frame_index]
		self.rect = self.image.get_rect()
		self.rect.x, self.rect.y = x, y

	def check_collision(self, dx, dy, colliders, offset):
		"""
		checks collision for character movements

		"""
		for collision_rect in colliders:
			collision_rect = pygame.Rect(collision_rect.copy())
			collision_rect.move_ip(-offset[0], -offset[1])
			x_moved_rect = self.rect.move(dx,0)
			y_moved_rect = self.rect.move(0,dy)
			# x-direction collisions
			if x_moved_rect.colliderect(collision_rect):
				if self.x_direction == 1: # moving right
					dx = collision_rect.left - self.rect.right
				elif self.x_direction == -1: # moving left
					dx = collision_rect.right - self.rect.left
			# y-direction collisions
			elif y_moved_rect.colliderect(collision_rect):
				if self.y_direction == 1: # falling
					dy = collision_rect.top - self.rect.bottom
				elif self.y_direction == -1: # rising
					dy = collision_rect.bottom - self.rect.top
		return dx, dy
	
	def move(self, colliders, offset, right, left, up, down):
		dx = 0; dy = 0
		move_world = False
		if self.alive:
			if right or left or up or down:
				if right or left:
					self.update_action('run')
					if right:
						self.x_direction = 1
					if left:
						self.x_direction = -1
					dx += self.x_speed*self.x_direction
				if up or down:
					if up and self.y_direction == 1:
						self.y_direction = -1
					dy += self.y_speed*self.y_direction

			else:
				self.update_action('idle')

			dy += self.gravity
			if dy > 0: # falling
				self.y_direction = 1
			else: # rising
				self.y_direction = -1

			dx, dy = self.check_collision(dx,dy,colliders,offset)

			if dy != 0: # not colliding with a ground
				self.update_action('jump')

			return dx, dy

	def update_action(self, new_action):
		if self.action != new_action:
			self.action = new_action
			self.frame_index = 0

	def update_animation(self):
		if (pygame.time.get_ticks() - self.counter) > self.animation_cooldown:
			self.frame_index = (self.frame_index+1) % len(self.sprites[self.action])
			self.image = self.sprites[self.action][self.frame_index]
			self.counter = pygame.time.get_ticks()

	def update(self, colliders=None, offset=[0,0], **kwargs):
		dx, dy = self.move(colliders, offset, kwargs['right'],kwargs['left'],kwargs['up'],kwargs['down'])
		self.update_animation()
		return dx, dy

	def draw(self, screen, camera_offset):
		offset_rect = self.rect.move(np.ceil(camera_offset[0]), np.ceil(camera_offset[1]))
		screen.blit(self.image, offset_rect)
		return offset_rect
		

