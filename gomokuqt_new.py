#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = 'Dominik Krzeminski'
__version__ = '0.82'
__date__ = '29-05-2013'
__license__ = 'GPL'

import sys
from socket import *
import numpy as np
from PyQt4 import QtGui, QtCore
from ast import literal_eval

class Gra(QtGui.QMainWindow):
	def __init__(self):
		super(Gra, self).__init__()
		#inicjalizacja podsatwowych stalych
		self._prz=45 #wymiary buttona
		self._x0=10 # poczotkowe pozycje
		self._y0=40
		self.wym=12 # wymiar planszy
		self.stan=StatusGry() #klasa sprawdzajaca czy rozgrywka jest juz skonczona
		self.komp=SAI() # prosta sztuczna inteligencja - wybory komputera
		
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
		'''resetuje plansze zmienia status gry online i z komputerem
		na falsz, zmienia licznik ruchu na 1, jezeli problem z wymiarem
		to blokuje przyciski'''
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
		'czysci przyciski na puste'
		self.resetuj()
		for i in range(len(self.przyc)):
			self.przyc[i].setText(' ')
		self.blokada(True)
	
	def rob_menu(self,nazwa, skrot, stTip, akcja):
		r=QtGui.QAction(nazwa,self)
		if skrot: r.setShortcut(skrot)
		if stTip: r.setStatusTip(stTip)
		r.triggered.connect(akcja)
		return r
	def gorne_menu(self):
		'obsluguje wszystkie akcje z gornego menu'
		menubar = self.menuBar()
		
		exitAct = self.rob_menu("&Zamknij",'Ctrl+Q','Zamyka aplikacje',QtGui.qApp.quit)
		startAct = self.rob_menu('&Nowa Gra','Ctrl+N','Rozpoczyna nowa  gre',self.reset_planszy)
		on1Act=self.rob_menu('&Gra online -1szy gracz',None,'Rozpoczyna nowa  gre online jako numer 1',self.startgracz1)
		on2Act=self.rob_menu('&Gra online -2gi gracz',None,'Rozpoczyna nowa  gre online jako numer 2',self.startgracz2)
		aiAct = self.rob_menu('&Gra z komputerem', None,'Rozpoczyna nowa  gre z wirtualnym przeciwnikiem',self.start_z_komp)
		helpAct = self.rob_menu('&Pomoc', 'Ctrl+H','Wyswietla informacje',self.maly_help)
		
		fileMenu = menubar.addMenu('&Menu')
		fileMenu.addAction(startAct)
		fileMenu.addAction(on1Act)
		fileMenu.addAction(on2Act)
		fileMenu.addAction(aiAct)
		fileMenu.addAction(exitAct)

		fileMenu2 = menubar.addMenu('&Opcje')
		#fileMenu2.addAction(rozmAct)

		fileMenu3 = menubar.addMenu('&Info')
		fileMenu3.addAction(helpAct)
		
	def maly_help(self):
		f=open('about.txt','r')
		msg=''
		for w in f: msg+=w
		QtGui.QMessageBox.about(self, "O Gomoku", msg.strip())

	def plansza(self,n):
		'''obsluguje stan poczatkowy planszy, rysuje przyciski i dodaje
		do nich mozliwosc klikniecia wraz z odpowiednia akcja'''
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
		'czyli co sie dzieje po kliknieciu - przechwytuje pozycje i wywoluje wstaw'
		sender = self.sender()
		self.bl=1 #blokada zapetlania wysylanego sygnalu
		zl,zr=sender.pozycja
		self.wstaw(zl,zr)
	
	def rysuj(self,plansza):
		'rysowanie planszy dostosowane do nowej sytuacji na niej'
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
		'''wstawianie nowego ruchu na plansze wraz z obsluga kilku zdarzen
		m.in. przypadkow wyboru online, badz wyboru gry z komputerem'''
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
		
		if self.ONLINE_ST==True and self.bl==1:
			self.wyslij_syg(a1,a2)
			self.bl=0

	###ONLINE
	def startgracz1(self):
		self.wys=Wysylacz()
		self.odb=Odbieracz()
		self.laczenie()

	def startgracz2(self):
		self.wys=Wysylacz(srv=40205,kl=40100)
		self.odb=Odbieracz(srv=40205,kl=40100)
		self.laczenie()
		self.bl=0
		self.odbierz_syg()
		
	def laczenie(self):
		'laczy akcje z watkami'
		self.ONLINE_ST= True
		#self.connect(self.wys, QtCore.SIGNAL("output(QString)"), self.wypisz_w)
		self.connect(self.odb, QtCore.SIGNAL("finished()"), self.odsw)
		self.connect(self.odb, QtCore.SIGNAL("terminated()"), self.odsw)
		self.connect(self.odb, QtCore.SIGNAL("output(QString)"), self.otrzymany)
		
	def wyslij_syg(self,z1,z2):
		'wysyla kliknieta pozycje'
		self.blokada(False)
		self.statusBar().showMessage('Wysylanie w toku...')
		self.wys.pracuj(str((z1,z2)))
		print 'koniec pracy wysylajacego'
		self.odbierz_syg()

	def odbierz_syg(self):
		'nasluchuje, a gdy obierze powinno wstawic i przejsc do wyslania'
		self.statusBar().showMessage('Czekam na polaczenie...')
		self.blokada(False)
		self.odb.pracuj()
		
	def otrzymany(self, poz):
		print poz, type(poz)
		o1,o2=literal_eval(str(poz))
		self.wstaw(o1,o2)
	###
	def start_z_komp(self):
		'rozpoczyna gre z AI, resetuje plansze i ustawia status AI'
		self.reset_planszy()
		self.AI=True

	def koniec(self):
		'info o wygranej na koncu z uzyciem status baru'
		if self.znak==1:
			self.statusBar().showMessage('Wygral krzyzyk')
		if self.znak==0:
			self.statusBar().showMessage('Wygralo kolko')
		self.blokada()
	
	def odsw(self):
		self.blokada(True)
	
	def blokada(self,czy=False):
		'wylacza przyciski'
		for i in range(len(self.przyc)):
			self.przyc[i].setEnabled(czy)

	def czyjruch(self):
		'info o kolejnosci ruchu'
		if self.znak==1:
			self.statusBar().showMessage('Ruch kolka')
		if self.znak==0:
			self.statusBar().showMessage('Ruch krzyzyka')
	
	def wczyt(self):
		import pickle
		sc = 'set.data'
		f2 = open(sc, 'rb')
		dd = pickle.load(f2)
		self.srv=dd[0]
		self.kl=dd[1]
		self.hostname=dd[2]
		
class StatusGry():
	'''begin - inicjalizuje plansze
	checkit przebiega po wierszach, kolumnach, przekatnych aby sprawdzicz czy nie
	ma liczby <<lim>> takich samych w danych rzucie. Jesli jest to zwraca False,
	gdy nie to oddaje True'''
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
	'''Bardzo proste AI. W zasadzie opiera sie o losowe ruchy. Tylko kiedy
	przeciwnik ma ustawione 3/4 w rzedzie to stawia znak dookola przeciwnika
	co moze zablokowac jego ruch.'''
	def __init__(self):
		self.sg=StatusGry()
		
	def simple_ai(self,plan):
		self.cala_plansza=plan
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
		else:
			fl=0
			nx,ny=x+b-1,y+a+1
			while fl==0:
				print nx,ny
				print plan
				if self.cala_plansza[nx][ny]==2:
					return nx,ny
				else:
					a=np.random.randint(0,2)
					if a==0: a-=1
					nx+=a*np.random.randint(0,2)
					ny+=a*np.random.randint(0,2)
					if nx>self.cala_plansza.shape[0]: nx-=self.cala_plansza.shape[0]
					if ny>self.cala_plansza.shape[0]: ny-=self.cala_plansza.shape[0]
					if nx<0: nx+=self.cala_plansza.shape[0]
					if ny<0: ny+=self.cala_plansza.shape[0]

	def zakanczacz(self,plan):
		lim=3
		for	e,row in enumerate(plan):
			for i in xrange(len(row)):
				if self.sg.sprawdzliste(row[i:i+lim],lim)==0:
					return self.stupid_ai(plan[e:e+lim,i:i+lim],e,i)
		for	e,row in enumerate(plan.T):
			for i in xrange(len(row)):
				if self.sg.sprawdzliste(row[i:i+lim],lim)==0:
					return self.stupid_ai(plan[i:i+lim,e:e+lim],e,i)
		for b in range(plan.shape[0]):
			for i in range(len(plan[0])):
				tab=plan[b:b+lim, i:i+lim]
				if tab.shape==(lim,lim):
					if self.sg.sprawdzliste(tab.diagonal(),lim)==0:
						return self.stupid_ai(tab,i,b)
					if self.sg.sprawdzliste(tab[:,::-1].diagonal(),lim)==0:
						return self.stupid_ai(tab,i,b)

class Wysylacz(QtCore.QThread):
	def __init__(self,parent=None,srv=40100,kl=40205):
		QtCore.QThread.__init__(self, parent)
		self.exiting = False
		self.port_srv=srv
		self.port_kl=kl
		self.host='localhost'
		

	def __del__(self):
		self.exiting = True
		self.wait()
        	
	def pracuj(self,a):
		self.a=a
		self.start()
		
	def run(self):
		self.b=socket(AF_INET, SOCK_STREAM)
		print 'start wysylania'
		fl=0
		self.b.connect((self.host, self.port_kl))
		if fl==0:
			print '++ polaczono', self.port_kl
			self.b.send(str(self.a))
			data = self.b.recv(1024)
			#if data=='jest ok':
				#self.b.close()
				#self.emit(QtCore.SIGNAL("output(QString)"),str(data)+'\n')

class Odbieracz(QtCore.QThread):
	def __init__(self,parent=None,srv=40100,kl=40205):
		QtCore.QThread.__init__(self, parent)
		self.exiting = False
		
		self.s = socket(AF_INET, SOCK_STREAM)
		self.port_srv=srv
		self.port_kl=kl
		self.host='localhost'
		self.s.bind((self.host, self.port_srv))
		print 'twoj host', self.host, 'port',self.port_srv
		self.s.listen(2)

	def __del__(self):
		self.exiting = True
		self.s.close()
		self.wait()

	def pracuj(self):
		self.start()
			
	def run(self):
		print 'start sluchania'
		client,addr = self.s.accept()
		data = client.recv(1024)
		print 'Polaczenie z ', addr
		print 'odebrano', data
		client.send('jest ok')
		client.close()
		self.emit(QtCore.SIGNAL("output(QString)"),str(data)+'\n')

def main():
	app = QtGui.QApplication(sys.argv)
	gra=Gra()
	sys.exit(app.exec_())

if __name__ == '__main__':
	main()
