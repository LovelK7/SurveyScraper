
SurveyScraper

*****************************************************************************************************

Verzija 2.2 (rujan 2023)
Autor: Lovel Kukuljan

**************************************	ŠTO JE SURVEYSCRAPER?	**************************************

SurveyScraper je jednostavan program koji pojednostavljuje obradu podataka mjernih vlakova. 
Program učitava kreirane tablice mjernih vlakova iz TopoDroid-a ili PocketTopo-a, filtrira samo 
glavne vlakove te ih pohranjuje u novu csv datoteku. Tada je moguće lako kopirati te podatke u 
Speleolite za izračun dimenzija speleološkog objekta. Dodatna funkcionalnost je uračunavanje 
magnetske deklinacije odnosno korekcije azimuta vlakova, a prema odabranoj lokaciji, modelu i datumu.

*************************************	UPUTE ZA KORIŠTENJE	*************************************

1. Odaberi program koji si koristio za crtanje i iz kojeg si kreirao datoteku vlakova (TopoDroid ili PocketTopo)

2. Otvori datoteku s vlakovima - .csv datoteka za TopoDroid / .txt datoteka za PocketTopo

3. Definiraj predznak točaka (opcijski)
	Npr. prema autoru nacrta (Marko Markić - "mm") ili imenu objekta (Markotova špilja - "mš")
	Tada će za prvi slučaj točke dobiti sljedeći predznak:
	mm-0	mm-1
	mm-1	mm-2
	...
	ili
	mm-1.0	mm-1.1
	mm-1.1	mm-1.2
	...

4. Uračunaj magnetsku deklinaciju (opcijski). Otvara se zaseban prozor za računanje.
	4.1 Upiši lokaciju speleološkog objekta (npr. najbliže mjesto ili grad, mjesto, ulica)
	4.2 Dohvati koordinate. Tražilica će locirati upisano mjesto te upisati koordinate u sljedeća dva polja
	(geografska širina i geografska dužina). Pronađena lokacija biti će prikazana na umanjenom zemljovidu.
	4.3 Koordinate je moguće upisati i samostalno (WGS84, decimalni zapis s točkom npr. 45.123 i 14.123)
	4.4 Odaberi željeni model za računanje magnetske deklinacije (default je WMM)
	4.5 Odaberi datum odnosno dan, mjesec i godinu mjerenja
	4.6 Izračunaj. Ukoliko je sve pravilno upisano, generirati će se magnetska deklinacija na tri decimalna mjesta.
	4.7 Izračunaj. Prozor će se zatvoriti, a izračunana magnetske deklinacije će biti zapamćena te prikazana
	na glavnom prozoru.

5. Generiraj CSV - Odaberi mjesto za pohranu CSV datoteke koja će automatski dobiti sufiks "glavni_vlakovi". 
	Ukoliko je definirana magnetska deklinacija, tada će biti uračunata, ukoliko nije, biti će 0.
	5.1 Ispisati će se poruka da li je postupak uspješan ili ne
	5.2 Pojaviti će se mogućnost otvaranja generirane CSV datoteke

****************************************	PROMJENA JEZIKA		****************************************

Jezik programa se mijenja postavkom na vrhu glavnog prozora. Primjena novog jezika moguća je jedino ponovnim 
otvaranjem programa.

*****************************************************************************************************************

Za sve komentare ili prijedloge poboljšanja, slobodno me kontaktiraj na lkukuljan7 (at) gmail.com		
	
