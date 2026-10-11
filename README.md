![ESPHome and Home Assistant voice assistant on the Waveshare ESP32-S3-AUDIO-Board](docs/hero.jpg)

# ESPHome Voice Assistant for the Waveshare ESP32-S3-AUDIO-Board

A **Home Assistant voice satellite** running on the
[Waveshare ESP32-S3-AUDIO-Board](https://www.waveshare.com/esp32-s3-audio-board.htm),
the little AI smart-speaker devkit with a dual-mic array, an ES8311 codec, three
buttons and a 7-LED RGB ring. Pure ESPHome, no custom C firmware: an always-on
core you pull as a package, plus one thin config file you actually edit.

> [!NOTE]
> **This is a fork** of
> [MichalZaniewicz/esphome-waveshare-esp32-s3-audio-va](https://github.com/MichalZaniewicz/esphome-waveshare-esp32-s3-audio-va)
> by **Michał Zaniewicz**, who designed and built the original firmware: the
> shared-I2S audio layout, the LED state machine, the wake word handling and
> the docs. This fork adds an alarm clock you set from Home Assistant, a timer
> countdown on the ring, a separate ring volume, replies and rings on an
> external speaker, the onboard RTC, diagnostics and a fallback hotspot. See
> [What this fork adds](#what-this-fork-adds) and [Credits](#credits).

<!-- The badges live OUTSIDE the alert on purpose: Home Assistant rewrites a
GitHub alert into <ha-alert> and drops every child whose textContent is empty,
which silently removes any <img> placed inside it. -->

If you like the project, support the original author: star
[his repository](https://github.com/MichalZaniewicz/esphome-waveshare-esp32-s3-audio-va)
or [buy him a coffee](https://buymeacoffee.com/zanula).

[![Star the original repo](https://img.shields.io/github/stars/MichalZaniewicz/esphome-waveshare-esp32-s3-audio-va?style=for-the-badge&logo=github&label=STAR%20THE%20ORIGINAL&labelColor=555555&color=ffc107)](https://github.com/MichalZaniewicz/esphome-waveshare-esp32-s3-audio-va) [![Buy the author a coffee](https://img.shields.io/badge/BUY%20HIM%20A%20COFFEE-FFDD00?style=for-the-badge&logo=buymeacoffee&logoColor=black)](https://buymeacoffee.com/zanula)

![Trailer: the voice assistant, the LED ring animations and the Home Assistant controls](docs/trailer.webp)

> **Status:** based on the original **v1.2.0** (stable: wake word, STT/TTS,
> clean playback and the LED ring confirmed on-device), plus this fork's
> additions, tested on the board. The release history is in
> [CHANGELOG.md](CHANGELOG.md); the fork's changes are under *Unreleased*.

```
You  ──▶  Waveshare ESP32-S3  ──▶  Home Assistant Assist
         (wake word + audio)      (STT / LLM / TTS)
```

## What it does

![Home Assistant entities, the LED ring animation picker, the media player and the wake-word controls](docs/features.jpg)

- **Voice assistant**: on-device wake word via `micro_wake_word` (Alexa, Okay
  Nabu, Hey Jarvis or Hey Mycroft, picked in Home Assistant), the full Home
  Assistant Assist pipeline (STT / LLM / TTS), a wake beep and music ducking
  while it listens.
- **Simultaneous music and announcements**: a mixer speaker blends the media and
  announcement pipelines, so a doorbell announcement ducks the music instead of
  fighting it. Both are exposed to Music Assistant.
- **LED ring**: one state machine drives it. Boot, no-Wi-Fi, no-HA, listening,
  thinking, replying, timer counting, ringing, volume changed, each a distinct
  colour/effect. Brightness and the animation for the listening / thinking /
  replying phases are pickable from HA: solid plus 14 animations (pulses,
  breathe, wipe, scan, spinner, comet, twinkle, fireworks, fire, rainbows).
- **Timers**: set by voice, with a "Next timer" sensor in HA and a countdown
  on the ring that drains as the timer runs out.
- **Alarm clock**: one alarm, set from HA (on/off, time, days). It runs on the
  device, so it rings even when HA or the Wi-Fi is down.
- **Ring volume**: timers and the alarm ring at their own volume, separate from
  the general one. They ring even with the player muted, and changing the
  general volume meanwhile doesn't touch them. Stop a ring with the wake word,
  Play/Pause, from HA, or it gives up after 15 minutes.
- **A bigger speaker**: Assist replies, timers and the alarm can play on any
  Home Assistant media player, with the device's own speaker silent for them.
  The wake beep always plays on the device, even with its volume at zero.
- **Clock without HA**: the onboard PCF85063 RTC is set from HA on every time
  sync and read back at boot, so the clock is right before HA connects.
- **Buttons**: the three onboard keys do volume down, play-pause, volume up.
  While a timer or the alarm rings, Play/Pause silences it instead.
- **Boot chime**: a short "ready" sound once the device connects to HA
  (toggleable).
- **Night mode**: one switch dims the ring to its own brightness and skips the
  wake beep and boot chime. Drive it from any Home Assistant automation.
- **Microphone mute you can see**: while muted, the ring gives a short red
  flash every 10 seconds, so a muted device doesn't look like an idle one.
- **Tunable live from HA**: wake word and sensitivity, mic gain, LED brightness
  and animations, volumes, alarm: all entities, no reflashing.
- **Diagnostics**: Wi-Fi signal, uptime, IP address, SSID, ESPHome version,
  free heap and PSRAM.
- **Fallback hotspot**: if the Wi-Fi can't be reached, the board opens its own
  access point with a captive portal to enter new credentials, so a changed
  Wi-Fi password doesn't mean a USB reflash.

https://github.com/user-attachments/assets/3236cd4f-7184-4eee-a16a-0db6fe1603a3

## What this fork adds

On top of the original v1.2.0:

| Feature | Where |
|---|---|
| Alarm clock set from HA: **Alarm**, **Alarm time**, **Alarm days**, **Alarm action** (the original engine was there but could not be armed) | [Alarm clock](#alarm-clock) |
| Timer countdown on the ring (**Timer Progress** effect) | [Timers](#timers) |
| **Ring volume**, independent of the general volume | [Timers](#timers) |
| **Ringing** switch: see and stop a ring from HA | [Timers](#timers) |
| **Replies on external speaker**, **Timer action**, and an *External speaker* option for timers and the alarm | [Using an external speaker](#using-an-external-speaker) |
| Wake beep always audible, even with the device muted | [Using an external speaker](#using-an-external-speaker) |
| Onboard PCF85063 RTC as a backup clock | [docs/HARDWARE.md](docs/HARDWARE.md#rtc) |
| Mute reminder flash every 10 s | [What it does](#what-it-does) |
| Diagnostic entities and a fallback hotspot with captive portal | [Configuration](#configuration) |
| Fixes: a cancelled timer kept the ring pulsing, "Next timer" picked the wrong timer, a silenced ring could cut a later one short | [CHANGELOG.md](CHANGELOG.md) |

## Quick start

> Requires **ESPHome 2026.8.0+**.

1. Copy `secrets.example.yaml` to `secrets.yaml` and fill in your Wi-Fi. The
   native API is unencrypted by default; enable encryption in `base/core.yaml`
   if you want it (see the commented block there).
2. Copy **`waveshare-va.yaml`** next to it and edit the `substitutions:` at the
   top (device name, timezone, volume limits). That thin file is the only
   firmware file you keep. The core is **pulled from GitHub at compile time**,
   see its `packages:` block.
3. **First flash over USB**, then updates go wireless:
   ```
   esphome run waveshare-va.yaml
   ```
   Or drop both files into the ESPHome dashboard's `/config/esphome/` and hit
   Install.
4. In Home Assistant: the new ESPHome device appears, open **Configure** and
   assign an Assist pipeline.
5. Say "Alexa". The ring should go violet. To use another wake word, change
   **Wake word** on the device page (see [Wake words](#wake-words)).

### Updating

The `packages:` block in `waveshare-va.yaml` decides which code you build:

```yaml
packages:
  core:
    url: https://github.com/lurisin/esphome-waveshare-esp32-s3-audio-va
    ref: main          # a branch or a tag
    files:
      - base/core.yaml
    refresh: 1d
```

`refresh: 1d` keeps the downloaded core for a day: an Install within that day
reuses the cached copy even if the branch has moved on. A quick Install (a few
seconds instead of minutes) that shows no new entities is the sign of a stale
cache. To pick up a change at once, either set `refresh: 0s` (re-downloads on
every Install; handy while testing, then set it back) or clear the cache with
**Clean Build Files** in the dashboard (`esphome clean waveshare-va.yaml` on the
command line).

## Documentation

The original project's
[Wiki](https://github.com/MichalZaniewicz/esphome-waveshare-esp32-s3-audio-va/wiki)
has the full guide to everything the two share. The features this fork adds
are documented in this README.

- **[Installation](https://github.com/MichalZaniewicz/esphome-waveshare-esp32-s3-audio-va/wiki/Installation)**: first flash, Home Assistant setup, updating.
- **[Configuration](https://github.com/MichalZaniewicz/esphome-waveshare-esp32-s3-audio-va/wiki/Configuration)**: every substitution and every Home Assistant entity.
- **[Audio architecture](https://github.com/MichalZaniewicz/esphome-waveshare-esp32-s3-audio-va/wiki/Audio-architecture)**: the shared-I2S two-bus design, in depth.
- **[LED ring](https://github.com/MichalZaniewicz/esphome-waveshare-esp32-s3-audio-va/wiki/LED-ring)**: the state machine and every ring effect.
- **[Hardware](https://github.com/MichalZaniewicz/esphome-waveshare-esp32-s3-audio-va/wiki/Hardware)**: pinout, I2C map, and sourced gotchas.
- **[Troubleshooting](https://github.com/MichalZaniewicz/esphome-waveshare-esp32-s3-audio-va/wiki/Troubleshooting)** and **[FAQ](https://github.com/MichalZaniewicz/esphome-waveshare-esp32-s3-audio-va/wiki/FAQ)**.

## How the shared I2S bus is handled

The board wires the **ES8311 (DAC) and the ES7210 (ADC) to the same BCLK/LRCLK
pins**, and only one device can drive those clocks. ESPHome also cannot run a
single I2S bus full-duplex: a microphone and a speaker on one bus each try to
init the port, and the second fails with "Parent bus is busy".

The layout that works, all on **stock ESPHome components**:

- **Two I2S buses** (two ports) over the shared pins. The **mic bus is the I2S
  master**: it is always capturing for the wake word, so it drives BCLK/LRCLK/MCLK
  continuously. The **speaker bus is a slave** that reads the mic's clock, so it
  never needs a port of its own to master.
- The ES8311 and ES7210 are stock and slave to the mic's clock.
- The mic is pinned to **16-bit** (the i2s_audio default is 32-bit); since the
  mic is master it sets the frame's slot width, and a 32-bit frame against the
  16-bit DAC comes out as noise.

This gives simultaneous capture + playback with no custom component. The
annotated config is in the audio section of `base/core.yaml`.

## Repository layout

```
waveshare-va.yaml          # YOUR config: copy + edit this (pulls the rest from GitHub)
secrets.example.yaml       # copy to secrets.yaml
base/
  core.yaml                # the always-on core, pulled as a remote package
ci/
  build.yaml               # CI build target: compiles the core from the working tree
.github/workflows/
  build.yml                # compiles the firmware on every push and pull request
docs/
  HARDWARE.md              # pinout, I2C map, RTC, gotchas
scripts/
  validate.py              # offline YAML check (syntax, substitutions, duplicate ids)
  esplog.py                # stream device logs over the native API
skill/
  waveshare-esp32-s3-audio/  # Claude Code skill: pinout + hard-won gotchas
```

## Configuration

Everything worth changing day to day is a Home Assistant entity, not a config
edit. On the device page:

| Group | Entities |
|---|---|
| Controls | media player, **Microphone Mute**, **Status Ring**, **Alarm**, **Alarm time**, **Ringing**, Next timer, Next timer name, Key1-3 |
| Voice | **Wake word** (from HA), **Wake word sensitivity**, **Wake word threshold**, **Mic gain (ES7210)**, **Wake sound**, **Boot sound** |
| Ring (LED) | **LED Ring Brightness**, **Night LED Ring Brightness**, **Night mode**, **Listening / Thinking / Replying effect**, **Timer countdown on ring** |
| Sound | **Ring volume**, **Replies on external speaker**, **Timer action**, **Amplifier** |
| Alarm | **Alarm days**, **Alarm action** |
| Diagnostic | WiFi Signal, Uptime, IP Address, Connected SSID, ESPHome Version, Free Heap, Free PSRAM |
| Maintenance | **Restart**, Logger Level (disabled by default) |

What lives in `waveshare-va.yaml`:

| Substitution | Default | What it does |
|---|---|---|
| `name` / `friendly_name` | `waveshare-va` / `Waveshare Voice` | Device name. Changing `name` re-creates every entity in HA. |
| `posix_timezone` | `CET-1CEST,...` | Clock zone in POSIX form (the device has no IANA database). DST automatic. |
| `volume_min` / `volume_max` | `0.4` / `0.8` | Media player clamps, because the onboard amp distorts near the top. Ring volume and the wake beep use the same range. |
| `hidden_ssid` | `false` | `true` enables `fast_connect` for a hidden SSID. |
| `fallback_ap_password` | empty (open) | Password of the fallback hotspot, 8+ characters. Empty leaves it open. |
| `boot_sound_file` | repo `startup.mp3` | The connect-to-HA chime. Any URL or local MP3/FLAC/WAV. |

Pins and the audio format are substitutions too (in `base/core.yaml`), but you
should not need them unless you are porting to another board.

Entity IDs in the examples below (`switch.waveshare_voice_...`) assume the
default *Waveshare Voice* name; check yours in **Developer tools > States**.

### Wake words

The firmware ships four wake word models: `alexa` (the default), `okay_nabu`,
`hey_jarvis` and `hey_mycroft`. Pick the active one with the **Wake
word** select on the device page in Home Assistant; the choice is stored on the
device and survives reboots and updates.

If several satellites share one Home Assistant instance and can hear the same
voice, give each a different wake word. Home Assistant ignores a wake word it
already heard within the last two seconds, on any device, so two satellites on
the same word cancel each other out (the second one beeps and does nothing).

### Night mode

The **Night mode** switch dims the ring to **Night LED Ring Brightness** and
skips the wake beep and the boot chime. Replies still play at the normal
volume, timers and the alarm at **Ring volume**. It is a plain switch, so any
automation can drive it:

```yaml
automation:
  - alias: Voice satellite night mode
    triggers:
      - trigger: sun
        event: sunset
        id: "on"
      - trigger: sun
        event: sunrise
        id: "off"
    actions:
      - action: switch.turn_{{ trigger.id }}
        target:
          entity_id: switch.waveshare_voice_night_mode
```

### Timers

Voice timers are handled by Home Assistant's Assist ("set a timer for 10
minutes", "how much time is left on the timer"). Ask from the same satellite
that set the timer: timers belong to the device that created them.

- **On the ring**: while a timer runs, the lit share of the ring is the share
  of the timer still to go, and it drains smoothly. **Timer countdown on ring**
  turns it off (e.g. a nap timer in a dark room).
- **When it finishes**: what happens depends on **Timer action**, see
  [Using an external speaker](#using-an-external-speaker). The default,
  *Play sound*, rings on the device.
- **Ring volume** (10-100 %, default 80 %) sets how loud timers and the alarm
  ring. It is independent of the general volume: a ring is heard even with
  the player muted or turned down, moving the slider while it rings is heard
  at once, and changing the general volume during a ring only takes effect
  once it stops.
- **Ringing** is on while a timer or the alarm rings. Turn it off to stop the
  ring from HA; turn it on to try the Ring volume.

A ring stops with the wake word, with Play/Pause, by turning **Ringing** off,
or by itself after 15 minutes.

### Alarm clock

One alarm, set from the device page in Home Assistant:

| Entity | What it does |
|---|---|
| **Alarm** | Arms or disarms it. |
| **Alarm time** | The time, local to the device's time zone, 24 h. |
| **Alarm days** | *Every day*, *Weekdays* (Mon-Fri), *Weekends* (Sat-Sun), or *Once*: rings at the next occurrence of the time, then turns **Alarm** off. |
| **Alarm action** | Where it rings, the same four choices as **Timer action** (see below). |

The device checks its own clock every minute, so the alarm rings even when
Home Assistant or the Wi-Fi is down (the onboard RTC keeps the clock through a
reboot, and through a power cut with a backup cell on its header). It rings
like a timer: at **Ring volume**, with the ring pulsing purple. There is no
snooze.

The `esphome.alarm_ringing` event (with *Send event* or *Sound and event*) can
also drive any other automation, for example to open the blinds:

```yaml
automation:
  - alias: Open the blinds with the alarm
    triggers:
      - trigger: event
        event_type: esphome.alarm_ringing
    actions:
      - action: cover.open_cover
        target:
          entity_id: cover.bedroom
```

### Using an external speaker

The onboard speaker is small. Replies, timers and the alarm can play on any
Home Assistant media player instead: a Music Assistant player, a tablet with
Browser Mod, a Bluetooth speaker exposed to HA, ... Two independent settings,
each with its own automation:

| You want... | Replies on external speaker | Timer / Alarm action |
|---|---|---|
| everything on the external speaker | on | *External speaker* |
| replies outside, rings on the device | on | *Play sound* |
| replies on the device, rings outside | off | *External speaker* |

The **wake beep always plays on the device**, even with its volume at zero
(it then plays at the `volume_min` level), so you always hear that it woke
up. It still follows **Wake sound** and **Night mode**.

The device sends these events to Home Assistant (each carries the device's
`device_id`):

| Event | When | Data |
|---|---|---|
| `esphome.tts_uri` | every reply or announcement; for a long, streamed LLM reply as soon as the audio starts | `uri` |
| `esphome.timer_finished` | a timer finishes (all actions but *Play sound*) | `name` |
| `esphome.alarm_ringing` | the alarm goes off (all actions but *Play sound*) | |

#### Replies

Turn on **Replies on external speaker**: the device's own speaker stays silent
during Assist replies (and announcements HA sends to it). Then play each reply
on your speaker:

```yaml
automation:
  - alias: Assist replies on the external speaker
    mode: restart
    triggers:
      - trigger: event
        event_type: esphome.tts_uri
        event_data:
          device_id: YOUR_DEVICE_ID      # from the event, in Developer tools > Events
    conditions:
      - condition: state
        entity_id: switch.waveshare_voice_replies_on_external_speaker
        state: "on"
    actions:
      - action: media_player.play_media
        target:
          entity_id: media_player.living_room
        data:
          media_content_id: "{{ trigger.event.data.uri }}"
          media_content_type: music
          announce: true    # resumes the music afterwards; remove if your player doesn't support it
```

The URL serves FLAC, which browsers and Music Assistant play fine. With the
switch on and no automation, replies are simply not heard.

#### Timers and the alarm

**Timer action** and **Alarm action** choose where a ring is heard:

| Action | On the device | Event to HA |
|---|---|---|
| *Play sound* (default) | rings, repeating | none |
| *Send event* | nothing (no ring to stop) | once |
| *Sound and event* | rings, repeating | once |
| *External speaker* | rings **silently**: Ringing on, ring pulsing purple, stopped like any ring | once |

The event says *what* rings (the alarm, or which timer); the **Ringing** switch
says *for how long*. Together they make the external speaker repeat until you
stop the ring, with the wake word for instance:

```yaml
automation:
  - alias: Rings on the external speaker
    mode: restart
    triggers:
      - trigger: event
        event_type: esphome.timer_finished
        event_data:
          device_id: YOUR_DEVICE_ID
        id: timer
      - trigger: event
        event_type: esphome.alarm_ringing
        event_data:
          device_id: YOUR_DEVICE_ID
        id: alarm
    actions:
      - variables:
          ringing: switch.waveshare_voice_ringing
          message: >-
            {% if trigger.id == 'alarm' %}Time to get up{% elif trigger.event.data.name %}Timer {{ trigger.event.data.name }} finished{% else %}Timer finished{% endif %}
      # The switch and the event arrive together; give Ringing a moment.
      - wait_template: "{{ is_state(ringing, 'on') }}"
        timeout: 3
        continue_on_timeout: true
      - repeat:
          sequence:
            - action: tts.speak
              target:
                entity_id: tts.piper                   # your TTS engine
              data:
                media_player_entity_id: media_player.living_room
                message: "{{ message }}"
            - delay: 5                                 # longer than the message
          until:
            - condition: template
              value_template: "{{ not is_state(ringing, 'on') }}"
```

With *Send event* Ringing never turns on, so this speaks once. A loud external
speaker right next to the device can make the wake word harder to hear while
it talks; a longer `delay` leaves more room.

### Custom wake word models

Any of the four slots can be replaced with any microWakeWord v2 model by
extending it by `id` in your own config:

```yaml
micro_wake_word:
  models:
    - id: !extend alexa
      model: https://example.com/my_wake_word.json
      # probability_cutoff: 0.85   # optional, overrides the manifest default
```

The **Wake word sensitivity** presets are relative to each model's default
cutoff (its manifest value, or `probability_cutoff:` above): *Slightly
sensitive* uses the default, *Moderately* and *Very sensitive* lower it step by
step. For exact control, set the select to **Custom** and use the **Wake word
threshold** slider, from 0.50 to 0.99. It applies to whichever wake word is
active. Lower values trigger more easily and give more false activations. On
first boot the slider starts at the active model's default cutoff; the models
differ (0.90 for Alexa, 0.97 for Okay Nabu), so revisit it after changing the
wake word.

### Extra voice phrases

Assist only understands the sentences its language ships with. If a phrase you
use is not recognised (it goes to the LLM, or gets "Sorry, I couldn't
understand that"), add it as a custom sentence in Home Assistant, in
`config/custom_sentences/<language>/`, then restart HA. **Developer tools >
Assist** shows whether a sentence is matched, and with which values. An Italian
example, for "quanto manca al timer" and "timer pasta 5 minuti":

```yaml
# config/custom_sentences/it/timer.yaml
language: "it"
intents:
  HassTimerStatus:
    data:
      - sentences:
          - "quanto manca [a|su](l[ mio]|i[ miei]) timer"
          - "quanto (resta|rimane) [a|su](l[ mio]|i[ miei]) timer"
        response: default
      - sentences:
          - "quanto manca [a|su](l[ mio]|i[ miei]) timer (nominato|chiamato|per|della|del|di) {timer_name:name}"
        response: default
  HassStartTimer:
    data:
      - sentences:
          - "[(avvia|imposta|crea|attiva) [un |il ]]timer [(per|di|della|del|per la|per il) ]{timer_name:name} [(per|da|di|d') ]{timer_minutes:minutes} minut(o|i)"
          - "[(avvia|imposta|crea|attiva) [un |il ]]timer [(per|di|della|del|per la|per il) ]{timer_name:name} [(per|da|di|d') ]{timer_seconds:seconds} second(o|i)"
          - "[(avvia|imposta|crea|attiva) [un |il ]]timer [(per|di|della|del|per la|per il) ]{timer_name:name} [(per|da|di|d') ]{timer_hours:hours} or(a|e)"
        response: default
      - sentences:
          - "[(avvia|imposta|crea|attiva) [un |il ]]timer [(per|di|della|del|per la|per il) ]{timer_name:name} [(per|da|di|d') ]un minuto"
        slots:
          minutes: 1
        response: default
```

## Claude Code skill

This repo ships a [Claude Code](https://claude.com/claude-code) skill at
[`skill/waveshare-esp32-s3-audio/`](skill/waveshare-esp32-s3-audio/SKILL.md):
the pinout, the shared-I2S constraint, and the gotchas that cost real debugging
time. Install it user-wide so any session picks it up:

```bash
cp -r skill/waveshare-esp32-s3-audio ~/.claude/skills/
```

## Credits

- **[Michał Zaniewicz](https://github.com/MichalZaniewicz)**: author of the
  [original project](https://github.com/MichalZaniewicz/esphome-waveshare-esp32-s3-audio-va)
  this fork is built on: the firmware design, the shared-I2S audio layout, the
  LED state machine, the hardware research in [docs/HARDWARE.md](docs/HARDWARE.md),
  the Claude Code skill, the artwork and the Wiki. Released under the
  [MIT License](LICENSE), which this fork keeps. If this firmware is useful to
  you, [star his repository](https://github.com/MichalZaniewicz/esphome-waveshare-esp32-s3-audio-va)
  or [buy him a coffee](https://buymeacoffee.com/zanula).
- **[lurisin](https://github.com/lurisin)**: this fork's additions (see
  [What this fork adds](#what-this-fork-adds)).
- **[jensenbox](https://github.com/jensenbox/waveshare-esp32-s3-audio)**: the
  ESP-master I2S layout for this board that the audio setup is based on.
- **ESPHome**: everything the firmware is built out of.
- **[Home Assistant Voice PE](https://github.com/esphome/home-assistant-voice-pe)**:
  the sounds, and the phase/ducking model the LED state machine follows.
