# -*- coding: utf-8 -*-

def init_map():
	addRoom((5,5), "cour interieure",[True, True, False, True])
	addRoom((5,4), "allée des échoppes",[True, True, True, False])
	addRoom((5,3), "écurie démolie",[False, True, False, False])
	addRoom((5,6), "pont-levis",[True, False, False, False])
	
	addRoom((4,5), "chemin de ronde",[False, False, True, True])
	addRoom((3,5), "tourelle sud-ouest",[True, False, True, False])
	addRoom((3,4), "chemin de ronde",[True, True, False, False])
	addRoom((3,3), "tourelle nord-ouest",[False, True, True, False])
	addRoom((4,3), "salle des gardes",[True, False, False, True])
	addRoom((4,2), "tourelle nord",[False, True, True, False])
	addRoom((5,2), "eglise",[True, False, False, True])
	addRoom((5,1), "cimetière",[False, True, False, False])

	"""addItem("vin blanc","vin_blanc.png","cuisine")
	addItem("poisson","poisson.png","cuisine")
	addItem("viande","viande.png","cuisine")"""
	addItem("statue (moche)","statue.png","escalier majestueux", True)
	addItem("mannequin d'entraînement","mannequin.png","salle d'arme",True)
	"""addItem("arc","arc.png","salle d'arme")
	addItem("hache","hache.png","salle d'arme")
	addItem("epee","epee.png","salle d'arme")
	addItem("masse","masse.png","salle d'arme")"""
	addWeapon("arc","arc.png", "salle d'arme"	,[10,10,1.0,True])
	addWeapon("épée","epee.png", "salle d'arme",[30,15,1.0,False])
	addWeapon("hache","hache.png", "salle d'arme",[20,20,1.2,False])
	addWeapon("masse","masse.png", "salle d'arme",[0,50,1.5,False])
		
	addMonster("araignee","../img/araignee.png","cave", [50, 20, 8, 0.5, False,100])
	addMonster("araignee","../img/araignee.png","cave", [50, 20, 8, 0.5, False,100])
	addMonster("araignee","../img/araignee.png","cave", [50, 20, 8, 0.5, False,100])
	addMonster("araignee","../img/araignee.png","cave", [50, 20, 8, 0.5, False,100])		

	addUser("Iv","123",r)
	addUser("V","VVV",r)
	addUser("Atrus","gp",r)
