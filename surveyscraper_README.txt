************************************************************************************

		    SurveyScraper - Verzija 3.0 (veljača 2024.)

************************************************************************************
************************     ŠTO JE SURVEYSCRAPER?      ****************************

SurveyScraper je program koji pojednostavljuje obradu podataka mjernih vlakova dobivenih iz najčešće korištenih programa za digitalno topografsko crtanje: TopoDroid, Qave i PocketTopo. Program u suštini zamjenjuje funkcionalnosti MS Excela za obradu mjernih vlakova te koristi funkcionalnosti Speleolita za izračun osnovnih dimenzija nacrta ili speleološkog objekta.

*************************     FUNKCIONALNOSTI       ********************************

-- Uvoz mjernih vlakova i automatsko filtriranje glavnih vlakova.
-- Dodavanje predznaka/prefiksa točkama koje se pohranjuju u csv datoteci.
-- Korekcija azimuta vlakova prema unesenoj ili izračunatoj magnetskoj deklinaciji.
-- Računanje magnetske deklinacije za odabranu lokaciju, model i datum.
-- Pohrana podataka i tablice mjernih vlakova u csv datoteku.
-- Mogućnost dodatnih funkcionalnosti otvaranjem Speleoliti Online

*************************      OPIS SUČELJA        *********************************

Program se sastoji od POČETNE TRAKE:
-- Speleoliti Online: otvaranje preglednika Google Chrome-a i stranice 		Speleoliti Online (https://www.speleo.net/speleoliti/online/app.html),
-- HR: odabir jezika (trenutno je dostupan jedino hrvatski jezik),
te TRI TABA:
-- Main: obrada mjernih vlakova,
-- MagDec: izračun magnetske deklinacije,
-- Help: otvaranje ovih uputa unutar programa.

*************************     UPUTE ZA KORIŠTENJE       ****************************

1. UVOZ 
-- U Main tab-u otvori datoteku s vlakovima: csv datoteku TopoDroid-a, srv	datoteku Qave-a ili txt datoteku PocketTopo-a.

2. Definiraj prefiks/predznak točaka (opcionalno) 
-- Npr. prema autoru nacrta (Marko Markić - "mm-") ili imenu objekta (Markićeva špilja - "mš-"). Tada će za slučajeve TopoDroid-a i Qave-a točke imati nazive:
	mm-0	mm-1
	mm-1	mm-2
	...
-- Odnosno za PocketTopo:
	mm-1.0	mm-1.1
	mm-1.1	mm-1.2
	...

3. Unesi magnetsku deklinaciju u decimalnim stupnjevima ili ju izračunaj automatski (opcionalno)
-- 3.1 Za izračun magnetske deklinacije pritisni tab MagDec
-- 3.2 Upiši lokaciju speleološkog objekta (npr. najbliže mjesto ili grad, mjesto, ulica)
-- 3.3 Dohvati koordinate. Tražilica će locirati upisano mjesto te upisati koordinate u sljedeća dva polja (geografska širina i geografska dužina). 		Pronađena lokacija biti će prikazana na umanjenom zemljovidu.
-- 3.4 Koordinate je moguće upisati i samostalno (WGS84, decimalni zapis s točkom npr. 45.12345 i 14.12345)
-- 3.5 Odaberi željeni model za računanje magnetske deklinacije (default: WMM)
-- 3.6 Odaberi datum odnosno dan, mjesec i godinu mjerenja (default: današnji datum)
-- 3.7 Izračunaj. Ukoliko je sve pravilno upisano, dohvatiti će se magnetska 		deklinacija na tri decimalna mjesta sa portala Magnetic Field Calculators (NOAA, https://www.ngdc.noaa.gov/geomag/calculators/magcalc.shtml). Nakon izračuna, magnetska deklinacija će biti automatski upisana u polje za magnetsku korekciju u Main tab-u.

4. Upiši dodatne podatke o speleološkom objektu (opcionalno)
-- Desni dio Main prozora omogućuje unos imena objekta, koordinate i nadmorske visine ulaza, definiranje imena izlazne datoteke te definiranje fiksne točke.
-- Prilikom obrade vlakova visinski najviša točka postaje određena kao fiksna, 		čime mjera "Dubina od fiksne točke" ujedno postaje i dubina objekta. 
(Trenutno, promjena fiksne točke neće automatski promjeniti i dubinu)

5. Pohrani postavke
-- Ukoliko je unesen predznak točaka, magnetska deklinacija i/ili ostali podaci 	o objektu, potrebno je pohraniti iste pritiskom na "Pohrani postavke".

6. IZVOZ
-- Pritiskom na "Izvezi u CSV" otvara se prozor za odabir mjesta za pohranu 		csv datoteke. Izlazna datoteka se sastoji od redova s podacima o objektu te 		tablice glavnih mjernih vlakova.
-- Opcija "Dodaj stupac izvornih azimuta" - Ukoliko je definirana magnetska 		deklinacija, moguće je aktivirati opciju izvoza stupca i originalnih azimuta.

*******************************     KONTAKT	 ***********************************

Za sve dojave bug-ova, komentare i prijedloge poboljšanja, slobodno me kontaktiraj na lkukuljan7 (at) gmail.com.		

************************************************************************************
