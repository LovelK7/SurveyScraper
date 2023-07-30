SurveyScraper
Verzija 1.0 (srpanj 2023)
Autor Lovel Kukuljan
*****************************************************************************************************

SurveyScraper je jednostavan program, koji ubrzava i olakšava obradu podataka mjernih vlakova. 
Program učitava kreirane tablice mjernih vlakova iz TopoDroida ili PockeTopoa, filtrira samo 
glavne vlakove te ih pohranjuje u novu csv datoteku. Tada je moguće lako kopirati te podatke u 
Speleolite za izračun dimenzija speleološkog objekta.

*************************************	UPUTE ZA KORIŠTENJE	*************************************
1. Odaberi program koji si koristio za crtanje i iz kojeg si kreirao datoteku vlakova
2. Otvori datoteku s vlakovima - .csv datoteka za TopoDroid / .txt datoteka za PocketTopo
3. Definiraj predznak točaka (opcijonalno)
	Npr. prema autoru nacrta (Marko Markić - "mm") ili imenu objekta (Markotova špilja - "mš")
	Tada će za prvi slučaj točke dobiti sljedeći predznak:
	mm-0	mm-1
	mm-1	mm-2
	...
	ili
	mm-1.0	mm-1.1
	mm-1.1	mm-1.2
	...
4. Generiraj csv - Odaberi mjesto za pohranu csv datoteke koja će automatski dobiti sufiks "glavni_vlakovi"

*****************************************************************************************************
Za sve komentare ili prijedloge poboljšanja, slobodno me kontaktiraj na lkukuljan7 (at) gmail.com		
	