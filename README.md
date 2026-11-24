# Plugin de Streamlink: La 7 TV (Región de Murcia)

Un plugin para [Streamlink](https://github.com/streamlink/streamlink) destinado al canal en directo **La 7 TV Directo** (<https://www.la7tv.es>), emitido mediante HLS a través de la plataforma Globalmest.

La transmisión está protegida por un token de corta duración que el sitio web genera para cada visitante. Este plugin obtiene dicho token de la página y lo añade a la transmisión, replicando el comportamiento del reproductor web; de este modo, es posible ver el canal utilizando Streamlink, VLC, mpv o cualquier otro reproductor compatible con streaming HLS.

## URL compatibles

| URL | Notas |
| --- | --- |
| `https://www.la7tv.es/a-la-carta/7tv-en-directo/20220810150726000939.html` | Página de emisión en directo; el token se extrae de ella. |
| `https://rtv-murcia-live.globalmest.com/principal/smil:principal.smil/playlist.m3u8` | URL directa de la transmisión; el token se obtiene de la página de emisión en directo. |
| `https://rtv-murcia-live.globalmest.com/...playlist.m3u8?auth_token=<JWT>` | URL completa copiada desde un navegador; el token se utiliza tal cual. |

Cualquier otra página dentro de `la7tv.es` también es reconocida y permite reproducir el mismo canal en directo.

## Uso

### Carpeta de plugins de usuario (no requiere recompilación)

Copia el archivo `la7tv.py` en el directorio de plugins de usuario de Streamlink:

| Sistema operativo | Ruta |
| --- | --- |
| Linux | `~/.config/streamlink/plugins/` |
| macOS | `~/Library/Application Support/streamlink/plugins/` |
| Windows | `%APPDATA%\streamlink\plugins\` |

Si la carpeta `plugins` no existe, créala. Streamlink detecta el plugin automáticamente.

## Uso

```bash
# Reproducir en el reproductor predeterminado
streamlink "https://www.la7tv.es/a-la-carta/7tv-en-directo/20220810150726000939.html" best

# Usar la URL directa del flujo (stream)
streamlink "https://rtv-murcia-live.globalmest.com/principal/smil:principal.smil/playlist.m3u8" best

# Guardar en un archivo
streamlink -o la7.ts "https://www.la7tv.es/a-la-carta/7tv-en-directo/20220810150726000939.html" best

# Mostrar la URL del flujo resuelta
streamlink --stream-url "https://www.la7tv.es/a-la-carta/7tv-en-directo/20220810150726000939.html" best

## Limitaciones

- **Duración del token:** los tokens tienen una validez aproximada de 2 horas. Si una sesión de visualización supera este tiempo, es posible que empiecen a aparecer errores HTTP 403. Reinicia Streamlink para obtener un nuevo token.

## Archivos

- `la7tv.py`: el plugin para streamlink https://github.com/streamlink/streamlink  
- `la7_hls_token.py`: script independiente que genera la URL `.m3u8` con token; puede utilizarse sin Streamlink, con VLC por ejemplo https://github.com/videolan/vlc/ 

## Contacto

Envie comentarios, sugerencias y dudas a fossideasdev@gmail.com

 

