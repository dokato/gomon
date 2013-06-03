#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
from socket import *
import numpy as np
from PyQt4 import QtGui, QtCore
from ast import literal_eval

class Gra(QtGui.QMainWindow):
	def __init__(self):
		super(Gra, self).__init__()
		#inicjalizacja podsatwowych stalych
		self._prz=50
		self._x0=10
		self._y0=40
		wym=12
		self.stan=StatusGry()

		self.resetuj(wym)
		
		self.wo=WysOdb()#uruchomienie serwera
		
		self.ONLINE_ST= False#czy gra ma sie toczyc online czy nie
		
		self.plansza(wym)
		self.statusBar()
		self.gorne_menu()
		
		self.setGeometry(50, 50, 700, 700)
		self.setWindowTitle('GoMoKu by DoKaTo')
		self.show()
	
	def resetuj(self,wym=12):
		self.znak=1 # 0 kolko, 1 krzyzyk, 2 puste
		
		self.licznikruchu=1		
		#wyglad planszy:
		self.ls=self.stan.begin(wym)

	def reset_planszy(self):
		self.resetuj()
		for i in range(len(self.przyc)):
			self.przyc[i].setText(' ')
		self.blokada(True)
		
	def gorne_menu(self):
		menubar = self.menuBar()
		
		exitAct = QtGui.QAction('&Zamknij', self)        
		exitAct.setShortcut('Ctrl+Q')
		exitAct.setStatusTip('Zamyka aplikacje')
		exitAct.triggered.connect(QtGui.qApp.quit)
		
		startAct = QtGui.QAction('&Nowa Gra', self)        
		startAct.setShortcut('Ctrl+N')
		startAct.setStatusTip('Rozpoczyna nowa  gre')
		startAct.triggered.connect(self.reset_planszy)
		
		helpAct = QtGui.QAction('&Pomoc', self)        
		helpAct.setShortcut('Ctrl+H')
		helpAct.setStatusTip('Wyswietla informacje')
		helpAct.triggered.connect(self.maly_help)
		
		fileMenu = menubar.addMenu('&Menu')
		fileMenu.addAction(startAct)
		fileMenu.addAction(exitAct)
		
		fileMenu2 = menubar.addMenu('&Info')
		fileMenu2.addAction(helpAct)

	def maly_help(self):
		msg = 'To moja wiadomosc \n jestem tworca tego programu \nDK'
		QtGui.QMessageBox.about(self, "O Gomoku", msg.strip())

	def plansza(self,n):
		self.czyjruch()

		self.przyc=[]
		for i in range(n):
			for j in range(n):
				self.przyc.append(QtGui.QPushButton(" ", self))
				self.przyc[-1].move(self._x0+j*self._prz,self._y0+i*self._prz)
				self.przyc[-1].resize(40,40)
				self.przyc[-1].clicked.connect(self.klik)
				self.przyc[-1].pozycja=(i,j)

	def klik(self):
		sender = self.sender()
		print self.licznikruchu
		zl,zr=sender.pozycja
		if self.ONLINE_ST==True:
			if self.licznikruchu%2==0:
				self.wstaw(zl,zr,sender)
			else:
				self.wo.przekaz(str((zl,zr)))
		else:
			self.wstaw(zl,zr,sender)


	def wstaw(self,a1,a2,ob):
		if self.ls[a1][a2]==2:
			self.licznikruchu+=1
			if self.znak==0:
				ob.setText('X')
			else:
				ob.setText('O')
			
			self.ls[a1][a2]=self.znak

			self.znak=self.licznikruchu%2
			self.czyjruch()
		
		if self.stan.checkit(self.ls)==False:
			self.koniec()

	def koniec(self):
		if self.znak==1:
			self.statusBar().showMessage('Wygral krzyzyk')
		if self.znak==0:
			self.statusBar().showMessage('Wygralo kolko')
		self.blokada()

	def blokada(self,czy=False):
		for i in range(len(self.przyc)):
			self.przyc[i].setEnabled(czy)

	def czyjruch(self):
		if self.znak==1:
			self.statusBar().showMessage('Ruch kolka')
		if self.znak==0:
			self.statusBar().showMessage('Ruch krzyzyka')

class WysOdb(object):
	def __init__(self,port_srv=7788,port_kl=6689,host='localhost'):
		self.s = socket(AF_INET, SOCK_STREAM)
		self.port_srv,self.port_kl=port_srv,port_kl
		self.host=host
		fl=1
		while fl:
			try: self.s.bind((self.host, self.port_srv))
			except:
				self.port_srv+=1
				continue
			fl=0
		self.s.listen(2)

	def przekaz(self,pozycja):
		b=socket(AF_INET, SOCK_STREAM)
		fl=1
		while fl:
			try: b.connect((self.host, self.port_kl))
			except:
				self.port_kl+=1
				continue
			fl=0
		b.send(pozycja)
		poprawnosc = b.recv(1024)
		if poprawnosc=='ok':
			return True

	def odbierz(self):
		client,addr = self.s.accept()
		data = client.recv(1024)
		client.send('ok')
		client.close()
		return data

class StatusGry():
	def begin(self, n):
		x=np.ones((n,n))*2
		return x
		
	def sprawdzliste(self,lst):
		if len(lst)==5:
			if np.sum(lst==0)==5:
				return False
			if np.sum(lst==1)==5:
				return False
		return True

	def checkit(self,plansza):
		lim=5 # ile razem aby wygrac
		# wiersze
		for	row in plansza:
			for i in xrange(len(row)):
				if self.sprawdzliste(row[i:i+lim])==0:
					return False
		#kolumny
		for	row in plansza.T:
			for i in xrange(len(row)):
				if self.sprawdzliste(row[i:i+lim])==0:
					return False
		#przekatne
		for b in range(plansza.shape[0]):
			for i in range(len(plansza[0])):
				tab=plansza[b:b+lim, i:i+lim]
				if tab.shape==(lim,lim):
					if self.sprawdzliste(tab.diagonal())==0:
						return False
					if self.sprawdzliste(tab[:,::-1].diagonal())==0:
						return False
		return True


def main():
	app = QtGui.QApplication(sys.argv)
	gra=Gra()
	sys.exit(app.exec_())

if __name__ == '__main__':
	main()
