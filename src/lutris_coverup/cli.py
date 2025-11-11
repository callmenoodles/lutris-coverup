import os
import sqlite3
import logging
from logging import Logger
from typing import List, Any

import click
from dotenv import load_dotenv
from steamgrid import SteamGridDB  # type: ignore
from pathlib import Path

from lutris_coverup.enums import ResizeMethod, AssetType
from lutris_coverup.fetch import fetch_cover_art, fetch_banners, fetch_icons

CONTEXT_SETTINGS = dict(max_content_width=96)
DEFAULT_LUTRIS_PATH = Path("~/.local/share/lutris")
DEFAULT_ICON_PATH = Path("~/.local/share/icons/hicolor/128x128/apps")

logger: Logger = logging.getLogger(__name__)


@click.command(context_settings=CONTEXT_SETTINGS)
@click.help_option("-h", "--help")
@click.version_option(
    "0.1.1",
    "-v",
    "--version",
    prog_name="lutris-coverup",
    message="%(prog)s v%(version)s",
)
@click.option(
    "-k",
    "--api-key",
    envvar="STEAMGRIDDB_API_KEY",
    required=True,
    type=click.STRING,
    help="SteamGridDB API key",
)
@click.option(
    "-r",
    "--resize",
    default=ResizeMethod.STRETCH,
    show_default=True,
    type=click.Choice(ResizeMethod, case_sensitive=False),
    help="Lutris uses a different aspect ratio than SteamGridDB. "
    "Specify whether the new assets should be stretched or cropped to fill",
)
@click.option(
    "-t",
    "--target",
    default=AssetType.ALL,
    show_default=True,
    type=click.Choice(AssetType, case_sensitive=False),
    help="The assets to be updated",
)
@click.option(
    "-l",
    "--lutris-path",
    default=DEFAULT_LUTRIS_PATH,
    type=click.Path(file_okay=False, dir_okay=True, writable=False, path_type=Path),
    show_default=True,
    help="Path to the directory containing coverart, banners, and pga.db",
)
@click.option(
    "-i",
    "--icon-path",
    default=DEFAULT_ICON_PATH,
    type=click.Path(file_okay=False, dir_okay=True, writable=False, path_type=Path),
    show_default=True,
    help="Path to the directory containing the game icons",
)
def cli(
    api_key: str,
    resize: ResizeMethod,
    target: AssetType,
    lutris_path: Path,
    icon_path: Path,
) -> None:
    lutris_path_abs: Path = lutris_path.expanduser().absolute()
    cover_art_path: Path = lutris_path_abs.joinpath("coverart")
    banner_path: Path = lutris_path_abs.joinpath("banners")
    db_path: Path = lutris_path_abs.joinpath("pga.db")
    icon_path = icon_path.expanduser().absolute()

    missing_cover_games: List[str] = []
    missing_banner_games: List[str] = []
    missing_icon_games: List[str] = []

    try:
        conn: sqlite3.Connection = sqlite3.connect(db_path)
        query: sqlite3.Cursor = conn.execute("SELECT slug FROM games")
        res: List[Any] = query.fetchall()

        for slug in res:
            slug = slug[0]  # slug_res returns ('slug',)

            if target is AssetType.COVERS or target is AssetType.ALL:
                game_cover_path: Path = cover_art_path.joinpath(slug).with_suffix(
                    ".jpg"
                )

                if not game_cover_path.is_file():
                    missing_cover_games.append(slug)
            if target is AssetType.BANNERS or target is AssetType.ALL:
                game_banner_path: Path = banner_path.joinpath(slug).with_suffix(".jpg")

                if not game_banner_path.is_file():
                    missing_banner_games.append(slug)
            if target is AssetType.ICONS or target is AssetType.ALL:
                game_icon_path: Path = icon_path.joinpath("lutris_" + slug).with_suffix(
                    ".png"
                )

                if not game_icon_path.is_file():
                    missing_icon_games.append(slug)

        if target == AssetType.COVERS and not missing_cover_games:
            logger.info("No missing covers found.")
        elif target == AssetType.BANNERS and not missing_banner_games:
            logger.info("No missing banners found.")
        elif target == AssetType.ICONS and not missing_icon_games:
            logger.info("No missing icons found.")
        elif target == AssetType.ALL and not (
            missing_cover_games or missing_banner_games or missing_icon_games
        ):
            logger.info("No missing assets found.")

    except Exception as e:
        logger.error(e)
        return

    load_dotenv()

    if api_key is None:
        api_key = os.getenv("STEAMGRIDDB_API_KEY")

    sgdb: SteamGridDB = SteamGridDB(api_key)

    if target is AssetType.COVERS or target is AssetType.ALL:
        fetch_cover_art(sgdb, missing_cover_games, cover_art_path, resize)
    if target is AssetType.BANNERS or target is AssetType.ALL:
        fetch_banners(sgdb, missing_banner_games, banner_path, resize)
    if target is AssetType.ICONS or target is AssetType.ALL:
        fetch_icons(sgdb, missing_icon_games, icon_path)
