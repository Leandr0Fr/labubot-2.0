# ¿Contabo Cloud VPS 4 para labubot? (octubre de 2026)

> **El proveedor todavía no está decidido.** Este documento evalúa un candidato
> (Contabo Cloud VPS 4) contra alternativas. Lo que vale para cualquier VPS es la
> sección 1 (qué necesita labubot), la 4 (el riesgo de la IP de datacenter) y el
> plan de prueba de la sección 7: se corre igual con el proveedor que sea.

> **Veredicto.**
> 1. Como máquina sirve, pero no es la más barata para lo que labubot usa. Es lo más barato con 4 vCPU y 8 GB, y labubot usa menos de 1 GB: los 8 GB sobran unas 8 veces. OVHcloud VPS-1 (2 vCPU, 4 GB, backup diario incluido) cuesta USD 5,35 sin compromiso, menos que Contabo a 1 mes (USD 6,60). Pagando 12 meses por adelantado cuesta USD 4,54, menos que Contabo a 24 meses (USD 5,28). A favor de Contabo queda la IP: en las dos fuentes que encontré, su red sale algo mejor que la de OVH (sección 4).
> 2. El riesgo no es el hardware sino la IP, y vale para cualquier VPS, no solo para Contabo: todos dan IP de datacenter. LinkedIn aporta el 62 % de las ofertas nuevas y el 56 % de las verdes y amarillas (20 al 31/10). No pasa por Cloudflare: tiene su propia defensa contra bots, que contesta 999. Otro ~18–19 % viene de 7 portales detrás de Cloudflare. Nadie publicó mediciones de LinkedIn contra IPs de Contabo.
> 3. No firmes 24 meses de entrada. Los USD 5,28 exigen 24 meses pagados juntos al contratar (USD 126,72): los términos cobran todo por adelantado a quien no vive en Alemania. Contratá 1 mes a USD 6,60 (sin cargo de setup), corré el plan de prueba de abajo y recién ahí decidí. Si falla, la alternativa es la PC de casa con cloudflared: IP residencial y el mismo código.

Datos consultados el 30 y 31/10/2026. Todo lo que no pude confirmar está marcado como **no confirmado**.

---

## 1. Qué necesita labubot

En la Fase 1 hay dos procesos (D5): `api` (FastAPI detrás de Caddy) y `worker` (daemon.py, que corre una vez por hora), los dos sobre un SQLite. No hay navegador.

| Pieza | Memoria | De dónde sale el número |
|---|---|---|
| worker (`main.py` importado: httpx, bs4, openai, pydantic-settings, schedule) | 59 MB en reposo; 100 MB de pico al parsear 4,7 MB de HTML con bs4 | **Medido** el 31/10/2026 con Python 3.14.6 en la PC (Windows, working set) |
| api (FastAPI 0.162 + uvicorn 0.54 + el router del webhook) | 53 MB | **Medido** el 31/10/2026 en un venv aparte, con una app mínima |
| Caddy | ~30–50 MB | Estimado, no medido |
| Ubuntu 24.04 + systemd + sshd | ~300–400 MB | Estimado, no medido |
| **Total** | **< 700 MB** | |

- **CPU.** La corrida pasa casi todo el tiempo esperando la red: reintentos de LinkedIn, pausas y las llamadas a OpenAI. Las corridas del 28/10 duraron entre 9,7 y 24,9 min (`logs/app.log`). Con 1 vCPU alcanza. El LLM corre en OpenAI, no en el VPS.
- **Disco.** La descripción promedio pesa 3,4 KB (4.180 ofertas en `resultados/`). Con 900 a 1.300 ofertas nuevas por día (885 el 28/10 y 1.275 el 21/10, en `resultados/`), la tabla `offers` crece hasta ~1,3 GB por año si nunca se purga. `deliveries` es chica: unos 100 bytes por fila. Cualquier disco de 25 GB o más alcanza.
- **Tráfico.** **No medido**: el Driver no loguea los GET a los portales. Casi todo es tráfico entrante, que ninguno de los candidatos cobra. Se mide con `vnstat` en la prueba.
- **Multiusuario.** Cada usuario agrega ~50 llamadas al LLM por hora (D4). Eso sale de la cuenta de OpenAI, no de la RAM: un perfil son ~8 KB de texto.

**Conclusión:** 1 GB queda justo, 2 GB es cómodo y 8 GB sobra. Igual, Cloud VPS 4 es el plan más chico de Contabo, así que ese es el precio mínimo de entrada.

---

## 2. Contabo Cloud VPS 4: lo que cuesta de verdad

Especificación: 4 vCPU, 8 GB de RAM, 100 GB de SSD, 1 snapshot, puerto de 200 Mbit/s, tráfico "Unlimited\*" y 1 IPv4.

| Plazo | USD/mes | Total del plazo | Fuente |
|---|---|---|---|
| 1, 3 o 6 meses | 6,60 | 6,60 por mes | Precio de lista en USD (JSON-LD de contabo.com/en-us/vps) |
| 12 meses (−15 %) | 5,61 | 67,32 | Calculado. El configurador muestra €4,68 (lista: €5,50) |
| 24 meses (−20 %) | **5,28** | **126,72** | El precio de tu captura. El configurador muestra €4,40 |

- **Qué es el precio tachado.** El sitio lo dice: *"The price displayed is the effective monthly rate for a 24-month subscription including applicable taxes"*. USD 6,60 es el precio mensual normal y USD 5,28 es el descuento por firmar 24 meses. No es una promoción que se pueda pagar mes a mes.
- **Cargo de setup.** Ninguno: el configurador dice "No Setup Fee" en todos los plazos.
- **Plazo mínimo y renovación.** *"Minimum initial contract length: 1 month \| Minimum following contract length: Equal to the initial contract length \| Minimum cancellation notice: None (pre-paid) or 4 weeks (post-paid)"*. Según los términos (cláusula 5.1), el contrato se renueva solo por un período igual al inicial, salvo baja con 4 semanas de aviso. Con 24 meses, eso es renovar por otros 24 meses pagados juntos. La ayuda de Contabo, en cambio, dice *"your contract will automatically renew on a monthly basis"*. **No confirmado** cuál de las dos vale para el plazo de 24 meses.
- **Baja y arrepentimiento.** La baja se pide en el panel y corta el servicio al final del período. Mientras no llegue esa fecha, se puede revocar desde el panel. Al dar de baja se borran los snapshots y los backups. La ayuda menciona una "revocation" dentro de los primeros 14 días para cuentas de particulares: hay que pedirla a soporte y aceptar perder los datos. **No confirmado** si devuelve el dinero ni si vale fuera de la UE. Si una renovación automática se cobró sin querer, hay 72 h para pedir el reintegro a soporte.
- **Precio después de los 24 meses.** **No confirmado.** El cartel dice "for the first 24 months" y no publica el precio siguiente. La cláusula 4.9 permite ajustar precios "in line with market developments", con derecho a rescindir. Conviene suponer que vuelve a la lista (USD 6,60) o más.
- **¿Se paga todo por adelantado?** Sí, para un cliente de Argentina. La cláusula 4.1 de los términos prevé cuotas mensuales para 3, 6 y 12 meses, pero cierra con *"If the customer's place of regular abode is located outside Germany, then payment for all the services of the Provider will fall due immediately"*. O sea: 12 meses son USD 67,32 y 24 meses son USD 126,72, en un solo pago al contratar. Dos comparativos lo confirman para los 24 meses: webhostingguide (15/10/2026: €105,60 al contratar) y affmaven (28/8/2026: el pedido dice "Prepaid 24 Months"). Ojo: un artículo de ayuda de Contabo dice *"it's only possible to pay for your services on a monthly basis"*. Contradice a los términos; el checkout lo va a mostrar.
- **Cambiar de plazo después.** La ayuda de Contabo dice que un servidor ya contratado se renueva por *"1 month, 3 months, 6 months or 12 months"*, hasta 18 meses por adelantado. El plazo de 24 meses no figura entre las renovaciones, y el artículo no dice si la renovación de 12 meses lleva el 15 %.
- **Ubicaciones y recargo mensual.** Así lo muestra el configurador, en EUR. El equivalente en USD es aproximado, con la misma relación que la lista de Contabo (6,60 / 5,50 = 1,2):

  | Región | Recargo |
  |---|---|
  | Unión Europea (el configurador no dice el sitio; el benchmark de abajo salió de Lauterbourg, Francia) | sin recargo |
  | Reino Unido | €1,05 (≈ USD 1,26) |
  | EE. UU. Central (St. Louis) | €1,05 (≈ USD 1,26) |
  | EE. UU. Este (Nueva York) | €1,55 (≈ USD 1,86) |
  | EE. UU. Oeste (Seattle) | €1,30 (≈ USD 1,56) |
  | Japón | €2,55 |
  | India | €2,40 |
  | Australia | €2,15 |
  | Singapur | sin stock |

  No hay datacenter en Sudamérica. **No confirmado** si el recargo entra en el descuento por plazo.
- **Tráfico "ilimitado\*".** El asterisco dice: *"Incoming Traffic: Unlimited and unmetered. No extra charges apply. \| Outgoing Traffic: Unlimited — fair usage policy applies based on average server workloads. To maintain fair network performance for all customers, Contabo reserves the right to throttle servers with exceptionally high or disruptive usage patterns."* Labubot casi solo baja datos, así que no lo afecta.
- **Backups.** No están incluidos. Auto Backup cuesta €1,65 por mes y el snapshot incluido es uno solo.
- **Alta.** En el primer pedido Contabo puede pedir verificación de identidad (documento o factura de servicio), y eso puede demorar el alta.
- **Impuestos para Argentina.**
  - Contabo no le cobra IVA a Argentina: su selector de país la muestra sin %, mientras que los países de la UE muestran el suyo.
  - **Percepción del 30 %:** ARCA la dejó de aplicar desde el 2/1/2026 a los pagos con tarjeta en moneda extranjera y a proveedores del exterior, salvo servicios turísticos pagados en pesos. Lo dicen Diario Popular, Comercio y Justicia y El Liberal (2/1/2026) e Info Viajera (diciembre de 2025). Solo una nota de Perfil (12/1/2026) la sigue mencionando. **No encontré el número de la norma** ni lo confirmé contra el Boletín Oficial.
  - **IVA 21 % (RG 4240):** lo percibe el banco si identifica un servicio digital del exterior. **No confirmé** si Contabo figura en el listado de ARCA.
  - **Ingresos Brutos:** algunas provincias suman una percepción sobre servicios digitales (impuestito.org habla de ~2 %, según la provincia). **No confirmado** para Contabo ni para tu provincia.
  - Peor caso, sin IIBB: USD 6,60 × 1,21 = **USD 7,99 por mes** (1 mes) o USD 5,28 × 1,21 = **USD 6,39** (24 meses). Con un 2 % de IIBB: USD 8,12 o USD 6,49.
- **Diferencia real entre 1 y 24 meses:** USD 1,32 por mes, o sea USD 31,68 en los dos años. Es poco a cambio de no quedar atado si la IP no sirve.

---

## 3. Rendimiento y soporte

| Dato | Valor | Fuente y fecha |
|---|---|---|
| Geekbench 6, Cloud VPS 4 | 1.012 single / 1.557 multi (4 vCPU AMD EPYC) | VPSBenchmarks, 25/10/2026, Lauterbourg (FR) |
| fio, Cloud VPS 4 | 4k: 63,8 MB/s (~16k IOPS) · 64k: 377 MB/s | ídem |
| iperf3, Cloud VPS 4 | 52–193 Mbit/s según el destino | ídem |
| Geekbench 6, Cloud VPS 10 (4c/8 GB, plan anterior) | 841 / 2.275 · fio 64k ≈ 1,1 GB/s · São Paulo a 211 ms | VPSBenchmarks, 9/9/2026 |
| Trustpilot | 4,6/5 con 11.620 reseñas; 11 % de 1 estrella. Las quejas de octubre de 2026 hablan de caídas de 48 h o más y respuestas automáticas | Trustpilot, consultado el 31/10/2026 |
| Soporte | Solo por ticket, sin chat. "Non-emergency response times average 24–48 hours" | opsforgelabs, 30/4/2026 (basado en reportes de usuarios) |

- **CPU sobrevendida.** Con 4 vCPU, un multi-core de solo 1,5 veces el single-core (1.557 contra 1.012) sugiere núcleos compartidos y con contención. El Cloud VPS 10 de septiembre, también con 4 vCPU, dio 2,7 veces (2.275 contra 841). Es una sola medición por plan, así que puede ser mala suerte con el host. Las reseñas coinciden en que hay "steal" en horas pico, pero no encontré mediciones de steal con fecha: los números que circulan son anécdotas.
- **Para labubot da igual.** Ni la CPU ni el disco son el cuello de botella. Sí importa la disponibilidad: si el VPS se cae, Telegram guarda los updates del webhook hasta 24 h (*"they will not be kept longer than 24 hours"*). Una caída de 48 h como las de Trustpilot pierde mensajes de usuarios, y se saltean corridas.

---

## 4. La IP: el riesgo que decide

**Qué hay delante de cada portal.** Revisé los headers de respuesta con curl desde la PC el 31/10/2026 (`server`, `cf-ray`, `via`, `x-li-pop`):

| Detrás de Cloudflare | Otro |
|---|---|
| Indeed (`apis.indeed.com`), Bumeran, GetOnBoard, Himalayas, Jobicy, WeWorkRemotely, Workable (y ZonaJobs) | **LinkedIn (borde propio: `server: Play`, `x-li-pop: gcp-…`, `via: 1.1 google`; sin `cf-ray`)**, Talent (CloudFront), Computrabajo (sin CDN visible), EmpleosIT (Apache) |

En la corrida del 30/10 de las 17 h, los 7 portales con Cloudflare aportaron 136 de las 725 ofertas listadas (19 %). LinkedIn solo aportó 439 (61 %; en la de las 16 h, 433 de 682, el 63 %). Contando las ofertas nuevas de `resultados/` del 20 al 31/10 (3.023), LinkedIn es el 62 % y los portales con Cloudflare el 18 %. De las verdes y amarillas (195), LinkedIn es el 56 %. Dato curioso: `ar.indeed.com` ya devuelve 403 desde casa, pero labubot no la usa: busca por la API GraphQL de la app.

**Lo que se sabe:**
- **La red de Contabo no sale peor que las alternativas.** Hay dos fuentes:
  - WaysCloud, consultado el 31/10/2026, califica AS51167 (Contabo) con riesgo **HIGH**: 45.265 IPs maliciosas y 804.781 reportes. Vultr (AS20473) también es HIGH. Peor, con **CRITICAL** ("top 1 %"), figuran DigitalOcean (AS14061), Hetzner (AS24940), OVH (AS16276) y Oracle (AS31898).
  - El estudio de dev.to (2/10/2026) tomó 30 IPs por proveedor de los rangos que anuncia cada ASN. Contabo dio **0 de 30 en listas negras, la más limpia de los 12 proveedores**. OVH dio 3 de 30; Hetzner y Vultr, 2 de 30; DigitalOcean, 1 de 30.
  - El problema no es Contabo: es ser una IP de datacenter.
- **Cloudflare no mira solo las listas negras.** Pesa el ASN y el DNS reverso. En el mismo estudio de dev.to, una IP limpia igual recibió el desafío de Cloudflare en ChatGPT. Eso pesa en el ~19 % que pasa por Cloudflare, no en LinkedIn.
- **Caso concreto con Contabo.** Desde un VPS de Contabo en Frankfurt, `curl` a `claude.ai` devolvía el desafío de Cloudflare, mientras que `api.anthropic.com` respondía (issue anthropics/claude-code#36201, 19/3/2026). Es una sola IP y un cliente sin JavaScript. Muestra que un mismo cliente puede pasar en un sitio con Cloudflare y no en otro. No prueba que toda la red de Contabo esté bloqueada.
- **LinkedIn guest:**
  - Un scraper público anotó: *"On 2026-10-17 one page per command worked from a datacenter IP, while several companies in one command got HTTP 999"*.
  - JobSpy: *"LinkedIn rate limits bursts of requests with a 429, which clears within about a minute"*.
  - Las guías que venden proxies residenciales dicen que LinkedIn bloquea los rangos de datacenter. Son fuentes interesadas y no las pude verificar.
  - Desde casa, labubot ya ve entre 11 % y 18 % de 429, todos recuperados con reintentos (pruebas del 18/10/2026).
  - **Ojo:** en LinkedIn, `_get` reintenta cualquier `LabubotError` (10 intentos, 3 s entre uno y otro), así que un 999 o un 403 también se reintentan. Si es un bloqueo y no un 429 suelto, cada pedido gasta ~27 s antes de cortar la búsqueda de ese término, y la corrida se alarga mucho. En los demás portales, el primer error corta la búsqueda.
- **Indeed.** Un análisis del 27/10/2026 dice *"Datacenter IPs fail every time"*, pero habla de las páginas web. JobSpy, que usa la misma API de la app que labubot, dice *"Indeed is the best scraper currently with no rate limiting"*. **No confirmado** desde Contabo.

**Lo que no se sabe:** no encontré a nadie que haya medido Contabo contra otro proveedor frente a LinkedIn o Indeed. La única manera de saberlo es la prueba de la sección 7.

---

## 5. Tabla comparativa

Precios sin impuestos argentinos. Donde el proveedor no publica el precio en USD, convertí EUR a USD a 1,15, la misma conversión que usa el comparativo de dev.to (23/10/2026). La columna de IP da la calificación de WaysCloud para el ASN (31/10/2026) y las IPs en listas negras según dev.to (2/10/2026, 30 por proveedor).

| Opción | vCPU / RAM / disco | USD/mes | Compromiso | Tráfico | IP para scraping | ¿Disponible hoy? | Comentario |
|---|---|---|---|---|---|---|---|
| **Contabo Cloud VPS 4** (UE) | 4 / 8 GB / 100 GB SSD | 6,60 (1 mes) · 5,61 (12 meses) · 5,28 (24 meses), todo por adelantado | 1 a 24 meses, renovación automática | Ilimitado con *fair use*, 200 Mbit/s | Datacenter · AS51167 HIGH · 0/30 | Sí (Singapur sin stock) | Lo que más RAM da por dólar; soporte lento; CPU con contención; backup aparte (€1,65) |
| **OVHcloud VPS-1** (gama 2027) | 2 / 4 GB / 40 GB NVMe | **5,35** (sin compromiso) · 5,08 (6 meses) · 4,54 (12 meses), por adelantado | Mensual o 6/12 meses | Ilimitado, 500 Mbit/s (cuota en Asia-Pacífico) | Datacenter · AS16276 CRITICAL · 3/30 | Figura en el catálogo; stock **no confirmado** en el checkout | Sin cargo de instalación; backup diario incluido; UE, Canadá, Singapur, Sídney y Mumbai; sin Sudamérica |
| **Hetzner CX23** | 2 / 4 GB / 40 GB | €5,99 (USD 7,09) | Por hora | 20 TB | Datacenter · AS24940 CRITICAL · 2/30 | **No**: toda la línea Cost-Optimized (CX y CAX) dice "currently unavailable" (página del 31/10/2026) | Subió dos veces en 2026 (1/4 y 15/6) |
| **Hetzner CPX02** (nuevo, 6/10/2026) | 1 / 1 GB / 20 GB NVMe | €6,49 (USD 8,09 con IPv4) | Por hora | 20 TB (UE) | Ídem Hetzner | **No**, según la web: el 12/10 y el 31/10 figuraba "currently unavailable", y desde el 26/6/2026 Hetzner restringe crear servidores a cuentas nuevas (incidente todavía abierto el 31/10) | El más barato de Hetzner, si te dejan crearlo |
| **Hetzner CPX12** | 1 / 2 GB / 40 GB NVMe | €11,99 (USD 14,09) | Por hora | 20 TB (UE) | Ídem Hetzner | **No**, por lo mismo que el CPX02 | El doble que Contabo por un cuarto de RAM |
| **Oracle Cloud Always Free** | Ampere A1: 2 OCPU / 12 GB (o 2 × E2.1.Micro de 1/8 OCPU y 1 GB) | 0 | Ninguno | 10 TB | Datacenter · AS31898 CRITICAL · 2/30 | A veces: "out of host capacity" es común | Lo recortaron a la mitad en junio de 2026. Reclama instancias con CPU, red y memoria por debajo del 20 % durante 7 días, y labubot cumple las tres: riesgo real de que lo apaguen |
| **DigitalOcean Basic** | 1 / 1 GB / 25 GB (o 512 MB a USD 4) | 6,00 | Por segundo (desde el 1/1/2026) | 1.000 GB | Datacenter · AS14061 CRITICAL · 1/30 | Sí | Sin región en Sudamérica |
| **Vultr Regular** | 1 / 1 GB / 25 GB | 5,00 (São Paulo × 1,5 = 7,50) | Por hora | 1 TB (+2 TB por cuenta) | Datacenter · AS20473 HIGH · 2/30 | Sí; tiene São Paulo, Santiago y México | El servidor detenido se sigue cobrando |
| **PC de casa + cloudflared** | La que ya tenés | 0 extra + luz (**no calculado**: W × 0,72 = kWh/mes; 60 W ≈ 43 kWh) | Ninguno | El de tu ISP | **Residencial: la misma con la que hoy anda todo** | Sí | Depende de que la PC esté prendida (Telegram guarda los updates 24 h). El túnel con nombre necesita el dominio en Cloudflare; los Quick Tunnels (`trycloudflare.com`) son solo para pruebas: "no uptime guarantee" |

**En limpio:**
- Para el hardware que pide labubot (1–2 GB), DigitalOcean y Vultr cuestan lo mismo que Contabo a 1 mes, con facturación por hora y sin compromiso, pero con la octava parte de RAM.
- OVHcloud VPS-1 es más barato que Contabo en cualquier plazo comparable, con 4 GB (sobra) y backup diario incluido. En contra: su ASN figura peor en las dos fuentes de reputación.
- Contabo gana en recursos y, por poco, en reputación de la red; en precio para lo que labubot usa, no gana.
- Hetzner, la alternativa de siempre, hoy no es realista para una cuenta nueva: lo barato está sin stock y su página de estado dice *"we are currently required to restrict the creation of new cloud servers for both new customers and some of our existing customers"*.
- Los seis proveedores de VPS dan IPs de datacenter. Solo la PC de casa evita el riesgo de la IP. Una prueba que pasa en un proveedor no vale para otro: es otro ASN.

---

## 6. Riesgos

| Riesgo | Probabilidad | Impacto | Qué hacer |
|---|---|---|---|
| LinkedIn o Indeed tiran 429/999/403 sostenidos desde la IP de Contabo | **No confirmada; es la gran incógnita** | Alto: LinkedIn es ~60 % del volumen | Plan de prueba (sección 7) antes de firmar plazo largo |
| Quedar atado 24 meses con una IP que no sirve | Evitable | USD 126,72, pagados al contratar | Arrancar con 1 mes |
| Renovación automática sin querer (los términos dicen "por el mismo plazo") | Media si nadie se acuerda | 1 mes: USD 6,60. 24 meses: hasta otros 24 meses pagados juntos | Pedir la baja apenas se contrata (el servidor sigue hasta el fin del plazo) y revocarla si conviene quedarse; si igual se renueva, hay 72 h para el reintegro |
| El precio sube después de los 24 meses o por la cláusula 4.9 | Media | Bajo (son pocos dólares) | Hay derecho a rescindir si suben el precio |
| Caídas largas con soporte lento (24–48 h por ticket) | Baja/media según Trustpilot | Alto si dura más de 24 h: se pierden updates de Telegram | Backup diario de `labubot.db` (`sqlite3 labubot.db ".backup ..."`) copiado fuera del VPS, para poder mudarse rápido |
| Sin backups incluidos (y la baja borra snapshots y backups) | Segura | Perder `labubot.db` (usuarios, perfiles, deliveries) | Lo mismo de arriba, o Auto Backup (€1,65/mes) |
| La verificación de identidad demora el alta | Media en el primer pedido | Días | Contratar con tiempo |
| Geolocalización: IP de Europa o EE. UU. pidiendo portales `.com.ar` | **No confirmada** | Resultados distintos o bloqueo regional | La prueba compara la cantidad de ofertas por portal |
| VPS expuesto a internet | Segura | Intrusión | Solo claves SSH, `ufw` con 22/80/443 y actualizaciones automáticas. Uvicorn escucha en 127.0.0.1 (D1) |
| *Fair use* de tráfico | Muy baja | Throttling | Nada: labubot casi solo baja datos |

---

## 7. Plan de prueba antes de comprometerse

**Objetivo:** saber si desde la IP del VPS labubot trae lo mismo que desde casa. Se compara la misma búsqueda, a la misma hora, desde las dos IPs.

### 0. (Opcional, cuesta centavos) Probar una IP de datacenter cualquiera
Levantá un droplet de DigitalOcean o un Vultr de 1 GB por 2–3 horas (se factura por segundo u hora) y corré la prueba A. Si LinkedIn o Indeed ya fallan ahí, es una señal fuerte en contra de cualquier VPS. Si andan, no prueba nada sobre Contabo, porque la ASN es otra: seguí al paso 1.

### 1. Contratar Contabo a prueba
- Cloud VPS 4, región **Unión Europea** (sin recargo), plazo **1 mes** (USD 6,60, sin setup), Ubuntu 24.04.
- El contrato se renueva solo. Lo más simple es pedir la baja en el panel apenas está andando: el servidor sigue hasta el fin del mes. Si la prueba pasa, revocás la baja antes de esa fecha (ayuda de Contabo).
- El mismo servidor después solo se renueva por 1, 3, 6 o 12 meses (ayuda de Contabo), y **no está confirmado** que esa renovación lleve descuento. Para tener los USD 5,28 de 24 meses hay que contratar un servidor nuevo y mudar `labubot.db` y `.env` (unos minutos). Ojo: el servidor nuevo trae **otra IP**, así que la prueba vale para la red de Contabo, no para esa IP puntual.

### 2. Preparar el VPS y la PC
```bash
# VPS
sudo apt update && sudo apt install -y git vnstat sqlite3
curl -LsSf https://astral.sh/uv/install.sh | sh        # uv trae Python 3.14 sin deadsnakes
source "$HOME/.local/bin/env"                          # suma uv (y después poetry) al PATH de esta sesión
uv python install 3.14 && uv tool install poetry
git clone <repo> ~/labubot && cd ~/labubot
poetry config virtualenvs.in-project true              # el venv queda en ~/labubot/.venv
poetry env use "$(uv python find 3.14)" && poetry install
cp .env.example .env    # LLM_API_KEY y TELEGRAM_* solo hacen falta para la prueba B
```
En la PC, cloná el repo **en otra carpeta**, con su propio `poetry install` y su `.env`, para que el log de la prueba quede separado del de todos los días.

El paso a paso con su aceptación está en [`tareas.md`](tareas.md), T0.2 y T0.3: ahí la carpeta de la PC es un `git worktree` de `dev` que usa el `.venv` del repo, y el `.env` de las dos máquinas sale del respaldo de T0.1 con el token del bot de prueba.

En las dos máquinas, poné `LOG_LEVEL=DEBUG` en `.env`: así quedan en el log los reintentos de LinkedIn (`Reintento tras: ...`).

Que la prueba no coincida con la corrida horaria del daemon de la PC, o pausalo mientras dura. Dos scrapes a la vez desde casa inflan los 429 del lado de la PC y la comparación sale a favor del VPS.

### 3. Prueba A: solo búsqueda, sin OpenAI ni Telegram
Script descartable `prueba_ip.py`: va en la raíz del clon y **no se commitea**. Recorre los mismos portales y términos que `main.py` y pide la descripción de las primeras 20 ofertas de cada portal. Solo 5 portales salen a buscarla por HTTP: LinkedIn, Computrabajo, Talent, Bumeran y EmpleosIT. Los otros 6 devuelven la que ya trajo la búsqueda. Está escrito contra el código del commit `ac57dfd`: si ya hiciste la F1 (`TERMS` pasa a llamarse `DEFAULT_TERMS`), cambiá el import.

```python
"""Prueba de IP: busca en los 11 portales y baja una muestra de descripciones."""

import logging
import time

from src.config.search import TERMS
from src.driver.http import Driver
from src.portals.bumeran import Bumeran
from src.portals.computrabajo import Computrabajo
from src.portals.empleosit import EmpleosIT
from src.portals.getonbrd import GetOnBoard
from src.portals.himalayas import Himalayas
from src.portals.indeed import Indeed
from src.portals.jobicy import Jobicy
from src.portals.linkedin import LinkedIn
from src.portals.talent import Talent
from src.portals.weworkremotely import WeWorkRemotely
from src.portals.workable import Workable

SAMPLE = 20

logger = logging.getLogger("prueba_ip")


def check(portal, jobs: dict[str, str], start: float) -> None:
    """
    Baja la descripción de las primeras SAMPLE ofertas y deja el resumen en el log.
    Args:
        portal: El portal que buscó (6 de los 11 guardan ahí las descripciones).
        jobs: {url: título} que devolvió la búsqueda.
        start: time.monotonic() de cuando arrancó ese portal.
    """
    urls = list(jobs)[:SAMPLE]
    described = 0
    for url in urls:
        if portal.description(url):
            described += 1
    seconds = time.monotonic() - start
    logger.info(
        f"{type(portal).__name__}: {len(jobs)} ofertas, "
        f"{described}/{len(urls)} con descripción, {seconds:.0f} s"
    )


def main() -> None:
    driver = Driver()
    for portal in (
        LinkedIn(driver),
        Computrabajo(driver),
        GetOnBoard(driver),
        Himalayas(driver),
        Talent(driver),
    ):
        start = time.monotonic()
        jobs: dict[str, str] = {}
        for term in TERMS:
            jobs.update(portal.search(term))
        check(portal, jobs, start)

    quoted_terms = []
    for term in TERMS:
        quoted = term
        if " " in term:
            quoted = f'"{term}"'
        quoted_terms.append(quoted)
    any_term = " OR ".join(quoted_terms)
    for portal in (Indeed(driver), Workable(driver)):
        start = time.monotonic()
        check(portal, portal.search(any_term), start)

    for portal in (
        Bumeran(driver),
        EmpleosIT(driver),
        Jobicy(driver),
        WeWorkRemotely(driver),
    ):
        start = time.monotonic()
        check(portal, portal.search(), start)
    driver.close()


if __name__ == "__main__":
    main()
```

**Cómo correrla:**
1. **Comparación cabeza a cabeza.** Lanzala en la PC y en el VPS al mismo tiempo (`python prueba_ip.py`), tres veces por día (mañana, tarde y noche) durante 2 días. Que sea a la misma hora importa: las ofertas cambian de hora en hora.
2. **Desgaste en 24 h.** En el VPS, dejala una vez por hora durante 24 h, como lo haría el worker: `crontab -e` → `0 * * * * cd ~/labubot && .venv/bin/python prueba_ip.py`. Así se ve si LinkedIn se pone más duro con el volumen acumulado.

**Qué mirar (en cada máquina):**
```bash
grep "prueba_ip" logs/app.log                          # ofertas y descripciones por portal
grep -oE "Reintento tras: Respondió [0-9]+" logs/app.log | sort | uniq -c  # reintentos de LinkedIn por status
grep -E "cortada|Sin descripción|salteado" logs/app.log | wc -l  # búsquedas, feeds o detalles que fallaron
grep -oE "Respondió (403|429|999|5..)" logs/app.log | sort | uniq -c
vnstat -d; free -m                                     # tráfico del día y RAM (en el VPS)
top                                                    # columna %st: CPU robada por vecinos
```

### 4. Criterio de aceptación (propuesto; ajustalo vos)
- **LinkedIn e Indeed:** en el VPS, al menos el 90 % de las ofertas que trae la PC en la misma corrida, en todas las repeticiones. Lo mismo durante las 24 corridas horarias, sin una tendencia a la baja.
- **Ningún portal** con 403 o 999 sostenidos (más de 3 seguidos sobre la misma búsqueda).
- **Descripciones:** al menos 18 de 20 en cada portal donde la PC también las trae. Solo mide algo en los 5 que piden el detalle aparte: en los otros 6, si la búsqueda anduvo, da 20 de 20.
- **Reintentos de LinkedIn** (`Reintento tras`) que no superen el doble de los de la PC, y que sean 429 y no 403 o 999.
- **Duración por portal** (los segundos del log de `prueba_ip`) que no supere el doble de la de la PC: la corrida tiene que entrar holgada en la hora.
- **Portales chicos** (Jobicy, WeWorkRemotely y GetOnBoard traen 3 a 4 ofertas cada uno): que falle alguno es tolerable, pero anotalo.

### 5. Prueba B: una corrida completa
Con la prueba A aprobada, corré `python main.py` una sola vez en el VPS:
- Usá **un bot y un chat de prueba**: creá otro bot con @BotFather y poné su `TELEGRAM_TOKEN` y `TELEGRAM_CHAT_ID` en el `.env` del VPS.
- Copiá de la PC `perfil.md` y `vistas.txt`: los dos están en `.gitignore`, así que el clon no los trae. Sin `perfil.md`, `main.py` busca en todos los portales y recién después falla al leerlo. Con `vistas.txt`, solo clasifica lo nuevo (~50 llamadas al LLM, como una corrida horaria).

Esto valida que desde el VPS salen bien las llamadas a `api.openai.com` y a `api.telegram.org`, y que los tiempos son razonables. `api.openai.com` también está detrás de Cloudflare; `api.telegram.org` no (nginx propio, revisado el 31/10/2026).

### 6. Decidir
- **Pasa:** migrar (F4) y recién ahí pasar a 12 o 24 meses: renovando el mismo servidor por 12, o con uno nuevo a 24 (ver paso 1). Lo que pasó en Contabo no vale para OVH ni para otro proveedor: si preferís uno más barato, hay que repetir la prueba ahí.
- **No pasa por LinkedIn o Indeed:** dar de baja Contabo y correr labubot en la PC de casa con un túnel cloudflared con nombre. Es el mismo código (D1): solo cambia dónde corre uvicorn. Opcional: dejar en el VPS solo la `api` (bot y panel) y scrapear desde casa. Eso suma una pieza: dos máquinas escribiendo el mismo SQLite no anda, así que habría que pensarlo aparte.
- **Pasa a medias** (por ejemplo, solo fallan portales chicos): aceptable. Anotá cuáles fallan para que no sorprenda después.

---

## 8. Lo que no pude confirmar
- El pago de los 24 meses todo junto. Los términos (cláusula 4.1, clientes fuera de Alemania) y dos comparativos dicen que se paga al contratar, pero un artículo de ayuda dice que solo se paga mes a mes. Hay que verlo en el checkout.
- Si un contrato de 24 meses se renueva solo por otros 24 meses (cláusula 5.1) o mes a mes (ayuda de Contabo).
- Si la "revocation" de 14 días devuelve el dinero y si vale para un particular de Argentina.
- El precio de Contabo después de los 24 meses, y si renovar un servidor ya contratado por 12 meses lleva el 15 %.
- Si Hetzner deja crear un CPX02 o un CPX12 a una cuenta nueva desde Argentina hoy (la restricción es por cuenta y por ubicación).
- Si OVHcloud tiene stock de VPS-1 y si cobra recargo por región: el precio sale de su catálogo público, no de un checkout.
- Si el recargo por región de Contabo entra en el descuento por plazo, y los recargos exactos en USD: el configurador me los mostró en EUR.
- Si Contabo figura en el listado de servicios digitales de ARCA (IVA 21 %). Tampoco el número de la norma que eliminó el 30 %: cuatro notas de diciembre de 2025 y enero de 2026 dicen que se eliminó; solo Perfil (12/1/2026) lo sigue mencionando.
- Cómo responden LinkedIn, Indeed y los demás portales con Cloudflare a una IP de Contabo en particular. No hay mediciones públicas: por eso existe el plan de prueba.
- El tráfico mensual de labubot y el consumo eléctrico de la PC de casa.
- Si una cuenta de Oracle pasada a pago por uso (Pay As You Go) se libra del reclamo por inactividad.

---

## Fuentes

| Fuente | Qué se tomó | Fecha |
|---|---|---|
| [Contabo, Cloud VPS (en-us)](https://contabo.com/en-us/vps/) | Lista USD 6,60 (JSON-LD), "for the first 24 months", plazo mínimo, aviso de baja, texto del asterisco de tráfico, selector de país con impuestos | consultado 30/10/2026 |
| [Contabo, configurador Cloud VPS 4](https://contabo.com/en-us/vps/cloud-vps-core-4/) | Plazos y descuentos (15 % y 20 %), "No Setup Fee", recargos por región, Auto Backup €1,65, Singapur sin stock | consultado 31/10/2026 |
| [Contabo, Terms & Conditions](https://contabo.com/en/legal/terms-and-conditions/) | Cláusulas 4.1 (cuotas; fuera de Alemania, todo al contratar), 4.9 (precios), 5.1 (renovación por el mismo plazo, aviso de 4 semanas), 9 (usos prohibidos), 11.2 (ancho de banda) | consultado 31/10/2026 |
| [Contabo Help, renovación](https://help.contabo.com/en/support/solutions/articles/103000331711-can-i-renew-my-subscription-for-a-different-period-of-time-) | Renovación por 1, 3, 6 o 12 meses; hasta 18 meses por adelantado | consultado 31/10/2026 |
| [Contabo Help, período de facturación](https://help.contabo.com/en/support/solutions/articles/103000366085-can-i-change-my-billing-period-) | "only possible to pay for your services on a monthly basis" (contradice a la cláusula 4.1) | consultado 31/10/2026 |
| [Contabo Help, renovación automática](https://help.contabo.com/en/support/solutions/articles/103000327506-my-service-was-automatically-renewed-can-i-cancel-it-) | "automatically renew on a monthly basis"; reintegro pidiéndolo dentro de las 72 h | consultado 31/10/2026 |
| [Contabo Help, baja](https://help.contabo.com/en/support/solutions/articles/103000269314-how-can-i-close-my-contabo-account-or-cancel-a-contabo-service-) y [revocación](https://help.contabo.com/en/support/solutions/articles/103000280031-can-i-cancel-or-revoke-my-new-contabo-product-) | La baja borra snapshots y backups; revocar la baja antes de la fecha; "revocation" en 14 días para particulares | consultado 31/10/2026 |
| [affmaven, Contabo coupon](https://affmaven.com/contabo-coupon/) | USD 6,60 / 5,28; el pedido de 24 meses figura como "Prepaid 24 Months" | actualizado 28/8/2026 |
| [Contabo Help, verificación](https://help.contabo.com/en/support/solutions/articles/103000348466-why-do-i-need-to-verify-my-purchase-) | Verificación de identidad en los pedidos | consultado 31/10/2026 |
| [webhostingguide.net, Contabo vs Hetzner](https://webhostingguide.net/vps/contabo-vs-hetzner/) | 24 meses prepagos (€105,60); renovación sin documentar | 15/10/2026 |
| [VPSBenchmarks, Contabo Cloud VPS 4](https://www.vpsbenchmarks.com/yabs/contabo-4c-8gb-20261025-8b52c3) | Geekbench 6, fio, iperf3 | 25/10/2026 |
| [VPSBenchmarks, Contabo Cloud VPS 10](https://www.vpsbenchmarks.com/yabs/contabo-4c-8gb-20260909-15add6) | Geekbench 6, fio, latencia a São Paulo | 9/9/2026 |
| [Trustpilot, Contabo](https://www.trustpilot.com/review/contabo.com) | 4,6/5, 11.620 reseñas, quejas de octubre de 2026 | consultado 31/10/2026 |
| [OpsForge Labs, Contabo VPS Review](https://opsforgelabs.com/reviews/contabo-vps-review/) | Soporte por ticket, 24–48 h | 30/4/2026 |
| WaysCloud: [AS51167 Contabo](https://ip.wayscloud.services/asn-intelligence/51167), [AS16276 OVH](https://ip.wayscloud.services/asn-intelligence/16276), [AS24940 Hetzner](https://ip.wayscloud.services/asn-intelligence/24940), [AS14061 DigitalOcean](https://ip.wayscloud.services/asn-intelligence/14061), [AS20473 Vultr](https://ip.wayscloud.services/asn-intelligence/20473), [AS31898 Oracle](https://ip.wayscloud.services/asn-intelligence/31898) | Riesgo HIGH (Contabo, Vultr) o CRITICAL (el resto), IPs maliciosas, reportes | consultado 31/10/2026 |
| [anthropics/claude-code#36201](https://github.com/anthropics/claude-code/issues/36201) | Desafío de Cloudflare a `curl` desde un VPS de Contabo | 19/3/2026 |
| [dev.to, "Your VPS IP is not on any blocklist…"](https://dev.to/mazijuacc/your-vps-ip-is-not-on-any-blocklist-chatgpt-still-blocks-it-ekl) | Cloudflare pesa el ASN y el PTR además de las listas negras; 30 IPs por proveedor en listas negras (Contabo 0/30, OVH 3/30, Hetzner 2/30, Vultr 2/30, Oracle 2/30, DigitalOcean 1/30) | 2/10/2026 |
| [OVHcloud, VPS](https://us.ovhcloud.com/vps/) y catálogo público (`ca.api.ovh.com/1.0/order/catalog/public/vps?ovhSubsidiary=WE`) | VPS-1 2027: 2 vCores, 4 GB, 40 GB NVMe, backup diario; USD 5,35 sin compromiso, 5,08 (6 meses), 4,54 (12 meses); instalación 0; centros de datos | consultado 31/10/2026 |
| [OVHcloud blog, VPS 2027](https://blog.ovhcloud.com/en/posts/vps-2027/) | Nueva gama con VPS-1 de entrada | 17/6/2026 |
| [toolzerhub/linkedin-scraper](https://github.com/toolzerhub/linkedin-scraper) | LinkedIn guest desde IP de datacenter: 1 página sí, varias → 999 | nota del 17/10/2026 |
| [JobSpy (README)](https://github.com/speedyapply/JobSpy) | 429 de LinkedIn; Indeed sin rate limit | consultado 31/10/2026 |
| [WebScraping.AI, Indeed 2026](https://webscraping.ai/blog/how-to-scrape-indeed) | "Datacenter IPs fail every time" (páginas web) | 27/10/2026 |
| [Hetzner, Cost-Optimized](https://www.hetzner.com/cloud/cost-optimized/) | CX23 €5,99; CX23 a CX53 "currently unavailable" | consultado 31/10/2026 |
| [Hetzner, Regular Performance](https://www.hetzner.com/cloud/regular-performance/) | CPX02 €6,49 (1/1 GB/20 GB), CPX12 €11,99 | consultado 31/10/2026 |
| [Hetzner Status, "Limited availability of cloud instances"](https://status.hetzner.com/incident/0a75c7ae-3377-41dc-aabe-601063724d24) | Desde el 26/6/2026 restringe crear servidores a cuentas nuevas; sigue "Identified" | consultado 31/10/2026 |
| [Private DevOps, Hetzner CPX02](https://privatedevops.com/news/hetzner-cpx02-1gb-cloud-server) | CPX02 y todos los CPX figuraban sin stock el 12/10 | 12/10/2026 |
| [Hetzner Docs, ajuste del 15/6/2026](https://docs.hetzner.com/general/infrastructure-and-availability/price-adjustment/) | Precios antes y después | 15/6/2026 |
| [AgentDeals, Hetzner 2026](https://agentdeals.dev/hetzner-pricing-2026) | CX23 USD 7,09; CPX12 €11,99 / USD 14,09; CPX02 USD 8,09; "a plan marked orderable may still be one a new customer cannot create" | precios del 7/10/2026 |
| [Spare Cores, Hetzner CPX12](https://sparecores.com/server/hcloud/cpx12) | 1 vCPU, 2 GB, 40 GB NVMe | consultado 31/10/2026 |
| [dev.to (hostingsift), 24 alternativas a Hetzner](https://dev.to/hostingsift/is-hetzner-still-the-cheapest-vps-we-priced-24-alternatives-october-2026-271g) | Comparativo de precios, EUR→USD a 1,15 | 23/10/2026 |
| [Oracle, Always Free Resources](https://docs.oracle.com/en-us/iaas/Content/FreeTier/resourceref.htm) | A1 2 OCPU/12 GB, E2.1.Micro, reclamo por inactividad, 10 TB | consultado 31/10/2026 |
| [Linuxiac, recorte del free tier de Oracle](https://linuxiac.com/oracle-quietly-cuts-free-tier-ampere-a1-resources-in-half/) | De 4/24 a 2/12 | 14/6/2026 |
| [DigitalOcean, Droplet pricing](https://www.digitalocean.com/pricing/droplets) | USD 4 y USD 6; facturación por segundo; regiones | consultado 31/10/2026 |
| [ployz.dev, Vultr pricing 2026](https://ployz.dev/blog/vultr-pricing) | USD 5 por 1 GB, São Paulo × 1,5, tráfico | 2026 |
| [Vultr, regiones](https://www.vultr.com/features/datacenter-regions/) | São Paulo, Santiago, México (vía buscador; la página me devolvió 403) | consultado 31/10/2026 |
| [Telegram Bot API, setWebhook](https://core.telegram.org/bots/api#setwebhook) y [Getting updates](https://core.telegram.org/bots/api#getting-updates) | Puertos 443/80/88/8443, header del secreto, updates guardados 24 h | consultado 31/10/2026 |
| [Cloudflare, Quick Tunnels](https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/do-more-with-tunnels/trycloudflare/) | Solo para pruebas, sin garantía de uptime | consultado 31/10/2026 |
| [Diario Popular, fin del 30 % del dólar tarjeta](https://www.diariopopular.com.ar/economia/dolar-tarjeta-arca-elimina-ese-30-adicional-pero-no-todos-los-consumos-n878910) | Sin percepción del 30 % desde el 2/1/2026, salvo turismo | 2/1/2026 |
| [Comercio y Justicia, el 30 % sigue para turismo en pesos](https://comercioyjusticia.info/economia/el-recargo-del-30-seguira-vigente-para-servicios-turisticos-abonados-en-pesos/) | Sin 30 % para pagos en moneda extranjera y a proveedores del exterior | 2/1/2026 |
| [El Liberal, "Desde hoy muere el dólar tarjeta"](https://www.elliberal.com.ar/nota/68222/2026/01/desde-hoy-muere-el-dolar-tarjeta--arca-elimina-el-30-en-porciento--de-recargo-y-el-tipo-de-cambio-es-400-menos) y [Info Viajera](https://www.infoviajera.com/2025/12/desde-enero-ya-no-regira-el-recargo-del-30-por-compras-con-tarjeta-en-dolares/) | Sin percepción del 30 % desde el 2/1/2026 | 2/1/2026 y 12/2025 |
| [impuestito.org, impuestos de suscripciones en dólares](https://impuestito.org/blog/que-impuestos-cobra-arca-al-pagar-juegos-y-suscripciones-con-tarjeta-en-dolares) | IIBB provincial ~2 % sobre servicios digitales (anterior al 2/1/2026) | 1/1/2026 |
| [Perfil, costo de pagar con tarjeta en 2026](https://www.perfil.com/noticias/economia/sin-impuesto-pais-como-cambia-el-costo-real-de-pagar-con-tarjeta-en-el-exterior-en-2026.phtml) | Todavía menciona el 30 % (contradice a la anterior) | 12/1/2026 |
| [ARCA, régimen de percepción RG 4240](https://www.afip.gob.ar/iva/servicios-digitales/reg-percepcion-4240.asp) | IVA de servicios digitales: lo perciben los bancos | consultado 31/10/2026 |
| Mediciones propias | Headers de cada portal con curl (`server`, `cf-ray`, `via`, `x-li-pop`: LinkedIn no pasa por Cloudflare); RAM del worker y de la api; corridas y volumen por portal (`logs/app.log`, `resultados/` del 20 al 31/10) | 30 y 31/10/2026 |
