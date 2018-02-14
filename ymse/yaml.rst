Konfigurering av LADiM
======================

Litt om YAML-formatet
---------------------

Akronymet YAML står for (YAML Ain't Markup Language). Hjemmesiden er yaml.org
og det er en god og ikke for lang beskrivelse på wikipedia. Formatet er valgt i
LADiM fordi i motsetning til XML og JSON så er formatet beregnet for å
leses/skrives av mennesker. Formatet er ganske vanlig for
konfigurasjonsfiler.

Innrykk er obligatorisk og angir strukturen. Filen skal ikke inneholde
tab-karakterer, men gode editorer erstatter automatisk tab med blanke.
Kommentarer begynner med skigard, ``#``. Det er ikke nødvendig med hermetegn
rundt tekststrenger.

Bruk i LADiM
------------

Default navn på konfigurasjonsfilen er ``ladim.yaml``, men navnet kan være hva
som helst. Bruk da ``ladim <navn på konfig-fil>`` fra kommandolinje.

Den definitive beskrivelsen av formatet er i leserutinen
``ladim/configuration.py``. Ekstra linjer blir stille oversett. Rekkefølge
spiller ingen rolle, bortsett fra at linjer må komme i den seksjonen de
tilhører.

Tidskontroll
------------

Seksjon heter ``time_control`` og har følgende obligatoriske felt::

  start_time
  stop_time
  reference_time

Tidspunkt angis i iso-format yyyy-mm-dd hh:mm:ss, hvor mindre signifikante ledd
i klokkeslett kan utelates. td 2018-01-30 09. En "T" mellom dato og klokkeslett
går greitt.

reference_time
  er tiden som brukes som referanse i output-filene, time for
  units "seconds since reference_time".

I eksemplene brukes $time0 foran start_time. Dette tillater gjenbruk av samme
tidspunkt som *time0 i reference_time.

KOMMENTAR
  Dette vil bli forenklet ved at reference_time blir optional med
  start_time som default. (Gamle måten skal fortsette å virke). For mer
  operasjonelle kjøringer, med output i flere filer anbefales det å være
  eksplisitt, f.eks. reference_time: 2000-01-01 00

Filer
-----

Seksjonen heter ``files`` og styrer filnavnene.

Obligatoriske felt er::

  grid_file
  input_file
  particle_release_file
  output_file

grid_file
  må inneholde ROMS felter som h, mask_rho, pm, pn, lon_rho og lat_rho.
  Videre trengs vertikal informasjon. Dette finnes ikke i en ROMS gridfil, men
  f.eks. i godt utstyrte history/average-filer. Alternativt kan vertikal
  informasjon gis i gridforce seksjonen.  Et tomt filnavn, "", tilsier at
  griddet er definert analytisk.

input_file
  er en eller flere filer med drivkrefter. Det vil si resultfil(er) fra en
  havmodellkjøring. For flere filer må leksikografisk og kronologisk rekkefølge
  falle sammen. Feltet for filnavn  inneholder da wildcards som '*' og '?'. Et
  tomt filnavn, "", tilsier analytiske drivkrefter.

particle_release_file
  inneholder tidspunkt, posisjon, m.m for partikkelslipp. Jeg har laget en vane
  med å ha et python-script make_release.py som lager denne utfra annen
  spesifikasjon.

output_file
  er navnet på output netcdf-fil fra simuleringen. Multi-fil output
  er i ferd med å fases inn. I disse situasjonen vil ``navn.nc`` gi filnavn
  ``navn_0000.nc``, ``navn_0001.nc``, ...

KOMMENTAR:
Greit å ha alle filnavnene samlet tidlig i YAML-filen. På den annen side er
dette nå litt ROMS-spesifikt. Kunne ha en gridforce-seksjon hvor filnavn var en
del av spesifikasjonen av griddet og drivkreftene. Ulike modeller kan ha ulike
krav om hva som skal spesifiseres. Dette må tenkes på litt nærmere.

state
-----

Her spesifiseres hvilke variable som skal brukes utover pid, X, Y, Z som alltid
er med. Har også optionalt felt ibm_variables som brukes av en eventuell IBM.

KOMMENTAR:
Bedre å ha underseksjon, eller egen seksjon, IBM. Den kan sendes i sin helhet
til en IBM-modul. Det gjør at ulike IBM-er selv kan bestemme hvilken
informasjon som trengs fra konfigurasjonsfilen. Alternativ: Kan ha en egen IBM
konfigurasjonsfil. Foretrekker å ha alt i en fil, slik at simuleringen er
enklere dokumentert.

particle_release
----------------

I denne seksjonen spesifiseres partikkelslipp.

Felter::

  release_type:  optional, default = discrete
  release_frequency:  optional når discrete
  variables:   obligatorisk
  converters:  null eller flere
  particle_variables:  obligatorisk

release_type er continuous eller discrete. Ved discrete tolkes filen
bokstavelig, hver linje gir en utslippshendelse. Ved continuous så kan hver
linje gi flere utslipp til den overstyres av nye linjer ved seinere tidspunkt.
Default = discrete.

release_frequency styrer hvor ofte det skjer utslipp ved continuous utslipp.
Feltet neglisjeres hvis discrete utslipp. Må gis som en liste [verdi, enhet].
F.eks. hver time kan gis som [1, h] eller [3600, s].

variables er en liste over variablene i release-filen. Rekkefølgen er viktig.

converters brukes til å tolke variablene. Uten konverter blir den tolket som
float. Mulige verdier er int for heltall, str for tekststreng, time for tid.
Eksempler: release_time: time, farmid: int, ...

particle_variables en underliste av variables som er partikkel-variable, m.a.o.
variable (utenom pid) som ikke endres over tid. Utslippstidspunktet er en slik
og skal alltid være med. Andre ting kan være utslippsposisjon, farmid eller
lignende.

KOMMENTAR:
Her kan ryddes litt opp. Listen med variable kan være første linje i release-filen. Det gjør denne mer selvforklarende og forenkler yaml-filen.

Kvasivariabelen mult er alltid int og burde ikke kreve et converter-felt.
Kunne kanskje også standardisert konvertering for release_time, X, Y, Z som alltid må være med.

gridforce
---------

Denns seksjonen styrer grid og drivkrefter.

Felt::

  module:   obligatorisk
  ibm_forcing:   optional
  grid:     optional

module gir python-modulen for grid-forcing. Kan bruke dot-notasjon
ladim.gridforce.ROMS for moduler i "standard" LADiM. Kan bruke navn for python
modul navn.py i arbeidskatalogen.

ibm_forcing er variable som skal leses inn for IBM. F.eks. temperatur og salt.
Python dictionary med navn i IBM-modul: navn på fil. Eksempel::

  ibm_forcing: {temperature: temp, salinity: salt}

grid er et mulig subseksjon med grid info som overføres til gridforce-modulen.
F.eks. ROMS gridforce kan definere et subgrid.

KOMMENTAR:
Dictionary delen er ufiks og unødvendig. Bare bruk navnene i IBM-en og la
gridforce ta hånd om eventuelle andre variabel-navn i filen.

ibm
---

Denne seksjonen er opional og har bare et felt::

  ibm_module: optional

Enten dot-navn som ladim.ibms.ibm_salmon_lice for ferdig installert IBM. For
lokal IBM i arbeidskatalog bare bruk navn for navn.py

KOMMENTAR:
Her kan legges inn flere elementer som tolkes av IBM-modulen selv.
Skifte navn til IBM med store bokstaver?

output_variables
----------------

Styrer utskriften. Felt::

  format: optional
  outper: obligatorisk
  particle: optional
  instance: obligatorisk
  netcdf_argument:  obligatorisk

format er netcdf-format. Default er NETCDF3_64BIT. Kan og bruke
NETCDF3_CLASSIC, NETCDF3_64BIT_DATA, NETCDF4_CLASSIC.

outper er tid mellom output. Format [verdi, enhet] f.eks. [3, h] for hver
tredje time.

particle: Navn på partikkel-variable som skal skrives ut.

instance: Navn på instans-variable som skal skrives ut. Skal alltid ha med pid.

Hver variabel har et netcdf_argument. Navnet definerer underseksjon og ulike
netCDF attributter som felt. Et ekstra obliigatorisk felt, ncformat som gir
datatypen. Eksempel::

      pid: {ncformat: i4, long_name: particle identifier} X:
          ncformat: f4 long_name: particle X-coordinate

Format i krølleparentes og på flere linjer med innrykk er likeverdig.

KOMMENTAR:
Ekstra optional felt, numrec, er i utviklingsversjon. Angir antall
records før output-filen splittes.

Har foreløpig ikke særlig nytte av netcdf4. Har ikke knagg for å velge
komprimering og chunking. Få litt bedre måte å oppgi den slags, skille
netcdf-tekniske ting fra det som skal ut som attributter.


numerics
--------

Styrer numerikken. Felt::

  dt:   obligatorisk
  advection:  obligatorisk
  diffusion:  optional

dt er modellens tidskritt. Format [verdi, enhet]

advection er adveksjonsalgoritme. EF, RK2 eller RK4 for Euler-Forward,
Runge-Kutta av ulik orden.

diffusion angir et konstand diffusjonsnivå. Verdi = 0 eller at feltet mangler
skrur av diffusjonen.

KOMMENTAR:
Ønske om å kunne ha inn variabel diffusivitet i rom og tid. Kan
f.eks. ha inn et filnavn for å hente. Evt. beregne utfra turbulensverdier i
havmodellen. Litt vanskelig å finne noe generelt å ha her.



