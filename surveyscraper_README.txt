SurveyScraper
Verzija 2.0 (kolovoz 2023)
Autor: Lovel Kukuljan
*****************************************************************************************************

SurveyScraper je jednostavan program, koji pojednostavljuje obradu podataka mjernih vlakova. 
Program učitava kreirane tablice mjernih vlakova iz TopoDroid-a ili PocketTopo-a, filtrira samo 
glavne vlakove te ih pohranjuje u novu csv datoteku. Tada je moguće lako kopirati te podatke u 
Speleolite za izračun dimenzija speleološkog objekta. Dodatna funkcionalnost je uračunavanje 
magnetske deklinacije odnosno korekcije azimuta vlakova, a prema odabranoj lokaciji, modelu i datumu.

*************************************	UPUTE ZA KORIŠTENJE	*************************************
1. Odaberi program koji si koristio za crtanje i iz kojeg si kreirao datoteku vlakova
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
	4.3 Koordinate je moguće upisati i samostalno (WGS84, decimalni zapis npr. 45.123 i 14.123)
	4.4 Odaberi željeni model (default je WMM)
	4.5 Odaberi datum odnosno dan, mjesec i godinu mjerenja
	4.6 Izračunaj. 
	Ukoliko je sve pravilno upisano, generirati će se magnetska deklinacija na tri decimalna mjesta.

5. Generiraj CSV - Odaberi mjesto za pohranu CSV datoteke koja će automatski dobiti sufiks "glavni_vlakovi". 
	Ukoliko je definirana magnetska deklinacija, tada će biti uračunata, ukoliko nije, biti će 0.

*****************************************************************************************************
Za sve komentare ili prijedloge poboljšanja, slobodno me kontaktiraj na lkukuljan7 (at) gmail.com		
	
