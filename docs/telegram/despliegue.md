# Despliegue en el VPS

El paso a paso para dejar labubot corriendo en un VPS Ubuntu 24.04 con el webhook
de Telegram detrás de un túnel de **ngrok** con dominio fijo y gratis. No hace
falta comprar un dominio ni abrir puertos. Los archivos de configuración del
servidor (las unidades de systemd, el túnel y la rotación de logs) se crean en
cada paso, con el contenido que está acá.

```text
Telegram ──HTTPS──▶ ngrok (<nombre>.ngrok-free.dev) ──▶ labubot-ngrok ──▶ uvicorn 127.0.0.1:8000 (labubot-api)
                                                                               │
                                       labubot-worker (daemon.py, cada hora) ──┴──▶ labubot.db (WAL)
```

Son tres servicios systemd: `labubot-api` (el webhook), `labubot-worker` (las
corridas: cada hora y cuando alguien manda `/start`) y `labubot-ngrok` (el
túnel). La api y el worker comparten `labubot.db`.

**Por qué ngrok.** El plan gratis da un dominio fijo por cuenta
(`<nombre>.ngrok-free.dev`, o `.ngrok-free.app` en cuentas viejas): `set_webhook.py`
se corre una sola vez. Alcanza de sobra para 5 usuarios: 20.000 pedidos y 1 GB por
mes, y cada mensaje o botón es un pedido. Un quick tunnel de Cloudflare cambia de
URL en cada reinicio, y un túnel con nombre pide tener un dominio en Cloudflare.
Si más adelante tenés dominio, la alternativa con Caddy está al final.

**Antes de comprometerte con un plazo largo**, corré la prueba de IP de
[`vps.md`](vps.md) §7: LinkedIn trae ~60 % de las ofertas y no está medido desde
una IP de datacenter.

Valores que vas a necesitar a mano:

| Qué | De dónde |
|---|---|
| IP del VPS | El panel del proveedor |
| `TELEGRAM_TOKEN` del bot real | @BotFather |
| `ADMIN_CHAT_ID` | Tu `.env` de la PC |
| `LLM_API_KEY` | Tu `.env` de la PC |
| Authtoken de ngrok y tu dominio fijo | dashboard.ngrok.com → *Your Authtoken* y *Domains* (cuenta gratis) |
| `labubot.db` | La PC, ya migrada (paso 4) |

---

## 1. Servidor base

Como `root` (o con el usuario que da el proveedor):

```bash
adduser labubot && usermod -aG sudo labubot
mkdir -p /home/labubot/.ssh && cp ~/.ssh/authorized_keys /home/labubot/.ssh/
chown -R labubot:labubot /home/labubot/.ssh && chmod 700 /home/labubot/.ssh
```

Probá desde la PC que `ssh labubot@<IP>` entra con la clave **antes** de cerrar la
contraseña. Después, como `labubot`:

```bash
# En sshd gana el primer valor leído: el 00- pisa al 50-cloud-init.conf.
printf 'PermitRootLogin no\nPasswordAuthentication no\n' | sudo tee /etc/ssh/sshd_config.d/00-labubot.conf
sudo systemctl restart ssh
sudo ufw allow OpenSSH && sudo ufw enable        # con ngrok no hace falta abrir nada más
sudo timedatectl set-timezone America/Argentina/Buenos_Aires
sudo apt update && sudo apt install -y git sqlite3
curl -LsSf https://astral.sh/uv/install.sh | sh && source "$HOME/.local/bin/env"
uv python install 3.14 && uv tool install poetry
poetry config virtualenvs.in-project true
```

Comprobá: `sudo sshd -T | grep -E "^(permitrootlogin|passwordauthentication) "`
→ `no` las dos; `timedatectl` → la zona de Argentina; `$(uv python find 3.14) -V`
→ `Python 3.14.x`.

## 2. Código

```bash
git clone <url del repo> ~/labubot && cd ~/labubot   # si es privado: una deploy key de solo lectura
git switch dev                                       # o la rama que tenga el multiusuario
poetry env use "$(uv python find 3.14)"
poetry install --only main
```

## 3. `.env`

```bash
cp .env.example .env && chmod 600 .env && nano .env
```

| Clave | Valor |
|---|---|
| `LOCATION`, `HOURS` | Como en la PC (`Argentina`, `24`) |
| `LLM_API_KEY` | La de OpenAI |
| `TELEGRAM_TOKEN` | El del bot **real** |
| `ADMIN_CHAT_ID` | Tu chat id |
| `WEBHOOK_URL` | `https://<nombre>.ngrok-free.dev/telegram/webhook` |
| `WEBHOOK_SECRET` | Uno nuevo: `.venv/bin/python -c "import secrets; print(secrets.token_hex(32))"` |
| `DB_PATH` | `labubot.db` |
| `LOG_LEVEL` | `INFO` |

`Settings` no acepta claves de más: si copiás un `.env` viejo, sacale
`TELEGRAM_CHAT_ID`. Comprobá:
`.venv/bin/python -c "from src.config.settings import settings; print(settings.webhook_url)"`.

## 4. La base

`labubot.db` se migra una sola vez, en la PC (`python migrate.py`, ver el README),
y se lleva al VPS. En la PC, con todo parado (daemon, uvicorn, túnel):

```bash
sqlite3 labubot.db ".backup corte.db"     # un solo archivo, con lo que quedaba en el -wal
scp corte.db labubot@<IP>:labubot/labubot.db
```

Si preferís arrancar de cero en el VPS: copiá `perfil.md` y `vistas.txt` a
`~/labubot` y corré `.venv/bin/python migrate.py` ahí. No lo corras dos veces una
vez que el bot está en uso: pisa el perfil del admin y le devuelve las listas que haya quitado.

Comprobá: `sqlite3 labubot.db "SELECT status, length(profile) FROM users"` →
`active|<caracteres de tu perfil>`.

## 5. api y worker

```bash
sudo tee /etc/systemd/system/labubot-api.service >/dev/null <<'EOF'
[Unit]
Description=labubot api: webhook de Telegram
After=network-online.target
Wants=network-online.target

[Service]
User=labubot
WorkingDirectory=/home/labubot/labubot
ExecStart=/home/labubot/labubot/.venv/bin/uvicorn api:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

sudo tee /etc/systemd/system/labubot-worker.service >/dev/null <<'EOF'
[Unit]
Description=labubot worker: corridas cada hora y con /start
After=network-online.target
Wants=network-online.target

[Service]
User=labubot
WorkingDirectory=/home/labubot/labubot
ExecStart=/home/labubot/labubot/.venv/bin/python daemon.py
Restart=always
RestartSec=30

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable --now labubot-api
```

`WorkingDirectory` importa: `labubot.db`, `logs/` y `resultados/` van por ruta
relativa.

Comprobá: `systemctl is-active labubot-api` → `active`;
`sudo ss -tlnp | grep 8000` → solo `127.0.0.1:8000`;
`curl -s -o /dev/null -w "%{http_code}\n" -X POST localhost:8000/telegram/webhook -H "Content-Type: application/json" -d "{}"`
→ `403` (sin el secreto).

El worker se arranca en el paso 8: al arrancar hace una corrida y manda mensajes.

## 6. Túnel ngrok

```bash
curl -sSL https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null
echo "deb https://ngrok-agent.s3.amazonaws.com bookworm main" | sudo tee /etc/apt/sources.list.d/ngrok.list
sudo apt update && sudo apt install -y ngrok

mkdir -p ~/.config/ngrok
tee ~/.config/ngrok/ngrok.yml >/dev/null <<'EOF'
version: 3
agent:
  authtoken: <AUTHTOKEN>
endpoints:
  - name: labubot
    url: https://<nombre>.ngrok-free.dev
    upstream:
      url: http://127.0.0.1:8000
EOF
chmod 600 ~/.config/ngrok/ngrok.yml && nano ~/.config/ngrok/ngrok.yml   # authtoken y dominio
ngrok config check --config ~/.config/ngrok/ngrok.yml

sudo tee /etc/systemd/system/labubot-ngrok.service >/dev/null <<'EOF'
[Unit]
Description=labubot túnel: ngrok con el dominio fijo hacia la api
After=network-online.target labubot-api.service
Wants=network-online.target

[Service]
User=labubot
ExecStart=ngrok start --all --config /home/labubot/.config/ngrok/ngrok.yml --log stdout
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
sudo systemctl daemon-reload && sudo systemctl enable --now labubot-ngrok
```

Comprobá: `journalctl -u labubot-ngrok -n 20` muestra el túnel arriba con tu
dominio, y desde la PC
`curl -s -o /dev/null -w "%{http_code}\n" -X POST https://<nombre>.ngrok-free.dev/telegram/webhook`
→ `403`: el pedido llegó a la api y la api lo rechazó por no traer el secreto.

## 7. Webhook

```bash
.venv/bin/python set_webhook.py
tail -n 3 logs/app.log      # "Webhook registrado en https://... y comandos publicados"
```

Comprobá en el navegador `https://api.telegram.org/bot<TOKEN>/getWebhookInfo`:
`url` = tu `WEBHOOK_URL`, `allowed_updates` = `["message","callback_query"]` y sin
`last_error_message`. Mandale `/start` al bot desde tu cuenta → "👋 ¡Volviste!…", y
`journalctl -u labubot-api -n 5` muestra `"POST /telegram/webhook HTTP/1.1" 200`.

Un bot tiene un solo webhook: desde acá el bot real atiende solo el VPS. Para
desarrollar en la PC, usá un bot de prueba (README).

## 8. Worker

**En la PC no tiene que quedar ningún `daemon.py` corriendo** (si no, las ofertas
llegan dos veces). Después:

```bash
sudo systemctl enable --now labubot-worker
tail -f logs/app.log        # "Arranca la corrida" … "Corrida terminada en X min"
```

Al terminar te llega un bloque por palabra y el resumen silencioso.

## 9. Backups y logs

Backup diario de la base, con 14 días de historia (`crontab -e` como `labubot`):

```cron
0 4 * * * mkdir -p /home/labubot/backups && sqlite3 /home/labubot/labubot/labubot.db ".backup /home/labubot/backups/labubot-$(date +\%F).db" && find /home/labubot/backups -name 'labubot-*.db' -mtime +14 -delete
```

`.backup` es seguro con la base en uso (un `cp` puede dejar afuera el `-wal`); en
cron el `%` va escapado. Cada tanto, bajá uno a la PC:
`scp labubot@<IP>:backups/labubot-<fecha>.db .`. El `.env` se guarda en un gestor
de contraseñas, no con los backups: la base tiene los CV de los usuarios.

Rotación semanal de `app.log`:

```bash
# copytruncate: los dos procesos tienen app.log abierto.
sudo tee /etc/logrotate.d/labubot >/dev/null <<'EOF'
/home/labubot/labubot/logs/app.log {
	weekly
	rotate 8
	compress
	missingok
	notifempty
	copytruncate
	su labubot labubot
}
EOF
sudo logrotate -f /etc/logrotate.d/labubot   # aparece logs/app.log.1.gz
```

Dónde mirar:

| Qué | Comando |
|---|---|
| La app (lo escriben api y worker) | `tail -f ~/labubot/logs/app.log` |
| Arranques, caídas y accesos de uvicorn | `journalctl -u labubot-api -u labubot-worker -f` |
| El túnel | `journalctl -u labubot-ngrok -f` |
| El webhook visto desde Telegram | `https://api.telegram.org/bot<TOKEN>/getWebhookInfo` |

## 10. Avatar

Ya está hecho: el nombre y la foto quedan en Telegram, no en el servidor, así que
mudarse al VPS no los cambia. Si hiciera falta de nuevo: @BotFather → `/setuserpic`
→ [`logo/labubot-640.png`](logo/labubot-640.png) como foto.

## 11. Prueba de reinicio

`sudo reboot`. Al volver, `systemctl is-active labubot-api labubot-worker labubot-ngrok`
→ `active` tres veces, `/start` contesta y el worker hace su corrida de arranque.

---

## Operación

**Actualizar el código:**

```bash
cd ~/labubot && git pull && poetry install --only main
sudo systemctl restart labubot-api labubot-worker
```

Reiniciar el worker corta la corrida en curso y arranca otra: no se pierde nada,
lo clasificado ya está en la base y lo no enviado sale en la próxima. Si cambiaron
los comandos del bot o la URL, `.venv/bin/python set_webhook.py` de nuevo
(descarta los updates que Telegram tenía en cola).

**Restaurar un backup:** `sudo systemctl stop labubot-api labubot-worker`, copiar
el backup como `labubot.db`, borrar `labubot.db-wal` y `labubot.db-shm` si
quedaron, y volver a arrancar.

**Borrar un usuario a mano:** `sqlite3 labubot.db "PRAGMA foreign_keys=ON; DELETE FROM users WHERE chat_id = <id>"`.
Sin el `PRAGMA` sus términos y entregas quedan huérfanos.

**Cortar el webhook:** `https://api.telegram.org/bot<TOKEN>/deleteWebhook`.

---

## Alternativa: dominio propio con Caddy

Con un dominio (uno propio, o un subdominio gratis de [DuckDNS](https://www.duckdns.org)
apuntando a la IP del VPS) se puede reemplazar ngrok por Caddy, que saca el
certificado de Let's Encrypt solo. Pide abrir el 80 y el 443 y no depende de un
tercero para el tráfico.

1. Registro `A` del dominio → IP del VPS (en Cloudflare, sin proxy).
2. `sudo ufw allow 80,443/tcp`.
3. Caddy desde su repo apt oficial (caddyserver.com/docs/install; el de Ubuntu es viejo).
4. `/etc/caddy/Caddyfile`, con tu dominio, y `sudo systemctl reload caddy`. Solo
   pasa `/telegram/webhook`; el resto contesta 404:

   ```caddy
   labubot.duckdns.org {
   	handle /telegram/webhook {
   		reverse_proxy 127.0.0.1:8000
   	}
   	handle {
   		respond 404
   	}
   }
   ```
5. `WEBHOOK_URL=https://<dominio>/telegram/webhook`, sin `labubot-ngrok`, y
   `set_webhook.py` como en el paso 7.
