# Qultura

<img src="qultura.gif" alt="Qultura" width="160">

Una PWA personale: un digest quotidiano curato al posto dello scroll su Instagram
o YouTube, più una libreria di appunti di studio scritti da zero. Niente feed
infinito, niente tempo reale — un aggiornamento al giorno, pensato per essere
letto e chiuso, non per tenerti incollato allo schermo.

## Il nome

Qultura = Q + cultura. La cultura è utile quando *rompe* qualcosa — un'idea
fissa, un pregiudizio, un modo di vedere le cose dato per scontato — non
quando la accumuli e basta. Nel logo la Q non si chiude: la coda taglia il
cerchio invece di richiuderlo, un cerchio interrotto invece che perfetto.
L'idea è ripresa dal concept album di Nayt, *La Lettera Q*.

## Cosa c'è dentro

**News** — sette categorie (AI & Robotica, Mondo, Calcio, Musica, Scacchi,
Filosofia e cultura, Running), aggiornate una volta al giorno da un lettore
automatico che passa tutto attraverso un livello di curatela: traduce,
riassume, scarta il rumore e tiene solo quello che vale la pena leggere.
Ogni pezzo ha un bottone di traduzione meccanica IT/EN — non riscrive il
contenuto, sposta solo la lingua.

**Libri** — una libreria di moduli di studio (oltre 130, soprattutto Controlli
Automatici e Robotica, con qualche paper). Non sono riassunti generati e
basta: ogni formula ed esempio è verificato numericamente prima di essere
pubblicato, e ogni errore di trascrizione trovato nei testi di partenza viene
corretto e segnalato esplicitamente invece di essere riprodotto in silenzio.

## Come funziona

Sito statico, nessun server dietro: una GitHub Action gira una volta al
giorno, legge le fonti pubbliche configurate, cura i contenuti con un
modello linguistico e pubblica un digest aggiornato su GitHub Pages. Il
frontend è una singola pagina installabile sulla home screen del telefono.

## Nota

Progetto personale, pensato per un solo utente (io). Non è un prodotto,
non raccoglie dati di nessun altro: è solo il modo in cui leggo le cose che
mi interessano.
