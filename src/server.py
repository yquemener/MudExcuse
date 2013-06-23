# -*- coding: utf-8 -*-

# One thread to receive connections and create sockets that stays open to the client
# One thread to receive orders from a single port and answer "ACK"
# The main thread manages an event loop fed by the second thread and regularly checks if the clients need updates of their informations 

import socket
from time import *
from random import *
from threading import *
import cPickle
import hashlib

Things = {}

nextIdx=0

def newIdx():
	global nextIdx
	nextIdx=nextIdx+1
	return nextIdx

class Thing:
	def __init__(self, category, index=None):
		self.category = category
		if index==None:
			self.index = newIdx()
		else:
			self.index=index
		return

class User(Thing):
	def __init__(self, name, password, place, meleeNum=0):
		Thing.__init__(self,"user")
		self.name = name
		self.password = password
		self.place = place
		self.meleeNum = meleeNum
		self.stats=[50,0,1.0,100] #Attaque , défense, vitesse d'action, PV
		self.dead=False # Laissons lui une chance...
		self.inventory=[]
		self.sha = hashlib.sha1(name+"@"+password).hexdigest()
		self.unsheathedWeapon=None
		self.lastActionTime=0.0
		return

class Room(Thing):
	def __init__(self, shortdesc, picname=""):
		Thing.__init__(self,"room")
		self.shortdesc = shortdesc
		self.bastonMode=False	
		self.picname=picname
		return

class Exit(Thing):
	def __init__(self, src, dst,  shortdesc, orient, hidden):
		Thing.__init__(self,"exit")
		self.shortdesc = shortdesc
		self.place = src
		self.destination = dst
		self.orientation = orient
		self.hidden = hidden
		return
		
class Item(Thing):
	def __init__(self, shortdesc, imgName, place, meleeNum=0, fixated=False, weaponStats=[0,0,1.0,False]):
		Thing.__init__(self,"item")
		self.shortdesc = shortdesc
		self.place = place
		self.meleeNum = meleeNum
		self.imageName = imgName
		self.fixated = fixated
		self.weaponStats=weaponStats 		# Bonus d'attaque, Dommages, modificateur de vitesse, isArmeADistance?
		return
		
class Monster(Thing):
	def __init__(self, shortdesc, imgName, place, meleeNum=0, stats=[0,0,0,1.0,False,10]):
		Thing.__init__(self, "monster")
		self.place=place
		self.imageName = imgName
		self.meleeNum = meleeNum
		self.shortdesc=shortdesc
		self.stats = stats					# [ATT, DEF, DOM, VIT, DISTANCE,HP]
		self.lastActionTime = time()+randint(-10,10)/20.0
		
	def act(self, server):
		global Things
		# Test if you can attack
		for t in Things.values():
			if t.category=="user":
				if t.place==self.place:
					if t.meleeNum==self.meleeNum and not t.dead:
						damage = self.stats[2]
						t.stats[3] = t.stats[3]-damage
						server.eventQueueLock.acquire()
						server.SendToEveryoneInPlace(t.place, ("damage", t.index,damage))
						server.eventQueue.append((t.sha, "charac", ""))
						server.eventQueueLock.release()
						return True
		# If not, move
		self.meleeNum = randint(0,7)
		return True

		


def addRoom(shortdesc, picname=""):
	global Things
	r= Room(shortdesc, picname)
	Things[r.index] = r
	return r.index

def addExit(roomShortDesc, destShortDesc, shortdesc, orient, hidden=False):
	global Things

	if orient not in ["N","S","E","W"]:
		raise Exception("Can't create Exit "+str(shortdesc), str(orient)+" is not a cardinal point")
		return

	count=0;
	for k in Things.keys():
		t=Things[k]
		if t.category=="room" and t.shortdesc==roomShortDesc:
			candidate = k
			count=count+1
	if count>1:
		raise Exception("Can't create Exit "+str(shortdesc), "Ambiguous start location :"+ str(roomShortDesc))
		return
	elif count==0:
		raise Exception("Can't create Exit "+str(shortdesc), "No start location :"+ str(roomShortDesc))
		return
	else:
		src=candidate
		
	count=0;
	for k in Things.keys():
		t=Things[k]
		if t.category=="room" and t.shortdesc==destShortDesc:
			candidate = k
			count=count+1
	if count>1:
		raise Exception("Can't create Exit "+str(shortdesc), "Ambiguous destination :"+ str(destShortDesc))
		return
	elif count==0:
		raise Exception("Can't create Exit "+str(shortdesc), "No destination :"+ str(destShortDesc))
		return
	else:
		dst=candidate
	e=Exit(src,dst, shortdesc, orient, hidden)
	Things[e.index]=e
	return e.index

def addItem(shortdesc, imgName, roomShortDesc, fixated=False):
	global Things
	count=0;
	for k in Things.keys():
		t=Things[k]
		if t.category=="room" and t.shortdesc==roomShortDesc:
			candidate = k
			count=count+1
	if count>1:
		raise Exception("Can't place Item "+str(shortdesc), "Ambiguous start location :"+ str(roomShortDesc))
		return
	elif count==0:
		raise Exception("Can't place Item "+str(shortdesc), "No start location :"+ str(roomShortDesc))
		return
	else:
		room=candidate
		
	e=Item(shortdesc, imgName, room, fixated=fixated)
	Things[e.index]=e
	return e.index

def addWeapon(shortdesc, imgName, roomShortDesc, weaponStats):
	global Things
	count=0;
	for k in Things.keys():
		t=Things[k]
		if t.category=="room" and t.shortdesc==roomShortDesc:
			candidate = k
			count=count+1
	if count>1:
		raise Exception("Can't place Item "+str(shortdesc), "Ambiguous start location :"+ str(roomShortDesc))
		return
	elif count==0:
		raise Exception("Can't place Item "+str(shortdesc), "No start location :"+ str(roomShortDesc))
		return
	else:
		room=candidate
	e=Item(shortdesc, imgName, room, fixated=False, weaponStats=weaponStats)
	Things[e.index]=e
	return e.index

def addMonster(shortdesc, imgName, roomShortDesc, stats):
	global Things
	count=0;
	for k in Things.keys():
		t=Things[k]
		if t.category=="room" and t.shortdesc==roomShortDesc:
			candidate = k
			count=count+1
	if count>1:
		raise Exception("Can't place Item "+str(shortdesc), "Ambiguous start location :"+ str(roomShortDesc))
		return
	elif count==0:
		raise Exception("Can't place Item "+str(shortdesc), "No start location :"+ str(roomShortDesc))
		return
	else:
		room=candidate
		
	e=Monster(shortdesc, imgName, room, stats=stats)
	Things[e.index]=e
	return e.index

class UserConnection:
	def __init__(self):
		self.username = None
		self.hash = None
		self.socket = None

	def authenticate(self, name, sha):
		for t in Things.values():
			if t.category=="user":
				if t.name==name:
					if hashlib.sha1(t.name + "@" + t.password).hexdigest()==sha:
						self.username=name
						self.hash=sha
						return True
					else:
						return False


def addUser(name, password, startPlace):
	global Things
	u=User(name, password, startPlace)
	Things[u.index]=u


execfile("server_map1.py")
init_map()

class Server:
	def __init__(self):
		self.host = ''
		self.connectPort = 50007
		self.commandPort = 50008
		self.connectionList = []
		self.connectionDict = {}
		self.connectionListLock = Lock()
		self.eventQueue = []
		self.eventQueueLock = Lock()
		self.thingsLock = Lock()
		self.alive = True
		
		"""self.eventsMap={
			"usr":lambda(x):None,
			"say":onSay,
			"desc":onDesc,
			"charac":onCharac,
			"go":onGo,
			"pick":onPick,
			"attack":onAttack,
			"drop": onDrop,
			"goMelee": onGoMelee,
			"unsheath":onUnsheath,
			"tinfo": onTinfo
		}"""
		
		thread1 = Thread(target=self.connectThread)
		thread1.daemon = True
		thread1.setDaemon(True)
		thread1.start()

		thread2 = Thread(target=self.receiveCommandsThread)
		thread2.daemon = True
		thread2.setDaemon(True)
		thread2.start()
		return

	def connectThread(self):
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.bind((self.host, self.connectPort))
		s.listen(5)
		print "Waiting for connection"
		while self.alive:
			conn, addr = s.accept()
			print 'Connected by', addr
			data = conn.recv(1024)
			try:
				(user,sha)=cPickle.loads(data)
				print user, sha
			except Exception:
				print 'ERR'
				conn.send('ERR')
				conn.close()
				continue
				
			uc=UserConnection()
			if uc.authenticate(user, sha):
				uc.socket=conn
				self.connectionListLock.acquire()
				self.connectionList.append(uc)
				self.connectionDict[sha]=(uc)
				self.connectionListLock.release()
				conn.send('OK')
				print "OK"
				# Appends a desc command to the event queue
				self.eventQueueLock.acquire()
				self.eventQueue.append((sha, "desc",""))
				self.eventQueue.append((sha, "charac",""))
				self.eventQueueLock.release()		
			else:
				conn.send('ERR')
				print 'ERR'
				conn.close()

		s.close()
	
	def refreshPlace(self,indexPlace):
		global Things
		userlist=[]
		monstersList=[]
		exitsList=[]
		bastonMode=False
		for t in Things.values():
			if t.category=="user":
				if t.place==indexPlace:
					userlist.append(t.name)
					if t.unsheathedWeapon!=None:
						bastonMode=True
			if t.category=="monster":
				if t.place==indexPlace:
					monstersList.append(t)
			if t.category=="exit":
				if t.place==indexPlace:
					exitsList.append(t)
		if len(monstersList)==0:
			# On revèle les sorties cachées
			for e in exitsList:
				e.hidden=False
		Things[indexPlace].bastonMode=bastonMode
		for c in self.connectionList:
			if c.username in userlist:
				self.eventQueue.append((c.hash, "desc",""))

	def SendToEveryoneInPlace(self,indexPlace, cmd):
		global Things
		userlist=[]
		for t in Things.values():
			if t.category=="user":
				if t.place==indexPlace:
					userlist.append(t.name)
		print len(userlist)
		for c in self.connectionList:
			if c.username in userlist:
				self.eventQueue.append((c.hash,)+cmd)



	def receiveCommandsThread(self):
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.bind((self.host, self.commandPort))
		s.listen(5)
		while self.alive:
			conn, addr = s.accept()
			data = conn.recv(1024)
			conn.send('ACK')
			self.eventQueueLock.acquire()
			self.eventQueue.append(cPickle.loads(data))
			self.eventQueueLock.release()
		s.close()
		
	def sendAndInsist(self, c, message):
		try:
			sentBytes=0
			s=str(len(message))
			s=(8-len(s))*" "+s
			while sentBytes<8:
				sent=c.socket.send(s)
				sentBytes+=sent
	
			sentBytes=0
			while sentBytes<len(message):
				sent=c.socket.send(message[sentBytes:])		
				sentBytes+=sent
		except Exception, e:
			if e[1]=="Broken pipe":
				# Le client s'est surement déconnecté, effacer sa connection de la liste
				print "failed in sendAndInsist"
				self.connectionList.remove(c)
				if self.connectionDict[c.hash]==c:
					self.connectionDict.pop(c.hash)

	def handleEvent(self, event):
		# Handle events
		if event[1] not in self.eventsMap.keys():
			print "Unkown network message :",event[1]
			return
		if self.connectionDict.has_key(event[0]):
			c=self.connectionDict[event[0]]
			for t in Things.values():
				if t.category=="user" and t.name==c.username:
					break
			player=t
			
		else:
			print "Reçu un message d'un utilisateur non connecté"
			return
		


		
	def run(self):
		global Things
		print "Server running"
		while(1):
			try:
				sleep(0)
				# Update world
				currentTime=time()
				placesToRefresh=set()
				for k in Things.keys():
					t = Things[k]
					if t.category=="monster":
						self.thingsLock.acquire()
						# Test death
						if t.stats[5]<1:
							placesToRefresh.add(t.place)
							Things.pop(k)
						# Test action
						if currentTime-t.lastActionTime>t.stats[3]:
							if t.act(self):
								t.lastActionTime=currentTime
								placesToRefresh.add(t.place)
						self.thingsLock.release()
					if t.category=="user":
						# Test death
						if not t.dead and t.stats[3]<1:
							t.dead=True
							placesToRefresh.add(t.place)
							self.eventQueueLock.acquire()
							self.eventQueue.append((t.sha, "die",""))
							self.eventQueueLock.release()
							
							
				#refresh the world for people who were in places that changed
				for place in placesToRefresh:
					self.refreshPlace(place)
							
				
				# Handle events
				self.eventQueueLock.acquire()
				while len(self.eventQueue)>0:
					e = self.eventQueue.pop(0)
					print "event :",e
					if e[1]=="usr":
						pass
					
					elif e[1]=="say":
						self.connectionListLock.acquire()
						sayer="None"
						for t in Things.values():
							if t.category=="user" and t.sha==e[0]:
								sayer=t.name
						whattosay=""
						for mot in e[2:]:
							whattosay+=mot+" "
						for c in self.connectionList[:]:
							try:
								self.sendAndInsist(c,cPickle.dumps(("chat",sayer,whattosay)))
							except Exception,e:
								print e
								pass
						self.connectionListLock.release()
						
					elif e[1]=="desc":
						if self.connectionDict.has_key(e[0]):
							c=self.connectionDict[e[0]]
							for t in Things.values():
								if t.category=="user" and t.name==c.username:
									break
							player=t
							exitlist=[]
							userlist=[]
							itemlist=[]
							tilelist=[]
							monsterlist=[]
							for t in Things.values():
								if t.category=="exit":
									if t.place == player.place and t.hidden==False:
										exitlist.append((t.index, t.shortdesc, Things[t.destination].shortdesc, t.orientation))
								if t.category=="user":
									if t.place == player.place:
										userlist.append((t.index, t.name, t.meleeNum))
								if t.category=="item" or t.category=="weapon":
									if t.place == player.place:
										itemlist.append((t.index, t.shortdesc, t.imageName, t.meleeNum, t.weaponStats))
								if t.category=="monster":
									if t.place == player.place:
										monsterlist.append((t.index, t.shortdesc, t.imageName, t.meleeNum, t.stats[5]))
							self.sendAndInsist(c,cPickle.dumps(("desc",	Things[player.place].shortdesc,
																		exitlist, 
																		userlist, 
																		itemlist, 
																		Things[player.place].picname, 
																		Things[player.place].bastonMode, 
																		monsterlist)))
	
						
					elif e[1]=="charac":
						if self.connectionDict.has_key(e[0]):
							c=self.connectionDict[e[0]]
							for t in Things.values():
								if t.category=="user" and t.name==c.username:
									break
							player=t
							inv=[]
							for i in player.inventory:
								inv.append((Things[i].index, Things[i].shortdesc, Things[i].imageName, Things[i].weaponStats))
							if player.unsheathedWeapon!=None:
								weaponStats=Things[player.unsheathedWeapon].weaponStats
							else:
								weaponStats=[0,1,1.0,False]
							self.sendAndInsist(c,cPickle.dumps(("charac",player.name, player.stats, inv, player.unsheathedWeapon, weaponStats)))
	
					elif e[1]=="go":
						if self.connectionDict.has_key(e[0]):
							c=self.connectionDict[e[0]]
							for t in Things.values():
								if t.category=="user" and t.name==c.username:
									break
							player=t
							place = Things[player.place]
							exitlist=[]
							userlist=[]
							t=None
							for t in Things.values():
								if t.category=="exit":
									if t.index == int(e[2]):
										break
							if t!=None:
								if player.lastActionTime+player.stats[2]<time():
									self.thingsLock.acquire()
									if place.bastonMode:
										player.lastActionTime=time()
									player.place = t.destination
									self.thingsLock.release()
									self.sendAndInsist(c,cPickle.dumps(("OK","")))
									# Appends a desc command to the event queue
									self.refreshPlace(t.destination)
									self.refreshPlace(t.place)
									self.eventQueue.append((e[0], "tinfo",""))
								else:
									self.sendAndInsist(c,cPickle.dumps(("NO","")))
							else:
								self.sendAndInsist(c,cPickle.dumps(("NO","")))
	
					elif e[1]=="pick":
						if self.connectionDict.has_key(e[0]):
							c=self.connectionDict[e[0]]
							for t in Things.values():
								if t.category=="user" and t.name==c.username:
									break
							player=t
							place = Things[player.place]
							exitlist=[]
							userlist=[]
							t=None
							for t in Things.values():
								if t.category=="item":
									if t.index == int(e[2]):
										break
							if t!=None and t.place==player.place and t.meleeNum==player.meleeNum and not t.fixated:
								if player.lastActionTime+player.stats[2]<time():
									self.thingsLock.acquire()
									if place.bastonMode:
										player.lastActionTime=time()
									t.place = player.index
									player.inventory.append(t.index)
									self.thingsLock.release()
									self.sendAndInsist(c,cPickle.dumps(("OK","")))
									# Appends a desc and a charac command to the event queue
									self.refreshPlace(player.place)
									self.eventQueue.append((e[0], "charac",""))
									self.eventQueue.append((e[0], "tinfo",""))
								else:
									self.sendAndInsist(c,cPickle.dumps(("NO","")))
							else:
								self.sendAndInsist(c,cPickle.dumps(("NO","")))
								
					elif e[1]=="attack":
						if self.connectionDict.has_key(e[0]):
							c=self.connectionDict[e[0]]
							for t in Things.values():
								if t.category=="user" and t.name==c.username:
									break
							player=t
							place = Things[player.place]
							exitlist=[]
							userlist=[]
							t=None
							for t in Things.values():
								if t.category=="monster":
									if t.index == int(e[2]):
										break
							failed = False
							if t==None: failed=True
							if t.place!=player.place: failed=True
							if not place.bastonMode: failed=True
							target=t
							if t.meleeNum!=player.meleeNum:
								if player.unsheathedWeapon!=None:
									if Things[player.unsheathedWeapon].weaponStats[3]==False: failed=True
								else: failed=True
							if player.lastActionTime+player.stats[2]>time(): failed=True
							
							if not failed:
								self.thingsLock.acquire()
								player.lastActionTime=time()
								if player.unsheathedWeapon==None:
									t.stats[5] = t.stats[5]-1
								else:
									damage = Things[player.unsheathedWeapon].weaponStats[1]
									t.stats[5] = t.stats[5]-damage
								self.thingsLock.release()
								self.sendAndInsist(c,cPickle.dumps(("OK","")))
								self.refreshPlace(player.place)
								self.SendToEveryoneInPlace(player.place, ("damage", target.index,damage))
								self.eventQueue.append((e[0], "charac",""))
								self.eventQueue.append((e[0], "tinfo",""))
							else:
								self.sendAndInsist(c,cPickle.dumps(("NO","")))
								
					elif e[1]=="damage":
						if self.connectionDict.has_key(e[0]):
							c=self.connectionDict[e[0]]
							for t in Things.values():
								if t.category=="user" and t.name==c.username:
									break
							player=t
							self.sendAndInsist(c,cPickle.dumps(e[1:]))
	
					elif e[1]=="drop":
						if self.connectionDict.has_key(e[0]):
							c=self.connectionDict[e[0]]
							for t in Things.values():
								if t.category=="user" and t.name==c.username:
									break
							player=t
							place = Things[player.place]
							exitlist=[]
							userlist=[]
							t=None
							for t in Things.values():
								if t.category=="item":
									if t.index == int(e[2]):
										break
							if t!=None and t.place==player.index:
								if player.lastActionTime+player.stats[2]<time():
									self.thingsLock.acquire()
									if place.bastonMode:
										player.lastActionTime=time()
									t.place = player.place
									t.meleeNum = player.meleeNum
									player.inventory.remove(t.index)
									self.thingsLock.release()
									self.sendAndInsist(c,cPickle.dumps(("OK","")))
									# Appends a desc and a charac command to the event queue
									#self.eventQueue.append((e[0], "desc",""))
									self.refreshPlace(player.place)
									self.eventQueue.append((e[0], "charac",""))
									self.eventQueue.append((e[0], "tinfo",""))
								else:
									self.sendAndInsist(c,cPickle.dumps(("NO","")))
							else:
								self.sendAndInsist(c,cPickle.dumps(("NO","")))
								
					elif e[1]=="goMelee":
						if self.connectionDict.has_key(e[0]):
							c=self.connectionDict[e[0]]
							for t in Things.values():
								if t.category=="user" and t.name==c.username:
									break
							player=t
							place = Things[player.place]
							if t!=None:
								if player.lastActionTime+player.stats[2]<time():
									self.thingsLock.acquire()
									if place.bastonMode:
										player.lastActionTime=time()
									player.meleeNum = e[2]
									self.thingsLock.release()
									self.sendAndInsist(c,cPickle.dumps(("OK","")))
									self.refreshPlace(player.place)
									self.eventQueue.append((e[0], "tinfo",""))
								else:
									self.sendAndInsist(c,cPickle.dumps(("NO","")))
							else:
								self.sendAndInsist(c,cPickle.dumps(("NO","")))
								
					elif e[1]=="unsheath":
						if self.connectionDict.has_key(e[0]):
							c=self.connectionDict[e[0]]
							for t in Things.values():
								if t.category=="user" and t.name==c.username:
									break
							player=t
							place = Things[player.place]
							failed=False
							if t==None:
								failed==True
							else:
								if player.lastActionTime+player.stats[2]<time():
									if e[2]==None or Things[e[2]].place==player.index:
										self.thingsLock.acquire()
										if place.bastonMode:
											player.lastActionTime=time()
										if e[2]==None:
											player.unsheathedWeapon = None
										else:
											player.unsheathedWeapon = e[2]
										self.thingsLock.release()
									else:
										failed=True
										
							if not failed:
								self.sendAndInsist(c,cPickle.dumps(("OK","")))
								self.refreshPlace(player.place)
								self.eventQueue.append((e[0], "charac",""))
								self.eventQueue.append((e[0], "tinfo",""))
							else:
								self.sendAndInsist(c,cPickle.dumps(("NO","")))

					elif e[1]=="die":
						if self.connectionDict.has_key(e[0]):
							c=self.connectionDict[e[0]]
							for t in Things.values():
								if t.category=="user" and t.name==c.username:
									break
							self.sendAndInsist(c,cPickle.dumps(("die","")))
	

					elif e[1]=="tinfo":			# Time info about the action counter
						if self.connectionDict.has_key(e[0]):
							c=self.connectionDict[e[0]]
							for t in Things.values():
								if t.category=="user" and t.name==c.username:
									break
							player=t
							if t!=None:
								self.thingsLock.acquire()
								actionBarPercent=min(100.0,100.0*(time()-player.lastActionTime)/player.stats[2])
								self.thingsLock.release()
								self.sendAndInsist(c,cPickle.dumps(("tinfo",actionBarPercent)))
							else:
								self.sendAndInsist(c,cPickle.dumps(("NO","")))
					
						
				self.eventQueueLock.release()
			except Exception, e:
				print "e",e
				self.alive=False

s=Server()
s.run()
