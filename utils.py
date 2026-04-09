import settings


def cart_to_iso( row, col, tile_size: tuple[int, int] = settings.tile_size) -> tuple[float, float]:
    iso_x = (row - col) * tile_size[0] // 2
    iso_y = (row + col) * tile_size[1] // 2
    return (iso_x, iso_y)

def z_stack_value(row, col, tile_size: tuple[int, int] = settings.tile_size) -> float:
    return  (row + col) * tile_size[1] // 2

def iso_to_cart(x, y, tile_size: tuple[int, int]= settings.tile_size) ->tuple[int, int]:
    "tile size: 1arg width 2arg height"
    row = y / tile_size[1] + x / tile_size[0]
    col = y / tile_size[1] - x / tile_size[0]
    return round(row), round(col)


