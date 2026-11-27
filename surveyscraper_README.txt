SURVEYSCRAPER 4.1
Upute za korištenje · studeni 2026.


O PROGRAMU

SurveyScraper obrađuje mjerne vlakove iz programa TopoDroid, Qave i PocketTopo. Izdvaja glavne vlakove, ispravlja azimute za magnetsku deklinaciju, pomoću Speleoliti Online izračunava osnovne dimenzije objekta i izvozi tablicu vlakova u CSV datoteku. Time zamjenjuje ručnu obradu mjernih vlakova u Excelu.


PODRŽANE DATOTEKE

• TopoDroid (.csv) – uobičajeni izvoz i izvoz sirovih podataka (svako mjerenje u zasebnom redu). Format se prepoznaje automatski.
• PocketTopo (.txt)
• Qave (.srv)

Program se određuje automatski prema nastavku datoteke.


SUČELJE

• Speleoliti Online – otvara Speleoliti Online (https://www.speleo.net/speleoliti/online/app.html) u pregledniku Google Chrome.
• HR / EN – jezik sučelja.
• Main – uvoz, obrada i izvoz vlakova.
• MagDec – izračun magnetske deklinacije.
• Help – ove upute.


1. UVOZ VLAKOVA

U kartici Main pritisni „Otvori datoteku s vlakovima“ i odaberi datoteku. Program učitava vlakove, izdvaja glavne vlakove i pomoću Speleoliti Online izračunava poligonalnu duljinu, horizontalnu duljinu, visinsku razliku i dubinu. Ime objekta, ime izlazne datoteke i datum mjerenja popunjavaju se automatski kada su zapisani u datoteci.

Kod izvoza sirovih podataka iz TopoDroida:
• ponovljena mjerenja istog glavnog vlaka se usrednjavaju,
• pomoćni vlakovi (splays) se zadržavaju,
• obrisana (deleted) mjerenja i mjerenja označena kao overshoot se izostavljaju.

Ako neki vlak nedostaje, provjeri u TopoDroidu nije li obrisan.


2. PREDZNAK TOČAKA (opcionalno)

U polje „Predznak točaka“ upiši prefiks koji se dodaje nazivima točaka, npr. inicijale autora nacrta („mm-“) ili oznaku objekta („mš-“).

• TopoDroid i Qave: mm-0, mm-1, mm-2 …
• PocketTopo: mm-1.0, mm-1.1, mm-1.2 …
• Pomoćni vlakovi (TopoDroid) zadržavaju zvjezdicu na početku: *mm-0, *mm-1 …

Predznak se preporučuje: bez njega Excel nazive točaka čita kao brojeve i uklanja vodeće nule.


3. MAGNETSKA DEKLINACIJA (opcionalno)

Deklinaciju u decimalnim stupnjevima možeš upisati izravno u polje „Mag. deklinacija“ u kartici Main ili je izračunati u kartici MagDec:

1) Upiši lokaciju (mjesto, grad ili adresu, npr. „Zagreb, Ilica 1“) i pritisni „Dohvati koordinate“. Pronađena lokacija prikazuje se na karti, a koordinate se upisuju u polja ispod.

2) Koordinate možeš upisati i ručno. U izborniku „Koordinatni sustav“ odaberi:
   • WGS84 – geografska širina i dužina u decimalnim stupnjevima, npr. 45.8150 i 15.9819
   • HTRS96/TM – Sjever (N) i Istok (E) u metrima, npr. 5075146 i 459737

3) Odaberi model: WMM (2025.–2029.) ili IGRF (1900.–2029.). Ako je datum mjerenja izvan raspona WMM-a, program sam odabire IGRF.

4) Provjeri datum mjerenja. Ako je zapisan u datoteci, upisuje se automatski; inače je odabran današnji datum.

5) Pritisni „Izračunaj“. Deklinacija se dohvaća s NOAA Magnetic Field Calculators (https://www.ngdc.noaa.gov/geomag/calculators/magcalc.shtml), prikazuje na tri decimale i automatski upisuje u karticu Main.

Koordinatni sustavi:
• Decimalni zarez i razmaci su dopušteni (npr. 45,8150 ili 5 075 146).
• Pri promjeni sustava već upisane koordinate se preračunavaju u odabrani sustav.
• HTRS96/TM koordinate se prije izračuna preračunavaju u WGS84 unutar programa, bez interneta. Razlika između HTRS96 i WGS84 manja je od metra i ne utječe na deklinaciju.
• Ako su N i E zamijenjeni ili su upisani stupnjevi umjesto metara, program javlja grešku.


4. PODACI O OBJEKTU (opcionalno)

Na desnoj strani kartice Main možeš upisati ime objekta, koordinate ulaza (X, Y), nadmorsku visinu (Z), ime izlazne datoteke i fiksnu točku.

Kao fiksna točka automatski se postavlja najviša točka, pa je „Dubina od fiksne točke“ ujedno i dubina objekta. Promjena fiksne točke trenutno ne preračunava dubinu.


5. POHRANA POSTAVKI

Nakon unosa predznaka, deklinacije ili podataka o objektu pritisni „Pohrani postavke“ kako bi se primijenili.


6. IZVOZ U CSV

Pritisni „Izvezi u CSV“ i odaberi mjesto pohrane. Datoteka sadrži podatke o objektu i tablicu glavnih vlakova.

• „Dodaj stupac izvornih azimuta“ – uz ispravljene izvozi i izvorne azimute. Dostupno nakon što je deklinacija primijenjena gumbom „Pohrani postavke“.
• „Uključi pomoćne vlakove“ (samo TopoDroid) – izvozi i pomoćne vlakove. Isključeno je prema zadanim postavkama jer ih Speleoliti obrada ne podržava.


KONTAKT

Prijave grešaka, komentare i prijedloge pošalji na lkukuljan7 (at) gmail.com.
