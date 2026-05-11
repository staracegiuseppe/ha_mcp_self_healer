# Home Assistant MCP Self Healer

Add-on Home Assistant autonomo che espone un piccolo server MCP, legge i log di Home Assistant, individua errori ricorrenti, prova remediation conservative e invia una mail con diagnosi e interventi eseguiti.

## Cosa fa

- Si collega a Home Assistant tramite REST API (`SUPERVISOR_TOKEN` negli add-on o Long-Lived Access Token).
- Espone strumenti MCP via JSON-RPC HTTP su `/mcp`.
- Controlla periodicamente i log (`/api/error_log`).
- Classifica gli errori tramite playbook locali.
- Esegue solo azioni consentite dalla configurazione.
- Crea un backup prima di azioni invasive, se richiesto.
- Invia una mail con errore rilevato, decisione presa, risultato e prossimi passi.

## Avvio locale

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -m ha_mcp_self_healer
```

## Add-on Home Assistant

Copiando questa cartella in un repository add-on o nella cartella `/addons`, Home Assistant può installarlo come add-on locale.

Configura almeno:

- `ha_url`
- `ha_token` se non gira come add-on con `SUPERVISOR_TOKEN`
- `smtp_host`, `smtp_user`, `smtp_password`, `email_from`, `email_to`

## Limiti di sicurezza

Questa app non modifica file YAML arbitrari e non fa restart distruttivi senza che l'azione sia abilitata. È volutamente prudente: quando non riconosce un errore, lo segnala via mail invece di improvvisare.
