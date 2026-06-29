# RP2350 PC Monitor

Surveillez les ressources de votre PC (CPU, RAM, réseau, température) sur un écran Waveshare RP2350-LCD-1.47-B, propulsé par LVGL + MicroPython.

![status](https://img.shields.io/badge/status-stable-brightgreen)
![version](https://img.shields.io/badge/version-1.0-blue)

## Matériel

- **Carte** : [Waveshare RP2350-LCD-1.47-B](https://www.waveshare.com/rp2350-lcd-1.47-b.htm) (RP2350 + écran 1.47" 172×320 ST7789V3)
- **Connexion** : USB série

## Fonctionnalités

- Utilisation CPU (barre + pourcentage)
- Température du CPU
- Utilisation RAM (barre + pourcentage)
- Nombre de processus actifs
- Débit réseau montant/descendant (Ko/s)
- Horodatage
- Barres colorées selon la charge (vert → orange → rouge)
- Reconnexion automatique côté PC si le Pico est débranché

## Structure du projet

| Fichier/Dossier | Description |
|-----------------|-------------|
| `main.py` | Firmware MicroPython — interface LVGL, pilote LCD, parseur JSON série |
| `pc_monitor.py` | Script PC — collecte les métriques système avec psutil, envoie du JSON sur série |
| `lib/lv_utils.py` | Utilitaires LVGL (timer tick + task handler) |
| `images/background-1.png` | Image de fond pour l'interface |
| `firmware/` | Fichiers de compilation du firmware LVGL+MicroPython (voir Installation) |

## Firmware personnalisé

Ce projet nécessite un **firmware MicroPython personnalisé** compilé avec les bindings LVGL.

### Prérequis

- Fork de [lvgl_micropython](https://github.com/lvgl/lvgl_micropython) avec support RP2350
- Pico SDK 2.x

### Compilation

```bash
cd lvgl_micropython
make.py rp2 BOARD=RPI_PICO2
```

Le binaire produit se trouve dans `build/lvgl_micropy_RPI_PICO2.uf2`.

### Flash

Maintenez le bouton **BOOTSEL** enfoncé en branchant le Pico 2 en USB, puis copiez le fichier UF2 :

```bash
cp build/lvgl_micropy_RPI_PICO2.uf2 /media/$USER/RPI_RP2/
```

Ou avec `picotool` :

```bash
picotool load build/lvgl_micropy_RPI_PICO2.uf2 && picotool reboot
```

## Brochage

| Pin LCD | GPIO |
|---------|------|
| DC | 16 |
| CS | 17 |
| SCLK | 18 |
| MOSI | 19 |
| RST | 20 |
| BL  | 21 (PWM) |

Utilise le bus **SPI0** à 60 MHz.

## Déploiement

### 1. Envoyer les scripts sur la carte

```bash
mpremote cp main.py :main.py
mpremote cp lib/lv_utils.py :lib/lv_utils.py
```

### 2. Lancer le moniteur PC

```bash
pip install pyserial psutil
python pc_monitor.py
```

## Fonctionnement

`pc_monitor.py` interroge `psutil` chaque seconde et envoie une ligne JSON sur le port série USB :

```json
{"time":"14:32:01","cpu":"23%","temp":"45.0C","ram":"67%","proc":312,"up":"0.5K","down":"1.2K"}
```

`main.py` parse le JSON et l'affiche sur l'écran via LVGL.

## Détails techniques

- Pilote d'affichage : ST7789V3, 172×320, utilisé en paysage (320×172) via MADCTL MV=1
- SPI : 60 MHz, RGB565 big-endian
- Mode de rendu LVGL : `PARTIAL` avec 2 buffers de draw (1/3 écran chacun)
- Offset Y de 34 appliqué dans `set_window()` pour compenser l'alignement du panneau ST7789V3
