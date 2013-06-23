#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pygame
from pygame.locals import *
from sdlTextZone import *


class Text:
	def __init__(self, game, text, pos, font):
		self.text=text
		self.font=font
		self.surface=self.font.render(text, False, (255,255,255))
		self.rect=[pos[0], pos[1], self.surface.get_width(), self.surface.get_width()]

	def changeBackgroundColor(self, color):
		self.surface=self.game.font.render(self.text, False, (255,255,255), color)

	def changeText(self, text):
		self.text=text
		self.surface=self.font.render(text, False, (255,255,255))
	
	def draw(self, screen):
		screen.blit(self.surface, (self.rect[0], self.rect[1]))


class Application:
	def __init__(self):
		pygame.init()
		self.size = (1024, 600)		
		self.screen = pygame.display.set_mode(self.size)		
		pygame.display.set_caption('Various fonts test')
		pygame.font.init()
		self.fonts = []
		for i in range(6,24):
			self.fonts.append(pygame.font.Font("Vera.ttf", i))
		self.drawList=[]
		y=10
		i=6
		for f in self.fonts:
			#self.drawList.append(Text(self, str(i)+"  Buvez de ce whisky que le patron juge fameux.",[50,y],f))
			i=i+1
			#y+=self.drawList[-1].surface.get_height()
			
		#multilineTest=u"\"Les sanglots des violons de l'automne bercent mon coeur d'une langueur monotone\", nous dit le poête. Moi l'automne me rappelle plutôt qu'il va bientôt falloir sortir la pelle pour ramasser les feuilles, mais j'ai toujours été un peu terre à terre."
		multilineTest=u"\"Les "
		self.testZone=TextZone(self, multilineTest, [100,100,200,100], self.fonts[6])
		self.drawList.append(self.testZone)

	def draw(self):
		for o in self.drawList:
			o.draw(self.screen)
		
	def mainLoop(self):
		while True:
			self.draw()	
			pygame.display.flip()
			for event in pygame.event.get():
				if event.type == QUIT:
					return
				elif event.type == KEYDOWN and event.key == K_ESCAPE:
					return
				elif event.type == KEYDOWN and len(event.unicode)==1 and event.key!=K_BACKSPACE:
					self.testZone.changeText(self.testZone.text + event.unicode)
				elif event.type == KEYDOWN and event.key==K_BACKSPACE:
					self.testZone.changeText(self.testZone.text[:-1])
				elif event.type == MOUSEBUTTONDOWN:
					self.handleClick(event.pos)


Application().mainLoop()