try:
	import wx
	from wx import glcanvas
	import random
	
except ImportError:
	raise ImportError, "Required dependency wx.glcanvas not present"

try:
	from OpenGL.GL import *
except ImportError:
	raise ImportError, "Required dependency OpenGL not present"

class GLComponent(glcanvas.GLCanvas):
	def __init__(self, parent, 
						attribList = (glcanvas.WX_GL_RGBA, glcanvas.WX_GL_DOUBLEBUFFER, glcanvas.WX_GL_DEPTH_SIZE, 24)):
		
		super(GLComponent, self).__init__(parent, attribList)

		self.Bind(wx.EVT_PAINT, self.OnCanvasDraw)
		self.Bind(wx.EVT_IDLE, self.OnCanvasIdle)
		self.InitGL()

	def InitGL(self):
		size = self.canvas.GetClientSize()
		glViewport(0, 0, size.width, size.height)
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		glOrtho(-0.5, 0.5, -0.5, 0.5, -1, 1)
		glMatrixMode(GL_MODELVIEW)
		glLoadIdentity()
		glClearColor(1, 1, 1, 1)

	def OnCanvasDraw(self, event):
		self.canvas.SetCurrent()
		glClearColor(1, 1, 1, 1)
		glClear(GL_COLOR_BUFFER_BIT)

		for i in range(25):
			glLoadIdentity()
			glTranslate(random.randint(-100,100)/100.0, random.randint(-100,100)/100.0,0)
			glRotate(random.randint(0,360),0,0,1)
			glBegin(GL_TRIANGLES)
			glColor(0, 0, 0)
			glVertex(-.15, -.15)
			glVertex(.15, -.15)
			glVertex(0, .15)
			glEnd()

		self.canvas.SwapBuffers()
		wx.IdleEvent().RequestMore()
	
	def OnCanvasIdle(self, event):
		self.Refresh()

