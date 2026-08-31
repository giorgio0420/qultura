# Sistema di informazione laterale curata — Brief di progetto

## Obiettivo
Dashboard/PWA personale che aggrega e cura contenuti **scritti** da fonti selezionate,
per sostituire lo scroll su Instagram/YouTube con una lettura mirata sugli interessi reali
dell'utente. Niente riproduzione audio/video: tutto il contenuto arriva come testo da leggere.

## Vincoli fondamentali
- **Solo testo.** Nessun player video/audio nell'interfaccia. Anche i contenuti che nascono
  come video (podcast, interviste, conferenze stampa) vanno trasformati in testo — vedi sotto.
- **Niente "flusso di uscite".** Per la musica in particolare: no notifiche tipo "è uscito il
  nuovo singolo di X". L'obiettivo è la critica/analisi scritta, non l'annuncio.
- **Aggiornamento giornaliero**, non in tempo reale — è una scelta deliberata per non ricreare
  il loop di controllo compulsivo che questo progetto vuole eliminare.
- **Lingua**: default inglese. Traduzione italiana disponibile a richiesta (toggle per singolo
  pezzo). Le fonti italiane (Rockit, L'Ultimo Uomo, ForzaRoma, Rick DuFer, Il Tascabile...)
  restano in italiano di default.
- **Consegna**: PWA installabile sulla home screen del telefono — niente store, funziona come
  un'app dedicata.
- **Instagram è fuori dall'automazione**: non esiste un modo legale/stabile per leggere in
  automatico i post degli account seguiti (nessuna API pubblica per following personale).
  Resta uso manuale e separato, non parte di questo sistema.

## Peso/priorità dei contenuti
1. **Massima priorità** (più volume, più profondità): AI / Robotica / Elettronica —
   è la categoria "fondante" per l'evoluzione professionale dell'utente.
2. **Peso normale**: Calcio/Roma, Musica.
3. **Peso minore** (fonti oggettivamente più scarse, contenuto più diradato): Scacchi,
   Running & Calisthenics, Filosofia/Stoicismo/Cultura.

## Come si estrae il contenuto scritto

### Fonti native scritte (RSS diretto)
Blog, testate e magazine hanno RSS nativo sul sito — nessuna elaborazione aggiuntiva richiesta.

### Fonti YouTube (canali "parlati": podcast, analisi, conferenze stampa)
Non si guarda/ascolta il video. Si estrae la **traccia sottotitoli** (generata automaticamente
da YouTube o caricata dal creator) come testo puro, poi si passa quel testo nello strato di
curatela AI per ottenere un estratto/riassunto scritto dei punti trattati — non "è uscito un
episodio", ma la sostanza di cosa è stato detto.

Limiti noti da tenere presenti nell'implementazione:
- Trascrizione affidabile su parlato pulito da studio (es. Rick DuFer, Cronache di Spogliatoio).
- Meno affidabile su interviste pre/post gara con rumore di fondo, voci sovrapposte, domande
  accavallate (es. conferenze stampa Gasperini, interviste giocatori Roma).
- Se un video ha i sottotitoli disattivati dal creator, quel contenuto va semplicemente saltato.
- Per contenuti dimostrativi/visivi puri (es. tecnica di un esercizio calisthenics), la parte
  visiva non è recuperabile in testo — solo il commento parlato lo è.

## Categorie e fonti

### 1. AI / Robotica / Elettronica (priorità massima)
- **Scritte (testate)**: IEEE Spectrum, MIT Technology Review, Ars Technica, The Robot Report,
  SpaceNews
- **Scritte (aziende e istituzioni del settore)**: NVIDIA Developer Blog
  (https://developer.nvidia.com/blog) e NVIDIA Blog (https://blogs.nvidia.com),
  OpenAI (https://openai.com/news), Google DeepMind (https://deepmind.google/blog),
  Google Research (https://research.google/blog), Hugging Face (https://huggingface.co/blog),
  Waymo (https://waymo.com/blog); italiane: Comau (https://www.comau.com) e
  Agenzia Spaziale Italiana (https://www.asi.it).
  Senza RSS, quindi non automatizzabili: Tesla (403 sul feed), SpaceX, Boston Dynamics,
  Anthropic, Figure, Agility Robotics, IIT, Leonardo, STMicroelectronics, Datalogic, Avio,
  Telespazio, D-Orbit. Le loro notizie arrivano comunque via The Robot Report (robotica
  industriale e umanoidi) e SpaceNews (spazio).
- **YouTube (via trascrizione)**: Kevin Wood | Robotics & AI, IBM Technology, RoboticaPedia,
  Polimi OpenKnowledge, MATLAB, EPICODE Institute of Technology, TED/TEDx, Amedeo Balbi, Geopop,
  Salvatore Sanfilippo, Stepwise Chemistry, e altri canali tech/scienza dall'elenco iscrizioni
  YouTube completo (152 canali, disponibile su richiesta).

### 2. Musica (rap/hip-hop IT+US, con apertura a rock/cantautorato italiano)
- **Scritte**: Rockit, Rolling Stone Italia, Rumore (IT) — Pitchfork, HipHopDX (US/intl).
  Complex non ha piu un feed RSS raggiungibile, escluso. Esse Magazine
  (essemagazine.it) e attivo ma non pubblica RSS: resta fuori dall'automazione.
- **Artisti di riferimento** (per tarare la selezione, non per notifiche dirette): Nayt,
  Fabri Fibra, Marracash, Guè, Ernia, Kid Yugi, Kendrick Lamar, Drake, Kanye West; dalle playlist personali
  emergono anche Neffa, Green Day, Negrita, Jovanotti — il gusto musicale è più ampio del solo
  rap/hip-hop.
- Jazz/soul "vecchia scuola": categoria aperta, fonti da definire.

### 3. Calcio/Roma
- **Scritte**: L'Ultimo Uomo (analisi tattica seria, il taglio di riferimento), ForzaRoma.info,
  Corriere dello Sport (sezione Roma)
- **YouTube (via trascrizione)**: Cronache di Spogliatoio, Il Critico Calcistico, canale
  ufficiale AS Roma (conferenze stampa Gasperini, interviste pre/post gara)

### 4. Scacchi
- **Scritte**: Chessbase News, FIDE
- **YouTube**: Chess.com Italiano, Anna Cramling, MontyMagnus Scacchi

### 5. Running & Calisthenics (nuova categoria, senza iscrizioni pregresse)
- **Scritte**: Runner's World, PodiumRunner
- **YouTube proposti, da confermare con l'utente**: Run Smarter with Brodie Sharpe (fisioterapista,
  evidence-based), Sage Canaday / Vo2max Productions (corsa); THENX (Chris Heria), Calisthenics
  Movement (corpo libero)

### 6. Filosofia / Stoicismo / Cultura
- **Scritte**: Il Tascabile (Treccani — saggistica ampia: filosofia, scienza, cultura),
  ArteSettima (https://artesettima.it — cinema come lettura del presente)
- **YouTube (via trascrizione)**: Rick DuFer / BarbaSophia (Matteo Saudino), Nova Lectio

## Livello di curatela (AI layer)
Un livello che processa ogni nuovo contenuto per:
- Tradurre quando serve (mantenendo l'originale disponibile)
- Riassumere/estrarre la sostanza (specialmente dalle trascrizioni)
- Scartare duplicati e contenuti ridondanti (nell'analisi dell'export Instagram è emerso un
  cluster di 6+ pagine stoiche che dicono sostanzialmente la stessa cosa — stessa logica di
  deduplica va applicata qui)
- Assegnare priorità secondo i pesi sopra

## Stack proposto (l'utente ha già "vibe codato" altre app, non è uno sviluppatore esperto)
- **Ingestion**: script che legge RSS (feedparser o simile) + estrae trascrizioni YouTube,
  schedulato una volta al giorno
- **Storage**: leggero — SQLite o anche solo file JSON, uso personale a basso volume
- **Curatela**: chiamate all'API Claude per traduzione/riassunto/deduplica/scoring
- **Frontend**: PWA con tab per categoria, card con fonte + lingua originale + traduzione,
  installabile su home screen del telefono
- **Hosting**: qualcosa di gratuito per iniziare (Vercel/Render per il frontend, cron gratuito
  per lo script di ingestion)

## Contesto utente
- Lavora nel settore dev/tech, esperienza pregressa di "vibe coding" ma non sviluppatore esperto
- Ha esportato following Instagram (~918 account — quasi tutti fuori dalle categorie sopra,
  soprattutto grafo sociale/locale, non rilevante per questo progetto) e iscrizioni YouTube
  (152 canali, in gran parte già mappati sopra)

## Prossimi passi aperti
- Confermare/aggiustare l'elenco fonti Running & Calisthenics
- Iniziare l'implementazione vera e propria: backend di ingestion + curatela, poi frontend
