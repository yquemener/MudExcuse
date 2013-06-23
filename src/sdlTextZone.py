#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pygame
from pygame.locals import *

class TextZone:
	def __init__(self, game, text, rect, font):
		self.text=text
		self.font=font
		self.rect=rect
		self.surface=pygame.Surface((rect[2], rect[3]), depth=32)
		self.wordWrap()
		
	def wordWrap(self):
		self.surface.fill((0,0,0))
		x=0
		y=0
		for line in self.text.split('\n'):
			words=[]
			for word in line.split(" "):
				words.append(self.font.render(word, False, (255,255,255)))
	
			wsp=self.font.render(" ", False, (255,255,255)).get_width()
			for w in words:
				if (x+wsp+w.get_width()<self.rect[2]):
					self.surface.blit(w, (x,y))
					x=x+wsp+w.get_width()
				else:
					y=y+12
					x=0
					self.surface.blit(w, (x,y))
					x=x+wsp+w.get_width()
			y=y+12

	def draw(self, screen):
		screen.blit(self.surface, (self.rect[0], self.rect[1]))

	def changeText(self, text):
		self.text=text
		self.wordWrap()
