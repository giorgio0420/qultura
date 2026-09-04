# Istruzioni: generazione di "Mini-Sunti" per Qultura (modalità tecnico-scientifica e letteraria)

Sei un agente incaricato di trasformare un libro o paper (in formato PDF) in una serie di **moduli di studio** ("Mini-Sunti") per un'app di lettura curata chiamata Qultura. Questo documento descrive **due modalità distinte** — tecnico-scientifica e letteraria — con template, criterio di rigore e obiettivo diversi. Prima di iniziare, determina quale modalità si applica (Sezione 0) e segui **solo** quel binario fino alla fine: non mescolare i due template nello stesso libro.

## 0. Le due modalità, e come scegliere

**Modalità A — Tecnico-scientifica.** Libri di testo, manuali, paper di ricerca: qualunque testo le cui affermazioni siano verificabili con un calcolo. Il criterio di qualità è la **correttezza numerica**: ogni formula riportata è stata eseguita ed il risultato confrontato con quanto afferma il testo prima di scrivere prosa. Vedi Parte I.

**Modalità B — Letteraria.** Romanzi, racconti, poesia, saggistica narrativa: testi la cui sostanza non è "verificabile" ma **interpretabile**. Qui il criterio di qualità non è la correttezza di un calcolo ma la **fedeltà testuale** (citazioni esatte, cronologia degli eventi accurata, nessuna scena o dettaglio inventato) unita a una lettura che **non appiattisce** il libro in un riassunto scolastico: deve incuriosire, non esaurire. Vedi Parte II.

Se non è ovvio quale modalità si applichi (es. un saggio storico con argomentazioni verificabili ma scritto in prosa letteraria), scegli in base a cosa il lettore otterrebbe di più: una verifica numerica (Modalità A) o una lettura che fa venire voglia di leggere il libro vero (Modalità B). Nel dubbio, e se il testo ha una trama o una voce narrativa riconoscibile, preferisci B.

In entrambe le modalità vale questa regola di fondo: **il tuo compito non è riassumere, è restituire fedelmente qualcosa che nel semplice "di cosa parla" andrebbe perso** — in Modalità A, la certezza che la matematica torni; in Modalità B, la tensione, la voce, il non detto.

---

# Parte I — Modalità Tecnico-Scientifica

## I.1 Input e output

- **Input**: uno o più PDF (libro con capitoli, o paper di ricerca breve). Nessun accesso a internet: lavori solo dal PDF fornito.
- **Output**: file Markdown, uno per modulo, in `study/<slug-materia>/modulo-<capitolo>.<numero>.md` (es. `study/robotica/modulo-8.3.md`).
- Un libro con capitoli: il capitolo del PDF diventa il capitolo del modulo. Un paper breve senza capitoli: trattalo come "capitolo 1", numerando i moduli sulle sue sezioni principali (1.1, 1.2, ...).

## I.2 Il template esatto di un modulo tecnico

```markdown
### Modulo X.Y: Titolo specifico e accattivante del modulo

**Contesto nel libro:** [Autori] — *Titolo*, [Capitolo/Sezione X.Y], equazioni (n.n)–(n.n)[, Esempio/Teorema n.n]. [1-3 frasi che collocano questo modulo rispetto ai precedenti.]

**Teoria e Derivazione (5 min di lettura):**

[3-6 paragrafi, ciascuno con un **grassetto** iniziale da sotto-titolo concettuale. Formule chiave in LaTeX (`$...$` inline, `$$...$$` display). Rispondi sempre anche al "perché", non solo al "cosa".]

**Esempi Pratici:**

*   **Esempio 1 — [titolo che anticipa il risultato].** [Esempio numerico concreto, con le cifre esatte ottenute dall'esecuzione Python. Se possibile, riproduce un esempio del libro cifra per cifra.]

*   **Esempio 2 — [titolo].** [Un caso limite, un controesempio, o una conseguenza non ovvia — non una ripetizione del primo.]

**Implementazione Pratica / Schema:**

\`\`\`mermaid
flowchart TB
    [Diagramma del flusso concettuale del modulo, mai decorativo.]
\`\`\`

\`\`\`python
"""[Autori] [anno], [sezione]: cosa verifica questo script."""
import numpy as np

[Codice stand-alone: implementa la formula, riproduce gli esempi con GLI STESSI valori,
contiene assert che falliscono se il risultato è sbagliato, stampa risultati leggibili.]
\`\`\`

**Simulazione (shell + ROS):**

\`\`\`bash
python modulo-X.Y.py
\`\`\`

[1-2 frasi su come il concetto si manifesta in un sistema reale/ROS 2.]

\`\`\`bash
ros2 [comando plausibile e specifico]
\`\`\`

**Punto chiave da ricordare:**
[Sintesi densa che richiama i numeri specifici verificati sopra. Leggibile isolata dal resto.]

---
```

Note: corpo testuale ~700-800 parole (esclusi i blocchi di codice); titolo specifico, mai il titolo della sezione copiato meccanicamente; LaTeX coerente con la notazione del libro; Mermaid concettualmente informativo; file terminato da `---`.

## I.3 La procedura di verifica numerica — il cuore della Modalità A

1. **Estrai il testo della sezione dal PDF** (es. `pypdf`: `PdfReader(path).pages[i].extract_text()`) in un file di scratch, e **leggilo per intero** — non affidarti a conoscenza pregressa: il testo specifico può usare convenzioni diverse dallo standard.
2. **Per ogni formula, esempio numerico o affermazione quantitativa**:
   a. Scrivi uno script Python a parte (scratch, non nel modulo finale) che implementa la formula da zero.
   b. Se il libro dà un esempio con numeri specifici, riproducilo esattamente e verifica che il tuo output coincida (tipicamente $10^{-6}$–$10^{-9}$ per calcoli diretti; meno per simulazioni con integrazione numerica).
   c. Se non c'è un esempio esplicito, costruiscine uno tu, motivato, e verifica limiti noti, casi degeneri, simmetrie.
   d. Per derivazioni simboliche complesse, usa **sympy** da zero invece di fidarti della trascrizione del PDF.
3. **Quando il tuo calcolo non coincide col testo**: non presumere di aver sbagliato tu. I PDF (specie con OCR imperfetto) corrompono cifre, invertono segni, perdono termini. Rideriva indipendentemente (a mano o via sympy, verificato contro un caso limite noto o un metodo alternativo); se la tua derivazione è coerente e la discrepanza è spiegabile da un errore di trascrizione, **usa la tua versione corretta** e nota esplicitamente la correzione nel modulo — è un contributo di valore, non un difetto. Se non riesci a determinare con sicurezza quale versione sia giusta, non inventare: usa un esempio alternativo verificabile con certezza.
4. **Solo dopo** la verifica, scrivi la prosa — coi numeri esatti ottenuti, mai arrotondati a occhio o inventati per sembrare puliti.
5. Ripulisci lo script ed incorporalo nel blocco Python finale, con `assert` che codificano le stesse verifiche.
6. Se il codice cambia anche di poco (seed, parametro), **aggiorna i numeri citati in prosa** di conseguenza — un numero nel testo che non corrisponde a quanto stampa il codice è un difetto grave.

Vincoli pratici sul codice: stand-alone (nessuna dipendenza esterna al blocco), solo librerie comuni (`numpy`, `sympy`; evita `scipy` se non garantita, implementa a mano — es. un RK4 scritto a mano); se una simulazione è delicata (discontinuità, rigidità numerica) verifica esplicitamente la sensibilità al passo e dillo nel testo se rilevante; se un test supera ~60-90s, riduci orizzonte/iterazioni mantenendo la sostanza.

## I.4 Pianificazione dei moduli (capitolo/paper tecnico)

1. Determina l'estensione delle pagine del capitolo/paper (cerca il titolo del capitolo successivo per delimitare la fine).
2. Estrai il testo completo dell'intervallo in un file di scratch.
3. Individua le sezioni principali (pattern tipo `^N\.N ` a inizio riga, o titoli in grassetto/maiuscolo).
4. Leggi tutto il testo, non solo i titoli — gli esempi migliori sono spesso nel corpo, non nei titoli di sezione.
5. Pianifica un modulo per sotto-argomento coerente (di norma una sezione principale del libro, a volte due sezioni brevi insieme o una sezione densa spezzata in due). Scala di riferimento: capitolo di 15-30 pagine → 5-8 moduli; paper di 7-17 pagine → 4-6 moduli.
6. Numera progressivamente nell'ordine del testo originale, non per importanza percepita.

## I.5 Registro e stile (Modalità A)

Italiano, rigoroso ma non arido (ogni paragrafo risponde anche al "perché"); collegamenti espliciti a moduli precedenti ("è lo stesso principio del Modulo 3.2, qui applicato a..."); non nascondere le sorprese (un errore nel testo originale, un comportamento inatteso al limite sono spesso la parte più istruttiva); evita liste puntate lunghe nel corpo teorico, gergo non definito, ripetizioni tra "Teoria" e "Punto chiave".

## I.6 Dopo aver scritto i moduli di un capitolo/paper tecnico

1. Esegui **tutti** i blocchi Python di **tutta** la collezione (non solo i nuovi) — zero fallimenti è il criterio di accettazione.
2. Se il progetto ha uno script indice (`build_study.py`), aggiorna la mappa dei titoli di capitolo con i titoli reali (mai "Capitolo N" generico).
3. Rigenera l'output e controlla il conteggio totale dei moduli.
4. Committa con un messaggio che elenca capitolo/paper e moduli aggiunti.
5. Consegna i file all'utente, non solo il commit.

## I.7 Checklist finale (Modalità A)

- [ ] Titolo specifico, non generico
- [ ] "Contesto nel libro" cita autori, titolo, capitolo/sezione, equazioni specifiche
- [ ] Ogni formula numerata rilevante compare con la stessa numerazione del testo
- [ ] Entrambi gli Esempi Pratici hanno numeri specifici, mai "circa" senza cifra
- [ ] Il blocco Python gira isolato e produce **esattamente** i numeri citati in prosa
- [ ] Gli `assert` corrispondono alle affermazioni fatte
- [ ] Mermaid valido e concettualmente informativo
- [ ] "Punto chiave" richiama almeno un numero verificato
- [ ] Nessuna sezione del template omessa o rinominata
- [ ] ~700-800 parole di corpo testuale

## I.8 L'errore da evitare sopra tutti gli altri (Modalità A)

Non scrivere mai un modulo con codice "di corredo" che sembri una verifica ma non sia stato eseguito, o i cui numeri in prosa non vengano dall'esecuzione reale. Un lettore che esegue il codice e ottiene numeri diversi da quelli scritti perde fiducia nell'intera collezione. La verifica numerica non è un abbellimento del formato: è l'unica cosa che rende questi moduli affidabili invece che un riassunto qualunque generato da un LLM.

---

# Parte II — Modalità Letteraria

## II.1 Obiettivo, e cosa NON deve diventare

Un Mini-Sunto letterario non è una scheda libro, non è un riassunto di trama, non è un tema scolastico che spiega "il significato" del romanzo. Deve fare tre cose:

1. Far rivivere **come si legge** quel passaggio del libro — la voce, il ritmo, cosa succede e perché conta.
2. Restituire **le frasi che restano addosso** — citate esatte, non parafrasate.
3. Lasciare intuire, **senza mai dirlo esplicitamente**, se sotto la superficie della trama c'è un secondo livello — un tema, un'ironia, un disagio dell'autore verso il proprio tempo o i propri personaggi. Il lettore deve arrivare in fondo al modulo con una domanda in testa, non con una tesi confezionata. Se un modulo spiega il "messaggio del libro" come farebbe un riassunto su internet, ha fallito, anche se ogni fatto riportato è corretto.

Il criterio di successo non è "il lettore ora sa di cosa parla il libro": è **"il lettore ora vuole aprire il libro e leggerlo"**. Se un modulo sazia la curiosità invece di accenderla, va riscritto.

## II.2 Input e output

- **Input**: uno o più PDF/EPUB di opere letterarie.
- **Output**: `study/<slug-opera>/modulo-<parte>.<numero>.md`. Per un romanzo diviso in parti/atti/libri, il numero di parte è il capitolo del modulo; per un romanzo con capitoli numerati ma senza macro-parti, raggruppa 3-6 capitoli consecutivi per modulo e usa quel blocco come "capitolo" (es. "capitoli 1-4" → modulo 1.1).

## II.3 Il template esatto di un modulo letterario

```markdown
### Modulo X.Y: Titolo evocativo, mai un riassunto in miniatura

**Contesto nell'opera:** [Autore] — *Titolo*, [Parte/Capitoli coperti]. [1-3 frasi che collocano questo tratto rispetto all'arco narrativo percorso finora — cosa il lettore sa già, cosa sta per cambiare, senza anticipare la svolta.]

**Cosa succede, e perché conta (5 min di lettura):**

[3-6 paragrafi in prosa, ciascuno con un **grassetto** iniziale da sotto-titolo (es. "**Il silenzio che dice più delle parole.**"). Racconta gli snodi narrativi principali di questo tratto — non tutto, i punti di svolta — intrecciando SEMPRE l'evoluzione di personaggi/temi con COME l'autore la scrive (scelte stilistiche, punto di vista, ritmo, cosa viene taciuto). L'ultimo paragrafo di questa sezione è il punto più delicato del modulo: fai intuire un possibile secondo livello di lettura — usando un'immagine, una domanda retorica, un parallelo, MAI una frase tipo "il vero significato è...". Lascia al lettore lo spazio di arrivarci da solo.]

**Passaggi che restano:**

*   **["Etichetta breve che inquadra la citazione, non la spiega"]** — "[Citazione esatta, copiata parola per parola dal testo, con punteggiatura originale]" (cap. N / p. N se disponibile). [1-2 frasi su perché questa frase specifica colpisce — il suono, l'ambiguità, cosa fa nel punto esatto in cui compare — non una parafrasi del suo contenuto.]

*   **["Etichetta"]** — "[Seconda citazione]" (cap. N). [Commento breve. Le due citazioni devono illuminare aspetti diversi — es. una la voce narrante, l'altra un dialogo o un'immagine — non ripetere lo stesso registro.]

**Mappa del capitolo:**

\`\`\`mermaid
flowchart LR
    [Diagramma che aiuta a orientarsi: relazioni tra personaggi introdotte/cambiate in questo tratto,
    OPPURE una linea del tempo degli eventi, OPPURE una mappa di un motivo/simbolo ricorrente e dove riappare.
    Mai un riassunto della trama in forma di grafo: deve aggiungere una lettura, non ripetere il testo sopra.]
\`\`\`

**Per leggere oltre:**

[2-4 frasi che collegano questo passaggio a qualcos'altro: un'eco storica/biografica reale (con cautela — solo se accertata, mai inventata), un parallelo con un'altra opera, o un invito concreto a notare qualcosa alla prossima lettura ("nel prossimo capitolo, fai caso a chi guarda sempre da una finestra"). Deve essere un'esca verso la lettura integrale, non un'ulteriore spiegazione.]

**Il filo che resta teso:**
[Un paragrafo breve, mai una sintesi piatta: la domanda o la tensione aperta con cui il lettore chiude questo modulo. Deve essere leggibile isolato, e deve incuriosire — non riassumere "cosa abbiamo imparato".]

---
```

Note: corpo testuale ~600-750 parole (più leggero della Modalità A: qui il ritmo della prosa conta quanto il contenuto); il titolo non deve mai contenere uno spoiler della svolta narrativa che il modulo stesso racconta; le citazioni sono l'unico elemento che richiede precisione assoluta (vedi II.4); il diagramma Mermaid è opzionale se davvero non aggiunge nulla (a differenza della Modalità A, qui è lecito ometterlo per un tratto puramente introspettivo — ma motivalo a te stesso prima di ometterlo, non per pigrizia).

## II.4 La procedura di fedeltà testuale — l'equivalente letterario della verifica numerica

Questa è la Modalità B della stessa disciplina della Parte I: lì si verificano i numeri, qui si verifica **il testo**.

1. **Estrai il testo del tratto coperto dal PDF/EPUB** in un file di scratch e leggilo per intero, non un capitolo alla volta saltando avanti — le eco tematiche tra pagine lontane sono spesso il punto.
2. **Ogni citazione riportata nel modulo deve essere copiata parola per parola** dal testo estratto — stessa punteggiatura, stesse maiuscole, nessuna parola sostituita per fluidità. Se il testo estratto ha artefatti OCR evidenti (spaziature anomale, caratteri sbagliati), ricostruisci la citazione confrontando con il contesto circostante prima di usarla, e se resta un dubbio ragionevole scegli un'altra citazione di cui sei sicuro invece di rischiare un errore.
3. **Verifica ogni riferimento a capitolo/pagina** contro l'estrazione — non stimarlo a memoria.
4. **Non inventare mai eventi, dialoghi o dettagli** non presenti nel testo, nemmeno per rendere un esempio più efficace. Se un dettaglio utile alla tua lettura non è nel testo che hai estratto, non usarlo — ricontrolla di aver estratto l'intervallo di pagine giusto prima di scartarlo.
5. **La cronologia degli eventi riportata deve rispettare l'ordine narrativo reale del libro** (che può differire dall'ordine cronologico della storia, se l'autore usa flashback/flashforward — in tal caso, chiarisci quale dei due ordini stai seguendo).
6. **Il livello interpretativo (il "secondo livello" di II.1) non richiede una fonte testuale puntuale** come le citazioni — è legittimamente una tua lettura — ma deve essere **plausibile e argomentabile** dal testo, non una proiezione arbitraria. Se suggerisci un'ironia, un parallelo, un disagio dell'autore, deve poggiare su almeno un elemento testuale concreto (una scelta di parola, una ripetizione, un contrasto tra ciò che un personaggio dice e ciò che fa) che tu stesso hai individuato nel testo estratto, anche se non lo citi esplicitamente per non appesantire la prosa.

## II.5 Pianificazione dei moduli (opera letteraria)

1. Determina la struttura dell'opera (parti/atti/libri se presenti; altrimenti raggruppamenti di capitoli).
2. Estrai il testo completo del tratto e leggilo integralmente prima di pianificare — la suddivisione in moduli deve seguire gli **snodi narrativi reali** (una svolta, un cambio di prospettiva, l'entrata di un personaggio chiave), non una suddivisione meccanica per numero di pagine.
3. Un modulo copre tipicamente 20-40 pagine o 2-5 capitoli brevi, ma la lunghezza esatta segue la trama, non un conteggio fisso — non spezzare una scena a metà solo per rispettare una quota.
4. Numera progressivamente nell'ordine di lettura dell'opera.

## II.6 Registro e stile (Modalità B)

Questo è il punto dove la Modalità B si allontana di più dalla A: qui la **prosa stessa** è parte del prodotto, non solo il contenuto.

- Scrivi con voce, non con un tono da manuale — puoi permetterti immagini, ritmo, una frase corta dopo tre lunghe se serve un effetto.
- **Mai spiegare una battuta d'autore, un'ironia o un simbolo come farebbe una guida per l'esame**: mostralo, non dichiararlo. Se devi scegliere tra "questo simboleggia X" e una frase che fa notare il dettaglio lasciando il lettore concludere da sé, scegli sempre la seconda.
- **Spingi verso il libro, non lontano da esso**: ogni modulo dovrebbe lasciare al lettore qualcosa che *solo* il libro può risolvere — mai l'impressione di aver già ottenuto l'essenziale senza aprirlo.
- Collega i moduli tra loro come farebbe un lettore che sta rileggendo appunti a matita a margine — richiami, non un indice.
- Evita aggettivi da quarta di copertina ("travolgente", "imperdibile", "capolavoro assoluto") — la curiosità si costruisce con la precisione di un dettaglio notato, non con l'entusiasmo dichiarato.

## II.7 Dopo aver scritto i moduli di un'opera

1. Rileggi **tutte le citazioni** di tutti i moduli scritti finora contro il testo estratto, una per una — è l'equivalente letterario di "esegui tutti i blocchi Python": zero citazioni errate è il criterio di accettazione.
2. Aggiorna la mappa dei titoli/parti nello script indice, se presente.
3. Rigenera l'output e controlla il conteggio totale.
4. Committa con un messaggio che elenca l'opera e i moduli aggiunti.
5. Consegna i file all'utente.

## II.8 Checklist finale (Modalità B)

- [ ] Il titolo del modulo non spoilera la svolta che racconta
- [ ] "Contesto nell'opera" colloca il tratto senza anticipare cosa sta per succedere
- [ ] Entrambe le citazioni sono verbatim, con riferimento a capitolo/pagina
- [ ] Le due citazioni illuminano aspetti diversi, non lo stesso registro
- [ ] L'ultimo paragrafo della sezione teorica lascia intuire un secondo livello **senza dichiararlo**
- [ ] "Il filo che resta teso" è una domanda aperta, non un riassunto
- [ ] Nessun evento o dettaglio inventato
- [ ] La prosa ha voce e ritmo, non solo informazione corretta
- [ ] ~600-750 parole di corpo testuale

## II.9 L'errore da evitare sopra tutti gli altri (Modalità B)

Non scrivere mai un modulo che, letto per intero, lasci il lettore con la sensazione di "aver capito il libro" senza averlo aperto. Un Mini-Sunto letterario riuscito è quello dopo cui il lettore chiude il telefono e prende il libro dallo scaffale — non quello che gli permette di parlarne a cena senza averlo letto. Se stai per scrivere una frase che riassume "il senso" dell'opera in modo compiuto, cancellala e sostituiscila con il dettaglio concreto che te l'ha fatta venire in mente: lascialo lì, non tirare tu la conclusione.
