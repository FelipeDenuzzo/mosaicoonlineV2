import math
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from PIL import Image


@dataclass
class TileInfo:
    path: Path
    average_color: tuple[int, int, int]
    uses: int = 0


def mm_to_pixels(mm: int, dpi: int = 240) -> int:
    inches = mm / 25.4
    return max(1, round(inches * dpi))


def average_color(image: Image.Image) -> tuple[int, int, int]:
    small = image.convert("RGB").resize((1, 1), Image.Resampling.LANCZOS)
    return small.getpixel((0, 0))


def list_image_files(folder: Path) -> list[Path]:
    supported = (".png", ".jpg", ".jpeg")
    return [
        folder / name
        for name in sorted(folder.iterdir())
        if name.suffix.lower() in supported
    ]


def load_tiles(folder: Path) -> list[TileInfo]:
    tiles: list[TileInfo] = []
    for path in list_image_files(folder):
        with Image.open(path) as image:
            rgb_image = image.convert("RGB")
            tiles.append(TileInfo(path=path, average_color=average_color(rgb_image)))
    return tiles


def distance(color_a: tuple[int, int, int], color_b: tuple[int, int, int]) -> float:
    return math.sqrt(sum((color_a[index] - color_b[index]) ** 2 for index in range(3)))


def select_tile(
    target_color: tuple[int, int, int],
    tiles: Iterable[TileInfo],
    max_uses: int,
    similarity: float,
) -> TileInfo:
    tiles_list = list(tiles)
    dists: list[tuple[TileInfo, float]] = []

    for tile in tiles_list:
        if max_uses and tile.uses >= max_uses:
            continue
        dists.append((tile, distance(target_color, tile.average_color)))

    if not dists:
        dists = [(tile, distance(target_color, tile.average_color)) for tile in tiles_list]

    if not dists:
        raise RuntimeError("No tile image available to continue the mosaic.")

    bounded_similarity = max(0.0, min(100.0, similarity))
    min_dist = min(d[1] for d in dists)
    max_dist = 442.0
    threshold = min_dist + (max_dist - min_dist) * (bounded_similarity / 100.0)

    candidates = [tile for tile, diff in dists if diff <= threshold]
    if candidates:
        return random.choice(candidates)

    return min(dists, key=lambda d: d[1])[0]


def build_mosaic(
    reference_path: Path,
    tiles_folder: Path,
    tile_size_mm: int,
    max_uses: int,
    output_path: Path,
    similarity: float = 0.0,
    quality: int = 85,
    dpi: int = 240,
) -> Path:
    tile_analysis_px = mm_to_pixels(tile_size_mm, dpi)
    tiles = load_tiles(tiles_folder)

    if not tiles:
        raise RuntimeError("No image found in the tiles folder.")

    with Image.open(reference_path) as reference:
        reference = reference.convert("RGB")
        tiles_x = max(1, reference.width // tile_analysis_px)
        tiles_y = max(1, reference.height // tile_analysis_px)

        resized_ref = reference.resize(
            (tiles_x * tile_analysis_px, tiles_y * tile_analysis_px),
            Image.Resampling.LANCZOS,
        )

        with Image.open(tiles[0].path) as sample:
            sample_width = sample.width
            sample_height = sample.height

    final_width = tiles_x * sample_width
    final_height = tiles_y * sample_height
    mosaic = Image.new("RGB", (final_width, final_height), "white")

    for row in range(tiles_y):
        for col in range(tiles_x):
            left_ref = col * tile_analysis_px
            top_ref = row * tile_analysis_px
            right_ref = left_ref + tile_analysis_px
            bottom_ref = top_ref + tile_analysis_px

            left_final = col * sample_width
            top_final = row * sample_height

            cell = resized_ref.crop((left_ref, top_ref, right_ref, bottom_ref))
            cell_color = average_color(cell)

            tile = select_tile(cell_color, tiles, max_uses=max_uses, similarity=similarity)
            tile.uses += 1

            with Image.open(tile.path) as tile_img:
                tile_img = tile_img.convert("RGB")
                if tile_img.size != (sample_width, sample_height):
                    tile_img = tile_img.resize((sample_width, sample_height), Image.Resampling.LANCZOS)
                mosaic.paste(tile_img, (left_final, top_final))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    mosaic.save(output_path, "JPEG", quality=max(1, min(100, quality)))
    return output_path
