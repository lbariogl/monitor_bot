# Monitoraggio Risorse con Telegram Bot

Questo script ti permette di monitorare l'uso di CPU, RAM e disco sul tuo computer, inviando notifiche su Telegram quando vengono superate soglie specifiche. Dopo un numero configurabile di notifiche consecutive, viene inviato anche un messaggio speciale.

## Prerequisiti

1. **Python 3.12 o superiore** - Assicurati di avere installato Python 3.12 o successivo.
2. **Telegram Bot** - Crea un bot su Telegram seguendo le istruzioni di seguito. Ottieni il token e annotalo.

## Creazione del Bot Telegram

1. **Apri una chat con BotFather** su Telegram cercando `@BotFather`.
2. Invia `/start` per visualizzare i comandi.
3. **Crea il bot** con `/newbot` e segui le istruzioni:
   - Inserisci un nome per il bot.
   - Inserisci un nome utente univoco per il bot, che termina con `_bot`.
4. Dopo la creazione, BotFather ti invierà il **Token API** del bot, che apparirà simile a `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`.

5. **Ottieni il Chat ID**:
   - **Per chat private**: Invia un messaggio al bot. Successivamente, utilizza uno dei seguenti metodi per ottenere il `chat_id`:
     - Vai su `https://api.telegram.org/bot<YOUR-TOKEN>/getUpdates` sostituendo `<YOUR-TOKEN>` con il token del tuo bot.
     - Cerca `chat_id` nei messaggi inviati al bot; avrà un formato simile a `12345678`.
   - **Per gruppi**: Aggiungi il bot al gruppo e ripeti il passaggio sopra per ottenere l'ID del gruppo.

## Installazione

1. **Crea la directory di lavoro e copia lo script**
    ```bash
    mkdir ~/monitor_bot && cd ~/monitor_bot
    # Inserisci il codice Python dello script all'interno di monitor_bot.py
    ```

2. **Configura un ambiente virtuale (opzionale ma consigliato)**
    ```bash
    python3.12 -m venv venv
    source venv/bin/activate
    ```

3. **Installa le dipendenze**
    ```bash
    pip install -r requirements.txt  # Assicurati di includere telegram e psutil
    ```

4. **Configura il file `config.yaml`**

    Crea un file `config.yaml` nella directory di lavoro e personalizzalo con le tue preferenze:
    ```yaml
    telegram:
      token: "IL_TUO_TOKEN_TELEGRAM"
      chat_id: "IL_TUO_CHAT_ID"  # Chat ID del destinatario

    thresholds:
      cpu: 80          # Soglia di utilizzo CPU in percentuale
      ram: 85          # Soglia di utilizzo RAM in percentuale
      disk: 90         # Soglia di utilizzo disco in percentuale
      disk_2: 90       # Soglia di utilizzo per il secondo disco

    repeat_threshold: 5  # Numero di notifiche consecutive per il messaggio speciale
    interval: 60         # Intervallo di monitoraggio in secondi
    ```

5. **Configura il servizio di sistema**

   Crea un file di servizio `systemd` per avviare automaticamente il bot all'avvio del sistema.

    ```bash
    sudo vim /etc/systemd/system/monitor_bot.service
    ```

    Inserisci il seguente contenuto, aggiornando i percorsi a `monitor_bot.py` e al tuo ambiente virtuale:
    ```ini
    [Unit]
    Description=Monitor Bot Service
    After=network.target

    [Service]
    Type=simple
    ExecStart=/home/<utente>/monitor_bot/venv/bin/python /home/<utente>/monitor_bot/monitor_bot.py
    Restart=always
    User=<utente>  # Sostituisci con il tuo nome utente

    [Install]
    WantedBy=multi-user.target
    ```

6. **Ricarica systemd e abilita il servizio**
    ```bash
    sudo systemctl daemon-reload
    sudo systemctl enable monitor_bot.service
    ```

## Avvio, Arresto e Stato del Bot

### Comandi Manuali
Per gestire manualmente il bot, puoi usare questi comandi:

- **Avvia il bot**:
  ```bash
  sudo systemctl start monitor_bot.service
  ```

- **Arresta il bot**:
  ```bash
  sudo systemctl stop monitor_bot.service
  ```

- **Controlla lo stato del bot**:
  ```bash
  sudo systemctl status monitor_bot.service
  ```

### Alias per gestire il Bot

Per semplificare la gestione, puoi aggiungere questi alias al tuo file `.bashrc` o `.zshrc`:

```bash
# Alias per gestire Monitor Bot
alias monitor_start="sudo systemctl start monitor_bot.service"
alias monitor_stop="sudo systemctl stop monitor_bot.service"
alias monitor_status="sudo systemctl status monitor_bot.service"
```

Carica gli alias nel terminale corrente:

```bash
source ~/.bashrc  # o source ~/.zshrc se usi zsh
```

Ora puoi gestire il bot con:

- `monitor_start` - Avvia il bot

- `monitor_stop` - Ferma il bot

- `monitor_start` - Controlla lo stato del bot

## Test del bot

Puoi eseguire un test manuale del bot per assicurarti che funzioni correttamente:

```bash
python monitor_bot.py
```
Se ricevi messaggi di notifica su Telegram, il bot è configurato correttamente.

## Note Importanti

- **Modifica del servizio**: Se apporti modifiche al file di configurazione `monitor_bot.service`, assicurati di riavviare il demone per applicare le modifiche:
  ```bash
  sudo systemctl daemon-reload
  ```

- **Modifica dello script**: Se apporti modifiche al file dello script `monitor_bot.py`, utilizza i comandi monitor_stop e monitor_start per fermare e riavviare il bot:
  ```bash
  monitor_stop
  monitor_start
  ```

Queste operazioni garantiranno che il bot funzioni con le configurazioni più aggiornate.


