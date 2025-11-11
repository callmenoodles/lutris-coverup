import logging
import tempfile

import requests
from PIL import Image
from steamgrid import StyleType, MimeType  # type: ignore

from lutris_coverup.enums import ResizeMethod

logger: logging.Logger = logging.getLogger(__name__)

LUTRIS_COVER_WIDTH = 264
LUTRIS_COVER_HEIGHT = 352
COVER_CROP_MARGIN = 50

LUTRIS_BANNER_WIDTH = 184
LUTRIS_BANNER_HEIGHT = 69

ICON_SIZE = 128  # width and height, since icons are 1:1


def fetch_icons(sgdb, games, path):
    for game in games:
        res = sgdb.search_game(game)

        if not res:
            logger.warning(f"Unable to find {game} on SteamGridDB")
            break

        game_name = res[0].name

        if not res:
            logger.warning(f'Unable to find icon for "{game_name}"')
        else:
            game_id = res[0].id
            icon = sgdb.get_icons_by_gameid([game_id])

            if icon is None:
                logger.warning(f'No icons available for "{game_name}"')
            else:
                icon_req = requests.get(icon[0].url)
                img_path = path.joinpath("lutris_" + game).with_suffix(".png")

                with open(img_path, "wb") as f:
                    f.write(icon_req.content)

                icon_img = Image.open(img_path)
                icon_img.thumbnail((ICON_SIZE, ICON_SIZE))
                icon_img.save(img_path)
                logger.info(f'Successfully updated icon for "{game_name}"')


def fetch_banners(sgdb, games, path, resize):
    for game in games:
        res = sgdb.search_game(game)

        if not res:
            logger.warning(f"Unable to find {game} on SteamGridDB")
            break

        game_name = res[0].name

        if not res:
            logger.warning(f'Unable to find banner for "{game_name}"')
        else:
            game_id = res[0].id
            banner = sgdb.get_heroes_by_gameid(
                [game_id], styles=[StyleType.Alternate], mimes=[MimeType.JPEG]
            )

            if banner is None:
                logger.warning(f'No banners available for "{game_name}"')
            else:
                banner_req = requests.get(banner[0].url)
                img_path = path.joinpath(game).with_suffix(".jpg")

                with open(img_path, "wb") as f:
                    f.write(banner_req.content)

                banner_img = Image.open(img_path)

                logos = sgdb.get_logos_by_gameid([game_id])

                # Should the banner be saved when no logo is found?
                if logos is None:
                    logger.warning(f'No logos available for "{game_name}"')
                else:
                    logo_req = requests.get(logos[0].url)

                    tmp_logo = tempfile.TemporaryFile()
                    tmp_logo.write(logo_req.content)
                    logo_img = Image.open(tmp_logo)
                    logo_img.thumbnail(
                        (banner_img.width - banner_img.width * 0.3, banner_img.height)
                    )

                    banner_img.paste(
                        logo_img,
                        (
                            int((banner_img.width - logo_img.width) / 2),
                            int((banner_img.height - logo_img.height) / 2),
                            int(
                                banner_img.width
                                - (banner_img.width - logo_img.width) / 2
                            ),
                            int(
                                banner_img.height
                                - (banner_img.height - logo_img.height) / 2
                            ),
                        ),
                        logo_img,
                    )

                # FIXME: Hardcoded sizes
                if resize == ResizeMethod.STRETCH:
                    banner_img = banner_img.resize(
                        (LUTRIS_BANNER_WIDTH, LUTRIS_BANNER_HEIGHT)
                    )
                elif resize == ResizeMethod.CROP:
                    cropped_img = banner_img.crop((133, 0, 1786, 620))
                    banner_img = cropped_img.resize(
                        (LUTRIS_BANNER_WIDTH, LUTRIS_BANNER_HEIGHT)
                    )

                banner_img.save(img_path)
                logger.info(f'Successfully updated banner for "{game_name}"')


def fetch_cover_art(sgdb, games, path, resize):
    for game in games:
        res = sgdb.search_game(game)

        if not res:
            logger.warning(f"Unable to find {game} on SteamGridDB")
            break

        game_name = res[0].name

        if not res:
            logger.warning(f'Unable to find cover for "{game_name}"')
        else:
            game_id = res[0].id
            grid = sgdb.get_grids_by_gameid([game_id], mimes=[MimeType.JPEG])

            if grid is None:
                logger.warning(f'No covers available for "{game_name}"')
            else:
                grid_req = requests.get(grid[0].url)
                img_path = path.joinpath(game).with_suffix(".jpg")

                with open(img_path, "wb") as f:
                    f.write(grid_req.content)

                cover_img = Image.open(img_path)

                # FIXME: Hardcoded sizes
                if resize == ResizeMethod.STRETCH:
                    cover_img = cover_img.resize(
                        (LUTRIS_COVER_WIDTH, LUTRIS_COVER_HEIGHT)
                    )
                elif resize == ResizeMethod.CROP:
                    cropped_img = cover_img.crop(
                        (0, COVER_CROP_MARGIN, 600, 900 - COVER_CROP_MARGIN)
                    )
                    cover_img = cropped_img.resize(
                        (LUTRIS_COVER_WIDTH, LUTRIS_COVER_HEIGHT)
                    )

                cover_img.save(img_path)
                logger.info(f'Successfully updated cover for "{game_name}"')
