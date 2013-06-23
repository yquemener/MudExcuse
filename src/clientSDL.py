# -*- coding: utf-8 -*-

import pygame
from time import *
import random
import math
from pygame.locals import *
import socket
from threading import *
import cPickle
import hashlib
import traceback
import sys

class ConfigSingleton:
	def __init__(self):
		#self.HOST = '192.168.0.1'    # The remote host
		self.HOST = 'localhost'
		self.PORTCOMMAND = 50008              # The same port as used by the server
		self.PORTLISTEN = 50007              # The same port as used by the server
		self.DEBUG_TEXTOUTPUT = False
		self.SIZE_UMAP = 48
		self.SIZE_MENU = 200
		self.SHA = None				# Will be filled with the username+password hash as soon as connection occurs

CONFIG = ConfigSingleton()
#----------------------------------------------------------------------

def listeningThread(app, user):
	global CONFIG
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((CONFIG.HOST, CONFIG.PORTLISTEN))
	s.send(cPickle.dumps((user,CONFIG.SHA)))
	data =s.recv(1024)
	if data!="OK":
		print "Erreur de connection"
		app.listeningThreadStatus=-1
		return
	app.listeningThreadStatus=1
	while 1:
		data=""
		while len(data)<8:
			data += s.recv(8-len(data))
		size=int(data)
		data=""
		while len(data)<size:
			data+= s.recv(size-len(data))
		if not data: break
		try:
			app.appendNetworkData(cPickle.loads(data))
		except Exception, e:
			print e
			pass
	s.close()

#------------------------------------------------------------------------------

class Object:
	def __init__(self):
		self.destroyMe=False
		self.zLevel=0
		
	def update(self, deltaT):
		return
	
	def draw(self, screen):
		return


#------------------------------------------------------------------------------

class Exit(Object):
	def __init__(self, game, orient, toolTipText):	
		Object.__init__(self)
		global CONFIG
		if orient=="N":
			door_X = game.size[0]/2 + CONFIG.SIZE_MENU/ 2 - CONFIG.SIZE_UMAP
			self.rect=pygame.Rect(door_X, CONFIG.SIZE_UMAP,2*CONFIG.SIZE_UMAP,CONFIG.SIZE_UMAP)
		elif orient=="S":
			door_Y = game.size[1] - 2*CONFIG.SIZE_UMAP
			door_X = game.size[0]/2 + CONFIG.SIZE_MENU/ 2 - CONFIG.SIZE_UMAP
			self.rect=pygame.Rect(door_X,door_Y,2*CONFIG.SIZE_UMAP,CONFIG.SIZE_UMAP)
		elif orient=="W":
			door_Y = game.size[1] / 2 - CONFIG.SIZE_UMAP
			door_X = CONFIG.SIZE_MENU + CONFIG.SIZE_UMAP
			self.rect=pygame.Rect(door_X,door_Y,CONFIG.SIZE_UMAP,2*CONFIG.SIZE_UMAP)
		elif orient=="E":
			door_Y = game.size[1] / 2 - CONFIG.SIZE_UMAP
			door_X = game.size[0] - 2 * CONFIG.SIZE_UMAP
			self.rect=pygame.Rect(door_X,door_Y,CONFIG.SIZE_UMAP,2*CONFIG.SIZE_UMAP)
		else:
			raise Exception("Could not create Exit", str(orient)+" is an incorrect orientation")
		
		self.game=game
		
		self.toolTip = Text(game, toolTipText, (self.rect[0], self.rect[1]))
		self.toolTip.visible = False
		game.InterfaceRoomElements.append(self.toolTip)
			
	def draw(self, screen):
		pygame.draw.rect(screen, (150,50,50), self.rect)
		#self.toolTip.draw(screen)
		
	def update(self, deltaT):
		(x,y) = pygame.mouse.get_pos()
		if 0<x-self.rect[0]<self.rect[2] and 0<y-self.rect[1]<self.rect[3]:
			self.toolTip.visible=True
			posx = min(x,self.game.size[0]-self.toolTip.surface.get_width())
			posy = min(y-self.toolTip.surface.get_height(),self.game.size[1]-self.toolTip.surface.get_height())
			self.toolTip.pos=(posx,posy)
		else:
			self.toolTip.visible=False

#------------------------------------------------------------------------------

class Unit(Object):
	def __init__(self, game, placeIndex, toolTipText, picName, width=0):
		Object.__init__(self)
		global CONFIG
		self.surface = pygame.image.load("../img/"+picName)
		
		self.game=game
		self.rect=[CONFIG.SIZE_MENU+3*CONFIG.SIZE_UMAP,CONFIG.SIZE_UMAP*(2+placeIndex), self.surface.get_width(), self.surface.get_height()]
		self.toolTip = Text(game, toolTipText, (self.rect[0], self.rect[1]))
		self.toolTip.visible = False
		self.width=width
		game.InterfaceRoomElements.append(self.toolTip)
	
	def draw(self, screen):
		w=self.width
		if w>0:
			r=[self.rect[0]-w/2, self.rect[1]-w/2, self.rect[2]+w, self.rect[3]+w]
			pygame.draw.rect(screen, (255,255,255), r, w)
		screen.blit(self.surface, (self.rect[0], self.rect[1]))
		#self.toolTip.draw(screen)
		
	def update(self, deltaT):
		(x,y) = pygame.mouse.get_pos()
		if 0<x-self.rect[0]<self.rect[2] and 0<y-self.rect[1]<self.rect[3]:
			self.toolTip.visible=True
			posx = min(x,self.game.size[0]-self.toolTip.surface.get_width())
			posy = min(y-self.toolTip.surface.get_height(),self.game.size[1]-self.toolTip.surface.get_height())
			self.toolTip.pos=(posx,posy)
		else:
			self.toolTip.visible=False
		
#------------------------------------------------------------------------------

class Player(Object):
	def __init__(self, game, placeIndex, toolTipText, picName, width=0):
		Object.__init__(self)
		global CONFIG
		if toolTipText==game.playerName:
			self.localPlayer=True
		else:
			self.localPlayer=False
			
		self.surface = pygame.image.load("../img/"+picName)
		
		self.game=game
		
		self.rect=[CONFIG.SIZE_MENU+3*CONFIG.SIZE_UMAP,CONFIG.SIZE_UMAP*(2+placeIndex), self.surface.get_width(), self.surface.get_height()]
		self.toolTip = Text(game, toolTipText, (self.rect[0], self.rect[1]))
		self.toolTip.visible = False
		game.InterfaceRoomElements.append(self.toolTip)
	
	def draw(self, screen):
		screen.blit(self.surface, (self.rect[0], self.rect[1]))
		if self.localPlayer:
			percent = min(100.0, self.game.playerLastTinfo[0] + 100.0*(time()-self.game.playerLastTinfo[1])/self.game.playerStats[2])
			r=[self.rect[0]+self.rect[2]-4, self.rect[1], 4, percent/100.0*self.rect[3]]
			if percent<100:
				pygame.draw.rect(screen, (255,0,0), r)
			else:
				pygame.draw.rect(screen, (255,255,255), r)
		#self.toolTip.draw(screen)
		
	def update(self, deltaT):
		(x,y) = pygame.mouse.get_pos()
		if 0<x-self.rect[0]<self.rect[2] and 0<y-self.rect[1]<self.rect[3]:
			self.toolTip.visible=True
			posx = min(x,self.game.size[0]-self.toolTip.surface.get_width())
			posy = min(y-self.toolTip.surface.get_height(),self.game.size[1]-self.toolTip.surface.get_height())
			self.toolTip.pos=(posx,posy)
		else:
			self.toolTip.visible=False

#------------------------------------------------------------------------------
class Monster(Object):
	def __init__(self, game, placeIndex, toolTipText, picName, hp):
		Object.__init__(self)
		global CONFIG
		self.surface = pygame.image.load("../img/"+picName)
		
		self.game=game
		self.hp=hp
		self.rect=[CONFIG.SIZE_MENU+3*CONFIG.SIZE_UMAP,CONFIG.SIZE_UMAP*(2+placeIndex), self.surface.get_width(), self.surface.get_height()]
		self.toolTip = Text(game, toolTipText, (self.rect[0], self.rect[1]))
		self.toolTip.visible = False
		game.InterfaceRoomElements.append(self.toolTip)
		self.hpTip = Text(game, str(self.hp), (self.rect[0], self.rect[1]))
		x=self.rect[0]+self.rect[2]-self.hpTip.surface.get_width()
		y=self.rect[1]+self.rect[3]-self.hpTip.surface.get_height()
		self.hpTip.pos = (x,y)
		#print x,y, hp, toolTipText
	
	
	def draw(self, screen):
		screen.blit(self.surface, (self.rect[0], self.rect[1]))
		self.hpTip.draw(screen)
		#self.toolTip.draw(screen)
		
	def update(self, deltaT):
		(x,y) = pygame.mouse.get_pos()
		if 0<x-self.rect[0]<self.rect[2] and 0<y-self.rect[1]<self.rect[3]:
			self.toolTip.visible=True
			posx = min(x,self.game.size[0]-self.toolTip.surface.get_width())
			posy = min(y-self.toolTip.surface.get_height(),self.game.size[1]-self.toolTip.surface.get_height())
			self.toolTip.pos=(posx,posy)
		else:
			self.toolTip.visible=False
		self.hpTip.changeText(str(self.hp))
		x=self.rect[0]+self.rect[2]-self.hpTip.surface.get_width()
		y=self.rect[1]+self.rect[3]-self.hpTip.surface.get_height()
		self.hpTip.pos = (x,y)
			


#------------------------------------------------------------------------------

class SwitchMeleeButton(Object):
	def __init__(self, game, pos):
		Object.__init__(self)
		self.surface = pygame.image.load("../img/fleche.png")
		self.game=game
		self.rect=[pos[0], pos[1], self.surface.get_width(), self.surface.get_height()]
		self.visible=False
			
	def draw(self, screen):
		if self.visible:
			screen.blit(self.surface, (self.rect[0], self.rect[1]))
		
	def update(self, deltaT):
		(x,y) = pygame.mouse.get_pos()
		if 0<x-self.rect[0]<self.rect[2] and 0<y-self.rect[1]<self.rect[3]:
			self.visible=True
		else:
			self.visible=False


#------------------------------------------------------------------------------
# Background image
class Tile(Object):
	def __init__(self, game, placeIndex, toolTipText, picName):
		Object.__init__(self)
		global CONFIG
		self.surface = pygame.image.load("../img/" + picName)
		self.game=game
		
		self.picName = picName

	def draw(self, screen):
		ItX = (self.game.size[0] - CONFIG.SIZE_MENU - 4*CONFIG.SIZE_UMAP) / CONFIG.SIZE_UMAP
		ItY = (self.game.size[1] - 4*CONFIG.SIZE_UMAP) / CONFIG.SIZE_UMAP
		for xi in range (ItX):
			for yi in range (ItY):
				self.rect=[CONFIG.SIZE_MENU+2*CONFIG.SIZE_UMAP+xi*CONFIG.SIZE_UMAP,2*CONFIG.SIZE_UMAP+yi*CONFIG.SIZE_UMAP,self.surface.get_width(), self.surface.get_height()]
				screen.blit(self.surface, (self.rect[0], self.rect[1]))

	def update(self, deltaT):
		return
#------------------------------------------------------------------------------

class Text(Object):
	def __init__(self, game, text, pos, font=None):
		Object.__init__(self)
		self.text=text
		self.game=game
		self.pos=pos
		self.visible=True
		self.zLevel=1
		if font==None:
			self.font=self.game.font
		else:
			self.font=font
		self.surface=self.font.render(text, False, (255,255,255))
		
	def changeBackgroundColor(self, color):
		self.surface=self.game.font.render(self.text, False, (255,255,255), color)

	def changeText(self, text):
		self.text=text
		self.surface=self.font.render(text, False, (255,255,255))
	
	def draw(self, screen):
		if self.visible:
			screen.blit(self.surface, self.pos)

#----------------------------------------------------------------------

class TextZone(Object):
	def __init__(self, game, text, rect, font=None, border=0):
		Object.__init__(self)
		self.text=text
		self.game=game
		self.pos=[rect[0], rect[1]]
		self.zLevel=1
		self.border=border
		if font==None:
			self.font=self.game.font
		else:
			self.font=font
		self.rect=rect
		self.surface=pygame.Surface((rect[2], rect[3]), depth=32)
		self.wordWrap()
		
	def wordWrap(self):
		self.surface.fill((0,0,0))
		x=0
		y=0
		for line in self.text.split('\n')[-5:]:
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
			x=0

	def draw(self, screen):
		screen.blit(self.surface, (self.rect[0], self.rect[1]))
		if self.border>0:
			r=pygame.Rect(self.rect[0]-1, self.rect[1]-1, self.rect[2]+2, self.rect[3]+2)
			pygame.draw.rect(screen, (255,255,255), r, self.border)

	def changeText(self, text):
		self.text=text
		self.wordWrap()

#----------------------------------------------------------------------


class DamageText(Text):
	def __init__(self, game, targetPos, amount):
		Text.__init__(self, game, str(amount), [targetPos[0], targetPos[1]])
		self.ttl=2.0
	
	def update(self, deltaT):
		self.ttl-=deltaT
		self.pos[1]-=deltaT*50
		if self.ttl<0:
			self.destroyMe=True
			
	def draw(self,screen):
		Text.draw(self,screen)
	
#----------------------------------------------------------------------

class Application:
	
	def __init__(self):
		self.networkData = []
		self.networkDataLock = Lock()
		self.listeningThread = None
		self.listeningThreadStatus = 0
		self.currentPlaceShortdesc=u""
		self.currentPlaceExits=[]
		self.currentPlacePeople=[]
		self.currentPlaceItems=[]
		self.currentPlaceTile=[]
		self.currentPlaceMonsters=[]
		self.currentPlaceBastonMode=False
		self.playerName="____"
		self.playerStats=[0,0,0,2.0]
		self.playerInventory=[]
		self.playerUnsheathedWeapon=False
		self.playerUnsheathedWeaponStats=[0.0,0.0,1.0,False]
		self.playerLastTinfo=(100, 0.0)
		self.clickArea=[]
		self.interfaceInitialized=False
		self.size = (640, 480)
		self.thingsPosition = {}
		
	def initSDL(self):
		pygame.init()
		d = pygame.display.Info()
		print "Resolution : " + str(d.current_w) + "*" + str(d.current_h)
		self.size = (d.current_w, d.current_h- 50)
		self.size = (1024, 600)		
		self.screen = pygame.display.set_mode(self.size)		
		pygame.display.set_caption('Client SDL de GLMud')
		pygame.font.init()
		self.font=pygame.font.Font("Vera.ttf", 23)
		self.lastTime=-1
		self.objList=[]

	def initInterface(self):
		self.TXTRoomShortdesc=Text(self, self.currentPlaceShortdesc, (200,46))
		self.objList.append(self.TXTRoomShortdesc)
		self.chatEnter=Text(self, "", (220,500))
		self.objList.append(self.chatEnter)
		self.chatLog=TextZone(self, "", Rect(220,530,550,69), font=pygame.font.Font("Vera.ttf", 12), border=1)
		self.objList.append(self.chatLog)
		self.InterfaceRoomElements = []
		self.interfaceInitialized=True
	
	def updateInterface(self):
		if(not self.interfaceInitialized):
			return

		for a in self.InterfaceRoomElements:
			self.objList.remove(a)
		self.clickArea=list()
		self.InterfaceRoomElements=list()
		
		self.TXTRoomShortdesc.changeText(self.currentPlaceShortdesc)
		y=90

		# Background texture
		if (len(self.currentPlaceTile)>0):
			t=Tile(self, 0, str(self.currentPlaceTile), str(self.currentPlaceTile))
			self.InterfaceRoomElements.append(t)
			#self.objList.append(t)
			
		for e in self.currentPlaceExits:
			t=Exit(self, e[3], unicode(e[1], 'utf-8'))
			self.InterfaceRoomElements.append(t)
			#self.objList.append(t)
			self.clickArea.append((t.rect, self.onClickExit, e[0]))
	
		# Acteurs
		melees=[]
		for i in range(8):
			melees.append(list())

		for p in self.currentPlacePeople:
			melees[p[2]].append(("people",)+p)
		
		for m in self.currentPlaceMonsters:
			#print m
			melees[m[3]].append(("monster",)+m)

		for p in self.currentPlaceItems:
			melees[p[3]].append(("item",)+p)

		for i in range(8):
			x=0
			b=SwitchMeleeButton(self, (CONFIG.SIZE_MENU+2*CONFIG.SIZE_UMAP,(2+i)*48))
			self.InterfaceRoomElements.append(b)
			#self.objList.append(b)
			self.clickArea.append((b.rect, self.onClickGoMelee, i))				
			for unit in melees[i]:
				
				if unit[0]=="people":
					t=Player(self, i, unicode(unit[2], 'utf-8'), "../img/joueur.png")
					t.rect[0]+=x
					x+=t.rect[2]+3
					self.thingsPosition[unit[1]]=(t.rect[0], t.rect[1])
					self.InterfaceRoomElements.append(t)
					#self.objList.append(t)
					self.clickArea.append((t.rect, lambda(x):0, unit[2]))
				if unit[0]=="item":					
					t=Unit(self, i, unicode(unit[2], 'utf-8'), unit[3])
					t.rect[0]+=x
					x+=t.rect[2]+3
					self.thingsPosition[unit[1]]=(t.rect[0], t.rect[1])
					self.InterfaceRoomElements.append(t)
					#self.objList.append(t)
					self.clickArea.append((t.rect, self.onPickItem, unit[1]))
				if unit[0]=="monster":	
					#print unit				
					t=Monster(self, i, unicode(unit[2], 'utf-8'), unit[3], unit[5])
					t.rect[0]+=x
					x+=t.rect[2]+3
					self.thingsPosition[unit[1]]=(t.rect[0], t.rect[1])
					self.InterfaceRoomElements.append(t)
					#self.objList.append(t)
					self.clickArea.append((t.rect, self.onAttackMonster, unit[1]))

		# Feuille de perso
		t=Text(self, self.playerName, (10,10))
		self.InterfaceRoomElements.append(t)
		#self.objList.append(t)
		
		t=Text(self, "ATT :"+str(self.playerStats[0]+self.playerUnsheathedWeaponStats[0]), (10,70))
		self.InterfaceRoomElements.append(t)
		#self.objList.append(t)
		
		t=Text(self, "DEF :"+str(self.playerStats[1]), (10,95))
		self.InterfaceRoomElements.append(t)
		#self.objList.append(t)

		t=Text(self, "DOM :"+str(self.playerUnsheathedWeaponStats[1]), (10,120))
		self.InterfaceRoomElements.append(t)
		#self.objList.append(t)

		t=Text(self, "PV :"+str(self.playerStats[3]), (10,145))
		self.InterfaceRoomElements.append(t)
		#self.objList.append(t)
		
		t=Text(self, "Inventaire :", (10,180))
		self.InterfaceRoomElements.append(t)
		#self.objList.append(t)
		
		y=180+30
		iconPic="ATTpoing.png"
		for item in self.playerInventory:
			if item[0]==self.playerUnsheathedWeapon:
				t=Unit(self, 0, unicode(item[1], 'utf-8'), item[2], width=1)
				iconPic="ATT"+item[2]
			else:
				t=Unit(self, 0, unicode(item[1], 'utf-8'), item[2])
			t.rect[0]=10
			t.rect[1]=y
			self.InterfaceRoomElements.append(t)
			#self.objList.append(t)
			#self.clickArea.append((t.rect, self.onDropItem, item[0]))
			self.clickArea.append((t.rect, self.onClickUnsheath, item[0]))			
			y+=t.rect[3]
		
		if self.currentPlaceBastonMode:
			t=Text(self, "BASTON !", (100+self.size[0]/2,50))
			self.InterfaceRoomElements.append(t)
			#self.objList.append(t)
			
		t=Unit(self, 0, "", iconPic)
		t.rect[0]=200-10-t.rect[2]
		t.rect[1]=self.size[1]-5-t.rect[3]
		if self.playerUnsheathedWeapon!=None:
			t.toolTip.changeText("Rengainer")
			self.clickArea.append((t.rect, self.onClickUnsheath, None))
		self.InterfaceRoomElements.append(t)
		#self.objList.append(t)
		self.objList = self.objList+self.InterfaceRoomElements
		return
		
	def onClickWeapon(self, arg):
		self.currentPlaceBastonMode= not self.currentPlaceBastonMode
		self.updateInterface()

	def onClickExit(self, arg):
		self.SendCommand(("go",arg))
	
	def onPickItem(self, arg):
		self.SendCommand(("pick",arg))

	def onDropItem(self, arg):
		self.SendCommand(("drop",arg))

	def onClickGoMelee(self, arg):
		self.SendCommand(("goMelee",arg))
	
	def onClickUnsheath(self, arg):
		self.SendCommand(("unsheath", arg))

	def onAttackMonster(self, arg):
		self.SendCommand(("attack", arg))
		
	def onEnterChatLine(self, arg):
		self.SendCommand(("say", arg))
	
	def handleClick(self, pos):
		for area in self.clickArea:
			a=area[0]
			if 0<pos[0]-a[0]<a[2] and 0<pos[1]-a[1]<a[3]:
				area[1](area[2])
	
	def appendNetworkData(self, data):
		self.networkDataLock.acquire()
		self.networkData.append(data)
		self.networkDataLock.release()
		
	def processNetworkEventsQueue(self):
		self.networkDataLock.acquire()
		while len(self.networkData)>0:
			line = self.networkData.pop(0)
			
			if line[0]=='chat':
				#print line
				self.chatLog.changeText(self.chatLog.text + line[1]+":"+line[2]+"\n")
				
			elif line[0]=='desc':
				self.currentPlaceShortdesc=unicode(line[1], 'utf-8')
				self.currentPlaceExits=line[2]
				self.currentPlacePeople=line[3]
				self.currentPlaceItems=line[4]
				self.currentPlaceTile=line[5]
				self.currentPlaceBastonMode=line[6]
				self.currentPlaceMonsters=line[7]				

				self.updateInterface()
				if CONFIG.DEBUG_TEXTOUTPUT:
					print "*"*(len(line[1])+4)
					print "*",line[1],"*"
					print "*"*(len(line[1])+4)
					print "Background received : " + str(line[5]) 				
					for e in line[2]:
						print str(e[0])+")  "+e[1]+" mène à "+e[2]
					print
					print "Sont présents:"
					for e in line[3]:
						print e
					print '__'*10
			elif line[0]=='charac':
				self.playerName=unicode(line[1], 'utf-8')
				self.playerStats=line[2]
				self.playerInventory=line[3]
				self.playerUnsheathedWeapon=line[4]
				self.playerUnsheathedWeaponStats=line[5]
				self.updateInterface()
				if CONFIG.DEBUG_TEXTOUTPUT:
					print "*"*(len(line[1])+4)
					print "*",line[1],"*"
					print "*"*(len(line[1])+4)
				
					print "ATT:", line[2][0],"\nDEF:", line[2][1],"\nSAU:",line[2][2]
					print
					print "Inventaire:"
					for e in line[3]:
						print e
			elif line[0]=='damage':
				self.objList.append(DamageText(self, self.thingsPosition.get(line[1],(-100,-100)), line[2]))
				#print "#"+str(line[1])+" se prend "+str(line[2])+" dommages dans la courge",self.thingsPosition.get(line[1],(-100,-100))
			elif line[0]=='die':
				self.objList.append(Text(self, "VOUS ETES MORT ! C'EST BALO...", (400,250)))
				
			elif line[0]=='tinfo':
				self.playerLastTinfo=(float(line[1]), time())
				#print self.playerLastTinfo
				
			elif line[0]=='OK':
				pass
			else:
				print 'Unknown network event dumped :',line
		self.networkDataLock.release()

	def SendCommand(self, command):
		global CONFIG		
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((CONFIG.HOST, CONFIG.PORTCOMMAND))
		tosend = tuple((CONFIG.SHA,))+tuple(command)
		s.send(cPickle.dumps(tosend))
		data = s.recv(1024)
		s.close()

	def cleanDestroyed(self):
		i=0
		while len(self.objList)>i:
			if self.objList[i].destroyMe:
				self.objList.pop(i)
			else:
				i=i+1
	
	def update(self):
		self.toBeAdded=list()
		if self.lastTime==-1:
			self.lastTime=time()
			return
		deltaT=time() - self.lastTime
		self.lastTime=time()
		for obj in self.objList:
			obj.update(deltaT)
		self.cleanDestroyed()
		self.objList = self.toBeAdded[:] + self.objList
		

	def draw(self):
		self.screen.fill((0,0,0))
		
		# Ligne de séparation de la feuille de perso
		pygame.draw.rect(self.screen, (250,250,250), (CONFIG.SIZE_MENU,0,2,self.size[1]))

		#Tri des objets dans l'ordre d'affichage
		self.objList.sort(lambda x,y:x.zLevel-y.zLevel)
		
		# Affichage des objets		
		for obj in self.objList:
			obj.draw(self.screen)

		# Affichage des rectangles contenant les mêlées
		# Pour l'instant : seulement huit mêlées dans la pièce
		#for i in range(8):
		#	pygame.draw.rect(self.screen, (0,255,0), Rect(CONFIG.SIZE_MENU+2*CONFIG.SIZE_UMAP,2*CONFIG.SIZE_UMAP+i*CONFIG.SIZE_UMAP, self.size[0]-4*CONFIG.SIZE_UMAP-CONFIG.SIZE_MENU, CONFIG.SIZE_UMAP), 1)	
	
	def MainLoop(self):
		global CONFIG
		running=True
		while(self.listeningThreadStatus!=1):
			self.listeningThreadStatus=0
			user=raw_input("Nom d'utilisateur :")
			passw=raw_input("Mot de passe :")
			CONFIG.SHA = hashlib.sha1(user+"@"+passw).hexdigest()
			self.listeningThread = Thread(target=listeningThread, args=(self,user))
			self.listeningThread.daemon=True
			self.listeningThread.setDaemon(True)
			self.listeningThread.start()
			
			while(self.listeningThreadStatus==0):
				sleep(0.1)
				
		self.initSDL()
		self.initInterface()
		self.updateInterface()

		while(running):
			try:
				self.processNetworkEventsQueue()
				self.update()
				self.draw()	
				pygame.display.flip()
				toSleep=0.02-time()+self.lastTime
				if toSleep>0:
					sleep(toSleep)
				for event in pygame.event.get():
					if event.type == QUIT:
						return
					elif event.type == KEYDOWN and event.key == K_ESCAPE:
						return
					elif event.type == KEYDOWN and event.key==K_BACKSPACE:
						self.chatEnter.changeText(self.chatEnter.text[:-1])
					elif event.type == KEYDOWN and event.key==K_RETURN:
						self.onEnterChatLine(self.chatEnter.text)
						self.chatEnter.changeText("")
					elif event.type == KEYDOWN and len(event.unicode)==1:
						self.chatEnter.changeText(self.chatEnter.text + event.unicode)
					elif event.type == MOUSEBUTTONDOWN:
						self.handleClick(event.pos)
					
			except Exception, e:
				print "Fais un peu gaffe ! ",e
				traceback.print_tb(sys.exc_info()[2],4)
				raise e
			

#------------------------------------------------------------------------------

app = Application()
app.MainLoop()

pygame.display.quit()
