# Hiltron Protec (Integrazione Custom per Home Assistant)

Integrazione nativa per Home Assistant creata per interfacciare le centrali d'allarme serie **Hiltron Protec** (Protec8 e compatibili con modulo di rete/DXETH).

Il componente comunica direttamente con la centrale tramite chiamate HTTP locali con autenticazione Basic, gestendo la lettura degli stati in polling asincrono non bloccante via `DataUpdateCoordinator`.

## Compatibilità Hardware

* **Testato e Verificato**: Testato e sviluppato attivamente su centrale **Hiltron Protec8GSM** dotata di scheda di rete **DXETH**.
* **Altre Centrali**: Non avendo a disposizione altri modelli per test diretti (come la **Hiltron Protec6GSM**), l'integrazione non è stata verificata su di essi; tuttavia, la logica di comunicazione si basa sul protocollo HTTP esposto dalla scheda di rete, quindi **dovrebbe funzionare in linea teorica con tutte le centrali Hiltron compatibili con il modulo DXETH**. Riscontri e feedback da possessori di altri modelli sono benvenuti!

## Caratteristiche Principali

* **Configurazione Guidata da UI**: Nessun file YAML da modificare. Il flusso di configurazione (Config Flow) integra campi mascherati per password e PIN utente, con verifica istantanea delle credenziali prima del salvataggio.
* **Polling Asincrono Locale**: Esecuzione efficiente e reattiva senza intaccare l'event loop di Home Assistant.
* **Pannello Allarme Completo**: Entità `alarm_control_panel` sincronizzata con gli stati moderni di Home Assistant (`disarmed`, `armed_away`, `armed_home`, `triggered`).
* **Sensori di Zona**: Entità `binary_sensor` dedicate per ciascuna linea (Zone 1–8) con `device_class` appropriate e monitoraggio linea 24H (Tamper/Manomissione).
* **Sensore Testuale "Memoria Allarme"**: Entità testuale dedicata che elenca in chiaro quali zone hanno causato l'ultimo scatto d'allarme.
* **Uscite Ausiliarie**: Entità `switch` per il comando e la gestione dei relè/attuatori.
* **Compatibilità Parallela con App Ufficiale**: L'integrazione **non interferisce né pregiudica** l'uso dell'applicazione ufficiale **MyHiltron**, che continuerà a funzionare regolarmente in parallelo.

## Requisiti e Best Practices di Rete

* **Ambiente esclusivamente LAN**: Si raccomanda caldamente l'impiego di questa integrazione **esclusivamente all'interno della stessa rete locale (LAN)** tra l'istanza di Home Assistant e la scheda di rete della centrale Hiltron.
* È vivamente sconsigliato esporre l'interfaccia HTTP della centrale direttamente su Internet o effettuare port forwarding senza adeguate misure di sicurezza (es. VPN dedicate come WireGuard/Tailscale).

## Installazione

### Tramite HACS (Consigliato)

1. Apri **HACS** nella tua istanza di Home Assistant.
2. Vai nella sezione **Integrazioni**.
3. Clicca sui tre puntini in alto a destra e seleziona **Repository personalizzati** (*Custom repositories*).
4. Incolla l'URL del tuo repository GitHub:
   ```
   https://github.com/tuo-username/ha-hiltron-protec
   ```
5. Seleziona **Integrazione** come categoria e clicca su **Aggiungi**.
6. Cerca **Hiltron Protec** nella lista di HACS, clicca su **Scarica** e riavvia Home Assistant.

### Installazione Manuale

1. Scarica il repository e copia la cartella `hiltron` (presente sotto `custom_components/`) all'interno della cartella `custom_components` della tua installazione di Home Assistant:
   ```
   /config/custom_components/hiltron/
   ```
2. Riavvia Home Assistant.

## Configurazione

1. Vai in **Impostazioni** -> **Dispositivi e Servizi** -> **Aggiungi integrazione**.
2. Cerca **Hiltron Protec**.
3. Compila i campi richiesti:
   * **Indirizzo IP**: IP locale assegnato alla centrale (es. `192.168.1.xxx`).
   * **Indirizzo MAC**: Indirizzo fisico della scheda DXETH (formato senza separatori, es. `001122334455`).
   * **Password DXETH**: Password di accesso rete (campo protetto).
   * **Codice Utente**: Codice PIN utente abilitato al comando (campo protetto).
4. Clicca su **Invia**: verrà eseguito un test immediato verso la centrale prima di registrare l'integrazione.

## Note di Sviluppo

Il progetto è nato per rispondere a un'esigenza personale di integrazione nativa e pulita. Alcune parti del codice e della logica di parsing sono state sviluppate con approccio *vibecoded* assistito da AI, ottimizzate sul campo per garantire stabilità, leggerezza ed efficienza nell'ecosistema Home Assistant. Eventuali issue e pull request per estensioni o rifiniture sono sempre ben accette.

## Disclaimer e Limitazione di Responsabilità

* **Nessuna Affiliazione Ufficiale**: Questo è un progetto indipendente e amatoriale sviluppato da terze parti. L'autore **non ha alcun tipo di affiliazione commerciale, accordo, partnership, sponsorizzazione o interesse economico con Hiltron S.p.A. o Hiltron S.r.l.** Marchi e nomi registrati appartengono ai rispettivi proprietari.
* **Sicurezza Domestica**: Il software viene distribuito "così com'è" (*AS IS*), a titolo puramente didattico e hobbistico, senza garanzie di alcun tipo, esplicite o implicite. Trattandosi di un sistema destinato alla sicurezza di immobili e beni, **l'utente installa e utilizza questa integrazione interamente a proprio rischio e pericolo**.
* L'autore e gli eventuali contributori declinano esplicitamente qualsiasi responsabilità civile o penale per:
  * Mancata attivazione o disattivazione degli allarmi;
  * Falsi allarmi o mancata segnalazione di intrusioni/manomissioni;
  * Furti, intrusioni, danni diretti o indiretti a cose o persone;
  * Malfunzionamenti software o anomalie di rete.
