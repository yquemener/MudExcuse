# -*- coding: utf-8 -*-

import socket
from threading import *
import cPickle
import hashlib

HOST = 'yves.quemener.net'    # The remote host
PORTCOMMAND = 50008              # The same port as used by the server
PORTLISTEN = 50007              # The same port as used by the server

SHA = None				# Will be filled with the username+password hash as soon as connection occurs
#----------------------------------------------------------------------
def listeningThread(app, user):
	global HOST,PORTLISTEN,SHA
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((HOST, PORTLISTEN))
	s.send(cPickle.dumps((user,SHA)))
	data =s.recv(1024)
	if data!="OK":
		print "Erreur de connection"
		return
	while 1:
		data = s.recv(1024)
		if not data:break
		try:
			app.appendNetworkData(cPickle.loads(data))
		except Exception, e:
			print e
			pass
	s.close()

	

#----------------------------------------------------------------------


class Application:
	
	def __init__(self):
		self.networkData = []
		self.listeningThread = None

	def appendNetworkData(self, data):
		self.networkData.append(data)
		self.processNetworkEventsQueue()
		
	def processNetworkEventsQueue(self):
		while len(self.networkData)>0:
			line = self.networkData.pop(0)
			if line[0]=='say':
				print "("+line[1]+") "+line[2]
			elif line[0]=='desc':
				print "*"*(len(line[1])+4)
				print "*",line[1],"*"
				print "*"*(len(line[1])+4)
				
				for e in line[2]:
					print str(e[0])+")  "+e[1]+" mène à "+e[2]
				print
				print "Sont présents:"
				for e in line[3]:
					print e
				print '__'*10
			elif line[0]=='OK':
				pass
			else:
				print 'Unknown network event dumped :',line

	def SendCommand(self, command):
		global HOST, PORTCOMMAND, SHA		
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((HOST, PORTCOMMAND))
		tosend = tuple((SHA,))+tuple(command)
		s.send(cPickle.dumps(tosend))
		data = s.recv(1024)
		s.close()

	def MainLoop(self):
		global SHA
		running=True
		while(running):
			try:
				line=raw_input()
				cmd = line.split(" ")
				if(cmd[0] in ["c","C","connect"]):
					SHA = hashlib.sha1(cmd[1]+"@"+cmd[2]).hexdigest()
					self.listeningThread = Thread(target=listeningThread, args=(self,cmd[1]))
					self.listeningThread.daemon=True
					self.listeningThread.setDaemon(True)
					self.listeningThread.start()
					
				elif(cmd[0] in ["s","S","say"]):
					mots=""
					for mot in cmd[1:]:
						mots+=mot+" "
					self.SendCommand(("say",mots))

				elif(cmd[0] in ["d","D","desc"]):
					self.SendCommand(("desc",""))

				elif(cmd[0] in ["g","G","go"]):
					self.SendCommand(("go",cmd[1]))
					
				elif(cmd[0] in ["q", "Q", "quit"]):
					running=False
				
				elif(cmd[0] in ["h", "H", "help"]):
					print
					print "Commandes"
					print "c utilisateur motdepasse : se connecter au serveur, c'est la première action à faire"
					print "s phrase : dit la phrase à tous les utilisateurs connectés"
					print "d : fournit une description du lieu"
					print "g numero : emprunte la sortie du numero indiqué"

			except Exception, e:
				print "Fais un peu gaffe ! ",e
			

#------------------------------------------------------------------------------


app = Application()
app.MainLoop()

