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
		self._prz=45
		self._x0=10
		self._y0=40
		self.wym=12
		self.stan=StatusGry()
		self.komp=SAI()
		
		self.resetuj(self.wym)
		
		self.ONLINE_ST= False#czy gra ma sie toczyc online czy nie
		self.AI=False
		
		self.plansza(self.wym)
		self.statusBar()
		self.gorne_menu()
		
		self.setGeometry(50, 50, 600, 600)
		self.setWindowTitle('GoMoKu by DoKaTo')
		self.show()
	
	def resetuj(self,wym2=12):
		self.znak=1 # 1 kolko, 0 krzyzyk, 2 puste
		
		self.ONLINE_ST=False
		self.AI=False
		self.licznikruchu=1		
		#wyglad planszy:
		self.ls=self.stan.begin(wym2)
		if wym2 !=self.wym:
			for i in range(len(self.przyc)):
				self.przyc[i].setEnabled(False)

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

		on1Act = QtGui.QAction('&Gra online -1szy gracz', self)
		on1Act.setStatusTip('Rozpoczyna nowa  gre online jako numer 1')
		on1Act.triggered.connect(self.startgracz1)

		on2Act = QtGui.QAction('&Gra online -2gi gracz', self)
		on2Act.setStatusTip('Rozpoczyna nowa  gre online jako numer 2')
		on2Act.triggered.connect(self.startgracz2)

		aiAct = QtGui.QAction('&Gra z komputerem', self)
		aiAct.setStatusTip('Rozpoczyna nowa  gre z wirtualnym przeciwnikiem')
		aiAct.triggered.connect(self.start_z_komp)
	
		helpAct = QtGui.QAction('&Pomoc', self)        
		helpAct.setShortcut('Ctrl+H')
		helpAct.setStatusTip('Wyswietla informacje')
		helpAct.triggered.connect(self.maly_help)
		
		rozmAct = QtGui.QAction('&Rozmiar planszy', self)        
		rozmAct.setShortcut('Ctrl+R')
		rozmAct.setStatusTip('Pozwala wybrac rozmiar planszy')
		rozmAct.triggered.connect(self.wybor_rozm)
		
		fileMenu = menubar.addMenu('&Menu')
		fileMenu.addAction(startAct)
		fileMenu.addAction(on1Act)
		fileMenu.addAction(on2Act)
		fileMenu.addAction(aiAct)
		fileMenu.addAction(exitAct)

		fileMenu2 = menubar.addMenu('&Opcje')
		fileMenu2.addAction(rozmAct)

		fileMenu3 = menubar.addMenu('&Info')
		fileMenu3.addAction(helpAct)

	def wybor_rozm(self):
		items = {"8x8":8, "12x12":12, "15x15":15}

		item, ok = QtGui.QInputDialog.getItem(self, "Rozmiar",
			"Season:", items.keys(), 0, False)
		if ok and item:
			self.statusBar().showMessage('Wybrano rozmiar: ' +str(item))
			self.resetuj(items[str(item)])
			
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
		self.wstaw(zl,zr)
	
	def rysuj(self,plansza):
		l=0
		for i in xrange(plansza.shape[0]):
			for j in xrange(plansza.shape[0]):
				if plansza[i][j]==2:
					self.przyc[l].setText(' ')
				if plansza[i][j]==1:
					self.przyc[l].setText('O')
				if plansza[i][j]==0:
					self.przyc[l].setText('X')
				l+=1

	def wstaw(self,a1,a2):
		if self.ls[a1][a2]==2:
			self.licznikruchu+=1
			self.ls[a1][a2]=self.znak
			
			if self.AI==True:
				self.licznikruchu+=1
				
				sz1,sz2=self.komp.simple_ai(self.ls)
				
				self.znak-=1
				
				self.ls[sz1][sz2]=self.znak
				self.rysuj(self.ls)
				
			else:
				self.rysuj(self.ls)

			self.czyjruch()
		
		if self.stan.checkit(self.ls)==False:
			self.koniec()
		
		self.znak=self.licznikruchu%2
		
		if self.ONLINE_ST==True:
			self.wyslij_syg(a1,a2)
		#tutaj cos co blokuje gdy serw slucha i wstawia wyslane dane


	###ONLINE
	def startgracz1(self):
		self.reset_planszy()
		self.ONLINE_ST=True
		self.blokada(False)
		self.wo=WysOdb()#uruchomienie serwera
		self.statusBar().showMessage('Grasz jako pierwszy - czekaj na polaczenie')
		if self.wo.przekaz('start')==True:
			self.statusBar().showMessage('Start')
			self.blokada(True)

	def startgracz2(self):
		self.reset_planszy()
		self.blokada(False)
		self.ONLINE_ST=True
		self.wo=WysOdb(op=0)#uruchomienie serwera ze zmiana
		self.statusBar().showMessage('Grasz jako drugi - czekaj na polaczenie')
		if self.wo.odbierz()=='start':
			self.statusBar().showMessage('Polaczono poprawnie czekaj na ruch')
			self.odbierz_syg()

	def wyslij_syg(self,z1,z2):
		self.blokada(False)
		self.wo.przekaz(str((z1,z2)))
		self.odbierz_syg()
		self.blokada(True)

	def odbierz_syg(self):
		self.blokada(False)
		dostane=self.wo.odbierz()
		while dostane!='start':
			dostane=self.wo.odbierz()
			print dostane
			o1,o2=literal_eval(dostane)
			self.wstaw(o1,o2)
		self.blokada(True)
	###
	def start_z_komp(self):
		self.reset_planszy()
		self.AI=True

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
	def __init__(self,port_srv=41000,port_kl=42000,host='localhost',op=1):
		self.s = socket(AF_INET, SOCK_STREAM)

		if op:
			self.port_srv,self.port_kl=port_srv,port_kl
		else:
			self.port_srv,self.port_kl=port_kl,port_srv
			
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
				print self.port_kl, 
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
		
	def sprawdzliste(self,lst,lim):
		if len(lst)==lim:
			if np.sum(lst==0)==lim:
				return False
			if np.sum(lst==1)==lim:
				return False
		return True

	def checkit(self,plansza,lim=5):
		# lim = ile razem aby wygrac
		# wiersze
		for	row in plansza:
			for i in xrange(len(row)):
				if self.sprawdzliste(row[i:i+lim],lim)==0:
					return False
		#kolumny
		for	row in plansza.T:
			for i in xrange(len(row)):
				if self.sprawdzliste(row[i:i+lim],lim)==0:
					return False
		#przekatne
		for b in range(plansza.shape[0]):
			for i in range(len(plansza[0])):
				tab=plansza[b:b+lim, i:i+lim]
				if tab.shape==(lim,lim):
					if self.sprawdzliste(tab.diagonal(),lim)==0:
						return False
					if self.sprawdzliste(tab[:,::-1].diagonal(),lim)==0:
						return False
		return True

class SAI(object):
	def __init__(self):
		self.sg=StatusGry()
		
	def simple_ai(self,plan):
		if self.sg.checkit(plan,lim=4)==0:
			return self.zakanczacz(plan)
		else:
			return self.stupid_ai(plan)
			
	def stupid_ai(self, plan,x=None,y=None):
		fl=0
		while fl==0:
			a=np.random.randint(0,plan.shape[0])
			b=np.random.randint(0,plan.shape[0])
			if plan[a][b]==2:
				fl=1
		if x==None and y==None: return a,b
		else: return x+b-1,y+a+1
	
	def zakanczacz(self,plan):
		lim=4
		for	e,row in enumerate(plan):
			for i in xrange(len(row)):
				if self.sg.sprawdzliste(row[i:i+lim],lim)==0:
					return self.stupid_ai(plan[e:e+lim,i:i+lim],e,i)
		for	e,row in enumerate(plan.T):
			for i in xrange(len(row)):
				if self.sg.sprawdzliste(row[i:i+lim],lim)==0:
					return self.stupid_ai(plan[i:i+lim,e:e+lim],e,i)
		for b in range(plan.shape[0]):
			for i in range(len(plansza[0])):
				tab=plan[b:b+lim, i:i+lim]
				if tab.shape==(lim,lim):
					if self.sg.sprawdzliste(tab.diagonal(),lim)==0:
						return self.stupid_ai(tab,i,b)
					if self.sg.sprawdzliste(tab[:,::-1].diagonal(),lim)==0:
						return self.stupid_ai(tab,i,b)

def main():
	app = QtGui.QApplication(sys.argv)
	gra=Gra()
	sys.exit(app.exec_())

if __name__ == '__main__':
	main()
