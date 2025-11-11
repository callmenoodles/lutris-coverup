# Cover Up for Lutris
Cover Up is a CLI application meant to aid with downloading missing covers, banners, and icons in Lutris. This is a common [issue](https://github.com/lutris/lutris/issues/4024), because Lutris only fetches assets from [IGDB (Internet Game Database)](https://www.igdb.com/).

## Quirks
> [!WARNING]
> I haven't implemented an undo feature yet, so if you run the program, it's only possible to undo by manually removing all assets.

> [!IMPORTANT]
> If a banner can't be found, Cover Up tries to put the game's logo on top of a hero. If there's no logo, the hero will be used as a banner.

> [!NOTE] 
> This project is a WIP and currently fetches assets from SteamGridDB only. Not all games on SteamGridDB have assets and there is no fallback option yet. However, it is possible to upload assets to SteamGridDB.
 
## Installation
1. Download `lutris-coverup` from [releases](https://github.com/callmenoodles/lutris-coverup/releases)
2. Make the binary executable: 
```commandline
# chmod +x lutris-coverup
```

### System-wide installation
```commandline
# mv lutris-coverup /usr/local/bin
```

## Usage
```commandline
$ lutris-coverup -k <STEAMGRIDDB_API_KEY>
```
### Options
```commandline
  -h, --help                      Show this message and exit.
  -v, --version                   Show the version and exit.
  -k, --api-key TEXT              SteamGridDB API key  [required]
  -r, --resize [none|stretch|crop]
                                  Lutris uses a different aspect ratio than SteamGridDB.
                                  Specify whether the new assets should be stretched or
                                  cropped to fill  [default: STRETCH]
  -t, --target [all|covers|banners|icons]
                                  The assets to be updated  [default: ALL]
  -l, --lutris-path DIRECTORY     Path to the directory containing coverart, banners, and
                                  pga.db  [default: ~/.local/share/lutris]
  -i, --icon-path DIRECTORY       Path to the directory containing the game icons  [default:
                                  ~/.local/share/icons/hicolor/128x128/apps]
```

#### API Key
You need to pass a SteamGridDB API key for this application to work.
1. Sign in to [SteamGridDB](https://steamgriddb.com) with your Steam account
2. Go to [Preferences > API](https://www.steamgriddb.com/profile/preferences/api)
3. Copy your API key

#### Resize
Lutris fetches its assets from IGDB and resizes them. Covers and banners fetched from SteamGridDB are not the same aspect ratio, so the covers are a bit more narrow. The `--resize` flag, described in [Usage](#usage), allows you to specify whether the assets should be stretched, cropped, or left as is after resizing them.
Icons are all square 1:1 images.

|             | Covers | Covers  | Banners | Banners  |
|-------------|--------|---------|--------|----------|
| IGDB        | 3:4    | 600x800 | 8:3    | ?        |
| Lutris      | 3:4    | 264x352 | 8:3    | 184x69   |
| SteamGridDB | 2:3    | 600x900 | 96:31  | 1920x620 |

#### Target
Use this if you only want to update covers, banners, **or**, icons.

#### Lutris Path
Lutris stores game covers in `coverart`, banners in `banners`, and all your games' information in a SQLite database called `pga.db`.

#### Icon Path
Lutris stores game icons in a separate directory `icons/hicolor/128x128/apps`.

## Credits
- [@Deytron](https://github.com/Deytron) for the foundation in [Lutris Cover Art Downloader](https://github.com/Deytron/lutris-art-downloader)
- [SteamGridDB](https://www.steamgriddb.com/) for the assets