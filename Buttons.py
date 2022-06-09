import pygame
from tkinter.filedialog import askopenfilename, asksaveasfilename


class TextButton:
	def __init__(self, x=0, y=0, text='text', font_type='opensans', font_size=12, font_color=(0,0,0)):
		# text
		self.font_color = font_color
		self.Font = pygame.font.SysFont(font_type, font_size)
		self.text_surf = self.Font.render(text, True, self.font_color)
		w,h = self.text_surf.get_size()
		# button
		self.image = pygame.Surface((w,h))
		self.rect = pygame.Rect(x,y,w,h)
		# cool down
		self.counter = pygame.time.get_ticks()
		self.cooldown = 300

	def normal(self):
		self.image.fill((6*255//10,)*3)
		self.image.blit(self.text_surf, self.text_surf.get_rect())
		pygame.draw.rect(self.image, (0,0,0), self.image.get_rect(), width=2,border_radius=2)

	def hover(self):
		self.image.fill((7*255//10,)*3)
		self.image.blit(self.text_surf, self.text_surf.get_rect())
		pygame.draw.rect(self.image, (0,0,0), self.image.get_rect(), width=2, border_radius=2)

	def update(self, screen, is_pressed):
		# update if cursor is colliding
		return_data = None
		if self.rect.collidepoint(pygame.mouse.get_pos()):
			self.hover()
			if is_pressed and (pygame.time.get_ticks() - self.counter) > self.cooldown:
				return_data = self.press()
				self.counter = pygame.time.get_ticks()
		else:
			self.normal()

		screen.blit(self.image, self.rect)
		return return_data

class LoadButton(TextButton):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)

	def press(self):
		filename = askopenfilename()
		return filename

class SaveButton(TextButton):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)

	def press(self):
		filename = asksaveasfilename()
		return filename


class ImageButton(TextButton):
	def __init__(self, name, sprite, scale_rect, **kwargs):
		super().__init__(**kwargs)
		self.name = name
		self.sprite = pygame.transform.scale(sprite, (scale_rect.w, scale_rect.h)).convert()
		self.rect.w, self.rect.h = self.sprite.get_size()

	def normal(self):
		self.image = pygame.Surface(self.sprite.get_size())
		self.image.blit(self.sprite, self.image.get_rect())

	def hover(self):
		self.image = pygame.Surface(self.sprite.get_size())
		self.image.blit(self.sprite, self.image.get_rect())
		pygame.draw.rect(self.image, (255,255,255), self.image.get_rect(), width=2)

	def press(self):
		return self.name

class BoolButton(TextButton):
	def __init__(self,**kwargs):
		super().__init__(**kwargs)
		self.bool_val = False
		self.check_box_w = max(self.rect.h,20)
		self.image = pygame.Surface((self.rect.w+self.check_box_w, self.check_box_w))
		self.check_box_rect = pygame.Rect([self.rect.w,0,self.check_box_w,self.check_box_w])
		self.screen_check_box_rect = self.check_box_rect.copy()
		self.screen_check_box_rect.x, self.screen_check_box_rect.y = self.rect.x+self.rect.w, self.rect.y
		self.rect.w, self.rect.h = self.image.get_size()

	def normal(self):
		text_rect = self.image.get_rect()
		text_rect.w = text_rect.w - self.check_box_w
		self.image.fill((255//2,)*3, text_rect)
		self.image.blit(self.text_surf, text_rect)
		self.image.fill((255,)*3, self.check_box_rect)
		pygame.draw.rect(self.image, (0,)*3, self.check_box_rect, width=2, border_radius=2)
		if self.bool_val:
			pygame.draw.line(self.image, (0,)*3, self.check_box_rect.bottomleft,
							 self.check_box_rect.topright, width=3)
			pygame.draw.line(self.image, (0,)*3, self.check_box_rect.bottomright,
							 self.check_box_rect.topleft, width=3)
	def press(self):
		if self.bool_val:
			self.bool_val = False
		else:
			self.bool_val = True

	def update(self, screen, is_pressed):
		self.normal()
		if self.screen_check_box_rect.collidepoint(pygame.mouse.get_pos()):
			if is_pressed and (pygame.time.get_ticks() -self.counter) > self.cooldown:
				self.press()
				self.counter = pygame.time.get_ticks()

		screen.blit(self.image, self.rect)
		return self.bool_val

class ValueButton(TextButton):
	def __init__(self, vals, display_vals, default_text, **kwargs):
		super().__init__(**kwargs)
		self.vals = vals
		self.display_vals = display_vals
		self.n_vals = len(self.vals)
		self.index = 0

		self.Font.bold=True
		default = self.Font.render(default_text, True, (0,0,0))
		w,h = default.get_size()
		self.arrow_box_w = 21
		self.image = pygame.Surface((w+self.arrow_box_w,max(h,self.arrow_box_w*2)))
		self.rect.w, self.rect.h = self.image.get_size()

		self.text_rect = pygame.Rect([0,0,w,self.rect.h])
		self.up_rect = pygame.Rect([w,0,self.arrow_box_w,self.rect.h/2])
		self.down_rect = pygame.Rect([w,self.rect.h/2,self.arrow_box_w,self.rect.h/2])

		self.screen_up_rect = self.up_rect.copy()
		self.screen_up_rect.x, self.screen_up_rect.y = self.rect.x+w, self.rect.y 
		self.screen_down_rect = self.down_rect.copy()
		self.screen_down_rect.x, self.screen_down_rect.y = self.rect.x+w, self.rect.y+self.rect.h/2

	def draw_text(self):
		self.image.fill((255,)*3)
		text = self.display_vals[self.index]
		text_surf = self.Font.render(text, True, self.font_color)
		text_rect = text_surf.get_rect()
		text_rect.center = self.text_rect.center
		self.image.blit(text_surf, text_rect)

	def draw_arrows(self):
		# up arrow
		pygame.draw.line(self.image, (0,)*3,
						 (self.up_rect.center[0], self.up_rect.bottom-5),
						 (self.up_rect.center[0], self.up_rect.top+5), width=5)
		pygame.draw.polygon(self.image, (0,)*3, [self.up_rect.midleft, 
												 self.up_rect.midtop,
												 self.up_rect.midright])
		pygame.draw.rect(self.image, (0,)*3, self.up_rect, width=2,border_radius=2)
		# down arrow
		pygame.draw.line(self.image, (0,)*3,
						 (self.down_rect.center[0], self.down_rect.bottom-5),
						 (self.down_rect.center[0], self.down_rect.top+5), width=5)
		pygame.draw.polygon(self.image, (0,)*3, [self.down_rect.midleft, 
												 self.down_rect.midbottom,
												 self.down_rect.midright])
		pygame.draw.rect(self.image, (0,)*3, self.down_rect, width=2,border_radius=2)


	def normal(self):
		# text
		self.draw_text()
		# arrows
		self.image.fill((6*255//10,)*3,self.up_rect)
		self.image.fill((6*255//10,)*3,self.down_rect)
		self.draw_arrows()
		
	def hover(self,rect_type):
		self.draw_text()
		if rect_type == 'up':
			self.image.fill((7*255//10,)*3,self.up_rect)
			self.image.fill((6*255//10,)*3,self.down_rect)
		elif rect_type == 'down':
			self.image.fill((6*255//10,)*3,self.up_rect)
			self.image.fill((7*255//10,)*3,self.down_rect)
		self.draw_arrows()

	def press(self,rect_type):
		if rect_type == 'up':
			self.index = (self.index+1)%self.n_vals
		elif rect_type == 'down':
			self.index = (self.index-1)%self.n_vals

	def update(self, screen, is_pressed):
		# update if cursor is colliding
		mouse_pos = pygame.mouse.get_pos()
		if self.screen_up_rect.collidepoint(mouse_pos):
			self.hover('up')
			if is_pressed and (pygame.time.get_ticks() - self.counter) > self.cooldown:
				self.press('up')
				self.counter = pygame.time.get_ticks()
		elif self.screen_down_rect.collidepoint(mouse_pos):
			self.hover('down')
			if is_pressed and (pygame.time.get_ticks() - self.counter) > self.cooldown:
				self.press('down')
				self.counter = pygame.time.get_ticks()
		else:
			self.normal()

		# draw to screen
		screen.blit(self.image, self.rect)
		return self.vals[self.index]
