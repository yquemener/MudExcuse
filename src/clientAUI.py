# -*- coding: utf-8 -*-

import wx
import wx.html
import wx.aui

import socket
from threading import *
import cPickle
import hashlib

import glcomponent

ID_Connect = wx.NewId()
ID_Desc = wx.NewId()
ID_LOGIN_Username = wx.NewId()
ID_LOGIN_Password = wx.NewId()

HOST = 'localhost'    # The remote host
PORTCOMMAND = 50008              # The same port as used by the server
PORTLISTEN = 50007              # The same port as used by the server

SHA = None				# Will be filled with the username+password hash as soon as connection occurs
#----------------------------------------------------------------------
def listeningThread(app, user):
	global HOST,PORTLISTEN,SHA
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((HOST, PORTLISTEN))
	print "send",SHA
	s.send(cPickle.dumps((user,SHA)))
	print "wait"
	data =s.recv(1024)
	print "rec",data
	if data!="OK":
		return
	while 1:
		print "receiving"
		data = s.recv(1024)
		if not data:break
		try:
			print cPickle.loads(data)
			app.appendNetworkData(cPickle.loads(data))
		except Exception(e):
			print e
			pass
	s.close()

#----------------------------------------------------------------------

class LoginDialog(wx.Dialog):
	def __init__(
			self, parent, ID, size=wx.DefaultSize, pos=wx.DefaultPosition, 
			style=wx.DEFAULT_DIALOG_STYLE,
			useMetal=False,
			):

		wx.Dialog.__init__(self, parent, ID, "Connexion", pos, size, style)

		self.parent = parent
		sizer = wx.BoxSizer(wx.VERTICAL)
		box = wx.BoxSizer(wx.HORIZONTAL)

		label = wx.StaticText(self, -1, "Nom d'utilisateur :")
		box.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)

		self.UserName = wx.TextCtrl(self, -1, "V", size=(80,-1))
		box.Add(self.UserName, 1, wx.ALIGN_CENTRE|wx.ALL, 5)

		sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

		box = wx.BoxSizer(wx.HORIZONTAL)
		label = wx.StaticText(self, -1, "Mot de passe :")
		box.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
		self.Password = wx.TextCtrl(self, -1, "VVV", size=(80,-1), style=wx.TE_PASSWORD)
		box.Add(self.Password, 1, wx.ALIGN_CENTRE|wx.ALL, 5)

		sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

		btnsizer = wx.StdDialogButtonSizer()


		OkBtn = wx.Button(self, wx.ID_OK)
		OkBtn.SetDefault()
		btnsizer.AddButton(OkBtn)

		btn = wx.Button(self, wx.ID_CANCEL)
		btnsizer.AddButton(btn)
		btnsizer.Realize()

		sizer.Add(btnsizer, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

		self.SetSizer(sizer)
		sizer.Fit(self)


#----------------------------------------------------------------------

class HTMLControl(wx.html.HtmlWindow):
    def __init__(self, parent, id):
        wx.html.HtmlWindow.__init__(self, parent, id, wx.DefaultPosition, wx.Size(400, 300), style=wx.NO_FULL_REPAINT_ON_RESIZE)
        if "gtk2" in wx.PlatformInfo:
            self.SetStandardFonts()

    def OnLinkClicked(self, linkinfo):
		print 'OnLinkClicked: %s\n' % linkinfo.GetHref()
		global HOST, PORTCOMMAND,SHA
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((HOST, PORTCOMMAND))
		s.send(cPickle.dumps((SHA, 'go',linkinfo.GetHref().lstrip('#'))))
		data = s.recv(1024)
		s.close()
		print "gone"
	

#----------------------------------------------------------------------


class PyAUIFrame(wx.Frame):
	
	def __init__(self, parent, id=-1, title="", pos=wx.DefaultPosition,
				 size=wx.DefaultSize, style=wx.DEFAULT_FRAME_STYLE |
											wx.SUNKEN_BORDER |
											wx.CLIP_CHILDREN):

		wx.Frame.__init__(self, parent, id, title, pos, size, style)
		
		# tell FrameManager to manage this frame		
		self._mgr = wx.aui.AuiManager()
		self._mgr.SetManagedWindow(self)
		
		self._perspectives = []
		self.n = 0
		self.x = 0
		
		self.networkData = []

		self.statusbar = self.CreateStatusBar(2, wx.ST_SIZEGRIP)
		self.statusbar.SetStatusWidths([-2, -3])
		self.statusbar.SetStatusText("Beuar !", 0)
		self.statusbar.SetStatusText("Beuar ici aussi !", 1)

		self.SetMinSize(wx.Size(400, 300))

		tb2 = wx.ToolBar(self, -1, wx.DefaultPosition, wx.DefaultSize,
						 wx.TB_FLAT | wx.TB_NODIVIDER| wx.TB_HORZ_TEXT)
		tb2.SetToolBitmapSize(wx.Size(16,16))
		tb2_bmp1 = wx.ArtProvider_GetBitmap(wx.ART_QUESTION, wx.ART_OTHER, wx.Size(16, 16))
		tb2.AddLabelTool(ID_Connect, " Connect", wx.ArtProvider_GetBitmap(wx.ART_EXECUTABLE_FILE))
		tb2.AddLabelTool(ID_Desc, "Desc", wx.ArtProvider_GetBitmap(wx.ART_INFORMATION))
		tb2.AddLabelTool(101, "Test", wx.ArtProvider_GetBitmap(wx.ART_WARNING))
		tb2.AddLabelTool(101, "Test", wx.ArtProvider_GetBitmap(wx.ART_MISSING_IMAGE))
		tb2.AddSeparator()
		tb2.AddLabelTool(101, "Test", tb2_bmp1)
		tb2.AddLabelTool(101, "Test", tb2_bmp1)
		tb2.Realize()
	   
		# add a bunch of panes
		self._mgr.AddPane(self.CreateTreeCtrl(), wx.aui.AuiPaneInfo().
						  Name("test8").Caption("Tree Pane").
						  Left().Layer(1).Position(1).CloseButton(True).MaximizeButton(True))
					  
		self.txtControl = self.CreateTextCtrl()
		
		self._mgr.AddPane(self.txtControl, wx.aui.AuiPaneInfo().
						  Name("test10").Caption("Text Pane").
						  Bottom().Layer(1).Position(1).CloseButton(True).MaximizeButton(True))
									  
		"""self._mgr.AddPane(self.CreateTextCtrl(), wx.aui.AuiPaneInfo().
						  Name("test11").Caption("Log Pane").
						  Bottom().Layer(1).Position(1).CloseButton(True).MaximizeButton(True))"""
									  

		# create some center panes

		self._mgr.AddPane(self.CreateHTMLCtrl(), wx.aui.AuiPaneInfo().Name("html_content").
						  CenterPane())
								
		# add the toolbars to the manager
						
		self._mgr.AddPane(tb2, wx.aui.AuiPaneInfo().
						  Name("tb2").Caption("Toolbar 2").
						  ToolbarPane().Top().Row(1).
						  LeftDockable(False).RightDockable(False))


		# "commit" all changes made to FrameManager   
		self._mgr.Update()

		#self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
		#self.Bind(wx.EVT_SIZE, self.OnSize)
		#self.Bind(wx.EVT_CLOSE, self.OnClose)

		# Show How To Use The Closing Panes Event
		#self.Bind(wx.aui.EVT_AUI_PANE_CLOSE, self.OnPaneClose)
		
		self.Bind(wx.EVT_MENU, self.OnExit, id=wx.ID_EXIT)
		self.Bind(wx.EVT_MENU, self.OnConnect, id=ID_Connect)
		self.Bind(wx.EVT_MENU, self.OnDesc, id=ID_Desc)

		#self.Bind(wx.EVT_IDLE, self.OnIdle)

	def appendNetworkData(self, data):
		self.networkData.append(data)
		self.processNetworkEventsQueue()
		print "appended"
		
	def OnPaneClose(self, event):

		caption = event.GetPane().caption

		if caption in ["Tree Pane", "Dock Manager Settings", "Fixed Pane"]:
			msg = "Are You Sure You Want To Close This Pane?"
			dlg = wx.MessageDialog(self, msg, "AUI Question",
								   wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)

			if dlg.ShowModal() in [wx.ID_NO, wx.ID_CANCEL]:
				event.Veto()
			dlg.Destroy()
		

	def OnClose(self, event):
		self._mgr.UnInit()
		del self._mgr
		self.Destroy()


	def OnExit(self, event):
		self.Close()


	def GetDockArt(self):
		return self._mgr.GetArtProvider()


	def DoUpdate(self):
		self._mgr.Update()


	def OnEraseBackground(self, event):
		event.Skip()


	def OnSize(self, event):
		event.Skip()

	def processNetworkEventsQueue(self):
		while len(self.networkData)>0:
			line = self.networkData.pop(0)
			print line
			if line[0]=='say':
				self.txtLog.AppendText("\n"+str(line[1]))
				self.Refresh()
			elif line[0]=='desc':
				s="<html><body><h3>"
				s+=line[1]
				s+="</h3>"
				for e in line[2]:
					s+="<br><a href='#"+str(e[0])+"'>"+e[1]+"</a> mène à "+e[2]
				s+="<br><br>Sont présents:"
				for e in line[3]:
					s+=e+"<br>"
				s+="</body></html>"
				
				self.mainText.SetPage(s)
				self.Refresh()
				print '__'
			else:
				print 'Unknown network event dumped :',line

	def OnConnect(self, event):
		global SHA
		frame = LoginDialog(self, wx.ID_ANY)
		if frame.ShowModal() == wx.ID_OK:
			SHA = hashlib.sha1(frame.UserName.GetValue()+"@"+frame.Password.GetValue()).hexdigest()
			self.ConnectToServer(frame.UserName.GetValue())

		
	def ConnectToServer(self, username):
		self.statusbar.SetStatusText("Connection en cours" , 1)
		t=Thread(target=listeningThread, args=(self,username))
		t.daemon=True
		t.start()
		

	def OnDesc(self, event):
		global HOST, PORTCOMMAND, SHA
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((HOST, PORTCOMMAND))
		s.send(cPickle.dumps((SHA, 'desc',"")))
		data = s.recv(1024)
		s.close()

	def OnIdle(self, event):
		#print "Idle", len(self.networkData), self.networkData[-1]
		pass
		
	def OnSend(self, event):
		global HOST, PORTCOMMAND, SHA
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((HOST, PORTCOMMAND))
		s.send(cPickle.dumps((SHA, 'say',self.ctrlEdit.GetValue())))
		data = s.recv(1024)
		s.close()
		self.ctrlEdit.Clear()
	
	
	def CreateTextCtrl(self):
		text = ("This is text box %d")%(self.n + 1)
		panel = wx.Panel(self,-1)
		sizer = wx.BoxSizer(wx.VERTICAL)

		self.txtLog = wx.TextCtrl(panel,-1, text, wx.Point(0, 0), wx.Size(-1, -1),
						   wx.NO_BORDER | wx.TE_MULTILINE)
		self.txtLog.SetEditable(False)
		sizer.Add(self.txtLog,10,wx.TOP|wx.EXPAND,1,0)
		
		self.ctrlEdit = wx.TextCtrl(panel,-1, text, wx.Point(0, 0), wx.Size(-1, -1),
						   wx.NO_BORDER| wx.TE_PROCESS_ENTER)
		self.ctrlEdit.SetEditable(True)
		sizer.Add(self.ctrlEdit,0,wx.BOTTOM|wx.EXPAND,0,0)
		self.ctrlEdit.Bind(wx.EVT_TEXT_ENTER, self.OnSend)

		panel.SetSizer(sizer)
		print sizer.GetSize()
		panel.Fit()
		print sizer.GetSize()		
		return panel


	def CreateTreeCtrl(self):
		tree = wx.TreeCtrl(self, -1, wx.Point(0, 0), wx.Size(160, 250),
						   wx.TR_DEFAULT_STYLE | wx.NO_BORDER)
		
		root = tree.AddRoot("AUI Project")
		items = []

		imglist = wx.ImageList(16, 16, True, 2)
		imglist.Add(wx.ArtProvider_GetBitmap(wx.ART_FOLDER, wx.ART_OTHER, wx.Size(16,16)))
		imglist.Add(wx.ArtProvider_GetBitmap(wx.ART_NORMAL_FILE, wx.ART_OTHER, wx.Size(16,16)))
		tree.AssignImageList(imglist)

		items.append(tree.AppendItem(root, "Users", 0))
		items.append(tree.AppendItem(root, "Items", 0))
		items.append(tree.AppendItem(root, "Exits", 0))

		for ii in xrange(len(items)):
		
			id = items[ii]
			tree.AppendItem(id, "Subitem 1", 1)
			tree.AppendItem(id, "Subitem 2", 1)
			tree.AppendItem(id, "Subitem 3", 1)
			tree.AppendItem(id, "Subitem 4", 1)
			tree.AppendItem(id, "Subitem 5", 1)
		
		tree.Expand(root)

		return tree


	def OnLinkClicked(a, linkinfo):
		print linkinfo

	def CreateHTMLCtrl(self):
		global overview
		self.mainText = HTMLControl(self, -1)
		#		wx.html.HtmlWindow(self, -1, wx.DefaultPosition, wx.Size(400, 300))
		self.mainText.SetPage(overview)		
		return self.mainText

	
	

#----------------------------------------------------------------------


overview = """\
<html><body>
<h3>wx.aui, the Advanced User Interface module</h3>

<br/><b>Overview</b><br/>

<p>wx.aui is an Advanced User Interface library for the wxWidgets toolkit 
that allows developers to create high-quality, cross-platform user 
interfaces quickly and easily.</p>

<p><b>Features</b></p>

<p>With wx.aui developers can create application frameworks with:</p>

<ul>
<li>Native, dockable floating frames</li>
<li>Perspective saving and loading</li>
<li>Native toolbars incorporating real-time, &quot;spring-loaded&quot; dragging</li>
<li>Customizable floating/docking behavior</li>
<li>Completely customizable look-and-feel</li>
<li>Optional transparent window effects (while dragging or docking)</li>
</ul>

</body></html>
"""




app = wx.PySimpleApp()
frame = PyAUIFrame(None, wx.ID_ANY, "Le Meude", size=(750, 590))
frame.Show()

app.MainLoop()
app.Destroy()
