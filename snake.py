from argparse import ArgumentParser, ArgumentTypeError
from dataclasses import dataclass
from itertools import cycle
import logging
from typing import List, Tuple
import pygame
from pygame import Surface
import random
from pygame.rect import Rect
import enum

RECT_SIZE = 20
ROWS = 20
COLS = 20
WIDTH, HEIGHT = RECT_SIZE * COLS, RECT_SIZE * ROWS

logging.basicConfig(
    format="%(asctime)s : %(levelname)s : %(message)s", level=logging.INFO
)
logger = logging.getLogger("snake")


class GameException(Exception):
    pass


class Direction(enum.Enum):
    NONE = enum.auto()
    UP = enum.auto()
    DOWN = enum.auto()
    LEFT = enum.auto()
    RIGHT = enum.auto()


RED = (255, 0, 0)
WHITE = (255, 255, 255)


Color = Tuple[int, int, int]


def gen_colors() -> List[Color]:
    step = 20
    start = 50
    stop = 256 - start
    return [
        (r, g, b)
        for r in range(start, stop, step)
        for g in range(start, stop, step)
        for b in range(start, stop, step)
    ]


COLORS = gen_colors()


def random_color() -> Color:
    return random.choice(COLORS)


@dataclass(frozen=True)
class Point:
    x: int
    y: int

    def __add__(self, other: "Point") -> "Point":
        return Point(self.x + other.x, self.y + other.y)

    def set_x(self, x: int) -> "Point":
        return Point(x, self.y)

    def set_y(self, y: int) -> "Point":
        return Point(self.x, y)


class Apple:
    def __init__(self, point: Point, color: Color):
        self.point = point
        self.color = color


class Snake:
    _MOVES = {
        Direction.NONE: Point(0, 0),
        Direction.UP: Point(0, -RECT_SIZE),
        Direction.DOWN: Point(0, +RECT_SIZE),
        Direction.LEFT: Point(-RECT_SIZE, 0),
        Direction.RIGHT: Point(+RECT_SIZE, 0),
    }

    def __init__(self, points: List[Point], colors: List[Color]):
        if len(points) == 0:
            raise GameException("points must not be empty")
        if len(points) != len(colors):
            raise GameException("points and colors must have the same length")
        self.points = points
        self.size = len(self.points)
        self.direction = Direction.NONE
        self.colors = colors

    def set_direction(self, direction: Direction):
        if direction == Direction.NONE:
            return
        if self._is_reverse_move(direction):
            return

        self.direction = direction

    def _is_reverse_move(self, direction: Direction) -> bool:
        if len(self.points) == 1:
            return False
        current_move = self._MOVES[direction]
        head = self._move(self.head(), current_move)
        return head == self.points[1]

    def current_move(self) -> Point:
        return self._MOVES[self.direction]

    def head(self) -> Point:
        return self.points[0]

    def collide_wall(self) -> bool:
        point = self.head() + self.current_move()

        if point.x < 0 or point.x + RECT_SIZE > WIDTH:
            return True

        if point.y < 0 or point.y + RECT_SIZE > HEIGHT:
            return True

        return False

    def collide_itself(self) -> bool:
        return len(set(self.points)) != len(self.points)

    def move(self):
        if self.current_move() == Point(0, 0):
            return
        self.points.insert(0, self._move(self.head(), self.current_move()))
        self.points = self.points[: self.size]

    def eat(self, apple: Apple) -> bool:
        if self.head() == apple.point:
            self.size += 1
            self.colors.append(apple.color)
            return True
        return False

    def _move(self, point: Point, move: Point) -> Point:
        point = point + move
        point = self._move_through_walls(point)
        return point

    def _move_through_walls(self, point: Point) -> Point:
        if point.x < 0:
            point = point.set_x(WIDTH - RECT_SIZE)
        elif point.x + RECT_SIZE > WIDTH:
            point = point.set_x(0)

        if point.y < 0:
            point = point.set_y(HEIGHT - RECT_SIZE)
        elif point.y + RECT_SIZE > HEIGHT:
            point = point.set_y(0)

        return point


def new_snake() -> Snake:
    w = (WIDTH // RECT_SIZE) // 2
    h = (HEIGHT // RECT_SIZE) // 2
    head = Point(w * RECT_SIZE, h * RECT_SIZE)
    return Snake([head], [RED])


def new_snake_sized(size: int) -> Snake:
    """return a snake folded into a spiral pattern"""
    w = (WIDTH // RECT_SIZE) // 2
    h = (HEIGHT // RECT_SIZE) // 2
    head = Point(w * RECT_SIZE, h * RECT_SIZE)

    moves = [
        [+RECT_SIZE, 0],
        [0, +RECT_SIZE],
        [-RECT_SIZE, 0],
        [0, -RECT_SIZE],
    ]

    points = [head]
    colors = [RED] + [random_color() for _ in range(size - 1)]

    moves = cycle(moves)
    pattern = [val for val in range(2, 100, 2) for _ in (0, 1)]

    for n, move in zip(pattern, moves):
        for _ in range(n):
            if len(points) >= size:
                return Snake(points[::-1], colors)
            i = len(points) - 1
            body = Point(points[i].x + move[0], points[i].y + move[1])
            points.append(body)

    raise GameException("fail to create snake")


def new_apple(snake: Snake) -> Apple:
    free_cells = set()
    for x in range(0, WIDTH // RECT_SIZE):
        for y in range(0, HEIGHT // RECT_SIZE):
            free_cells.add((x, y))

    for s in snake.points:
        x, y = s.x // RECT_SIZE, s.y // RECT_SIZE
        free_cells.discard((x, y))

    if len(free_cells) == 0:
        raise GameException("fail to create new apple")

    h, w = random.choice(list(free_cells))
    point = Point(w * RECT_SIZE, h * RECT_SIZE)
    return Apple(point, random_color())


def display_text(screen: Surface, text: str):
    font_style = pygame.font.SysFont("", 50)
    screen.fill(WHITE)
    surface = font_style.render(text, True, RED)
    h = WIDTH / 2 - surface.get_width() / 2
    w = HEIGHT / 2 - surface.get_height() / 2
    screen.blit(surface, [h, w])
    pygame.display.flip()


def display_multiline_text(screen: Surface, texts: List[str]):
    font_size = min(WIDTH, HEIGHT) // 10
    font_style = pygame.font.SysFont("monospace", font_size, bold=True)
    screen.fill(WHITE)

    surfaces = [font_style.render(text, True, RED) for text in texts]
    total_height = sum([s.get_height() for s in surfaces])
    max_width = max([s.get_width() for s in surfaces])

    height = HEIGHT / 2 - total_height / 2
    width = WIDTH / 2 - max_width / 2
    for surface in surfaces:
        screen.blit(surface, [width, height])
        height += surface.get_height()

    pygame.display.flip()


def draw_point(screen: Surface, color: Color, point: Point):
    pygame.draw.rect(screen, color, Rect(point.x, point.y, RECT_SIZE, RECT_SIZE))


def display_apple(screen: Surface, apple: Apple):
    draw_point(screen, apple.color, apple.point)


def display_snake(screen: Surface, snake: Snake):
    draw_point(screen, snake.colors[0], snake.points[0])
    for c, s in zip(snake.colors[1:], snake.points[1:]):
        draw_point(screen, c, s)


def run_game(screen: Surface, wall=False, body=False, speed=False, size=1):
    logger.info(f"WIDTH={WIDTH}, HEIGHT={HEIGHT}")
    logger.info(f"wall={wall}, body={body} speed={speed} size={size}")

    game_speed = 10
    clock = pygame.time.Clock()

    def init_state():
        snake = new_snake_sized(size)
        apple = new_apple(snake)
        direction = Direction.NONE
        return snake, apple, direction

    snake, apple, direction = init_state()
    game_over = True

    help_msg = [
        "Start     S",
        "Quit    ESC",
    ]

    directions = {
        pygame.K_UP: Direction.UP,
        pygame.K_DOWN: Direction.DOWN,
        pygame.K_LEFT: Direction.LEFT,
        pygame.K_RIGHT: Direction.RIGHT,
    }

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    logger.info("quit")
                    return
                elif event.key == pygame.K_s:
                    logger.info("start")
                    snake, apple, direction = init_state()
                    game_over = False
                elif event.key in directions:
                    logger.info(f"set direction: {direction}")
                    direction = directions[event.key]

        if game_over:
            display_multiline_text(screen, help_msg)
            continue

        snake.set_direction(direction)

        if wall and snake.collide_wall():
            logger.info("collide wall")
            game_over = True
            continue

        if body and snake.collide_itself():
            logger.info("collide itself")
            game_over = True
            continue

        if snake.eat(apple):
            logger.info("eat apple")
            logger.info(f"snake size: {snake.size}")
            try:
                apple = new_apple(snake)
            except GameException:
                logger.info("fail to create new apply")
                game_over = True
                continue
            if speed:
                logger.info(f"increase game speed: {game_speed}")
                game_speed += 1

        snake.move()

        screen.fill(WHITE)
        display_snake(screen, snake)
        display_apple(screen, apple)
        pygame.display.flip()

        clock.tick(game_speed)


def check_positive(value):
    v = int(value)
    if v <= 0:
        raise ArgumentTypeError("must be >= 0")
    return v


if __name__ == "__main__":
    ap = ArgumentParser()
    ap.add_argument(
        "-w",
        "--wall",
        default=False,
        action="store_true",
        help="enable snake collision with walls",
    )
    ap.add_argument(
        "-b",
        "--body",
        default=False,
        action="store_true",
        help="enable snake collision with itself",
    )
    ap.add_argument(
        "-s",
        "--speed",
        default=False,
        action="store_true",
        help="enable speed increase",
    )
    ap.add_argument(
        "-z",
        "--size",
        default=1,
        type=check_positive,
        help="initial length of the snake",
    )
    args = ap.parse_args()

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("snake")
    run_game(screen, wall=args.wall, body=args.body, speed=args.speed, size=args.size)
    pygame.quit()
