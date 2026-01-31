Dateien in diesem Verzeichnis:

PSC.F 	Dieses programm löst eine generische Transportgleichung für
	eine skalare Größe in 2D. Es werden sowohl der konvektive als
	auch der diffusive Transport berücksichtigt, aber das 
	Geschwindigkeitsfeld muss vorgegeben werden. Im Programm wird
	das Geschwindigkeitsfeld einer Potentialströmung um einen 
	Staupunkt festgelegt (dies kann - z.B. als eine Übungsaufgabe -
	durch die Vorgabe einer anderen Potentialströmung geändert
 	werden). Das zu lösende Problem ist im Buch in Abschnitt 4.8
	beschrieben worden. Die Finite-Volumen-Methode wurde benutzt;
	man kann bei der Diskretisierung der konvektiven Flüsse 
	zwischen Aufwind- und Zentraldifferenzen wählen, während
	diffusive Flüsse mit Zentraldifferenzen approximiert wurden.
	Das Gitter wird ebenfalls in diesem Programm erzeugt; es kann
	nichtäquidistant sein, was durch einen Expansionsparameter
	kontrolliert werden kann. Drei Gleichungslöser stehen zur
	Verfügung: linienweise Anwendung des Thomas-Algorithmus
	(TDMA) in X- bzw. Y-Richtung und ILU-Löser nach Stone (SIP; 
	siehe Abschnitt 5.3.4). Eingabedaten können entweder während
	der Ausführung des Programmen nach Aufforderung eingegeben,
	oder aus einer Datei eingelesen werden.

	Die Übersetzung und die Ausführung des programms kann wie folgt
	durchgeführt werden (vorausgesetzt, der Compiler heißt "f77"):

	f77 psc.f -o psc
	psc < psc.inp
	

PSC.INP	Diese Datei beinhaltet die Eingabedaten für das obige Programm;
	die Daten wurden im Programm durch Kommentare beschrieben.


PSCUS.F	Dies ist eine für instationäre Vorgänge erweiterte Version des
 	Programmes PSC.F. Man kann zusätzlich die Methode zur
	Zeitintegration wählen: explizite Euler-Methode (EE), implizite
	Euler-Methode (IE), Crank-Nicolson Methode (CN) oder implizite
	Methode mit drei Zeitebenen (I3L). Das Programm wurde verwendet,
	um das instationäre 2D-Problem aus Abschnitt 6.4 zu lösen.


PSCUS.INP Die Eingabedaten für das Programm PSCUS.F.


pcompact.f  Eine Version des Programmes "psc.f", in der für die konvektiven
	Flüsse eine Interpolation 4. Ordnung für die Bestimmung der
	Variablenwerte in der Mitte der KV-Seite ebenfalls zur Verfügung 
        steht.

