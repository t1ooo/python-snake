import unittest

from snake import (
    Snake,
    Apple,
    Point,
    RED,
    WHITE,
    RECT_SIZE,
    Direction,
    HEIGHT,
    WIDTH,
)


class SnakeGameTests(unittest.TestCase):
    def test_set_direction(self):
        def new_snake():
            return Snake([Point(0, 0), Point(RECT_SIZE, 0)], [RED, RED])

        # should set
        snake = new_snake()
        snake.set_direction(Direction.UP)
        self.assertEqual(snake.direction, Direction.UP)

        snake = new_snake()
        snake.set_direction(Direction.LEFT)
        self.assertEqual(snake.direction, Direction.LEFT)

        snake = new_snake()
        snake.set_direction(Direction.DOWN)
        self.assertEqual(snake.direction, Direction.DOWN)

        # reverse move, shouldn't set
        snake = new_snake()
        snake.set_direction(Direction.RIGHT)
        self.assertEqual(snake.direction, Direction.NONE)

    def test_collide_wall(self):
        snake = Snake([Point(0, 0)], [RED])

        # should collide with wall
        snake.set_direction(Direction.LEFT)
        self.assertTrue(snake.collide_wall())

        snake.set_direction(Direction.UP)
        self.assertTrue(snake.collide_wall())

        # shouldn't collide with wall
        snake.set_direction(Direction.RIGHT)
        self.assertFalse(snake.collide_wall())

        snake.set_direction(Direction.DOWN)
        self.assertFalse(snake.collide_wall())

    def test_collide_itself(self):
        # shouldn't collide itself
        snake = Snake(
            [Point(0, 0), Point(RECT_SIZE, 0), Point(RECT_SIZE * 2, 0)], [RED, RED, RED]
        )
        self.assertFalse(snake.collide_itself())

        # should collide itself
        snake.points += [Point(0, 0)]
        self.assertTrue(snake.collide_itself())

    def test_move(self):
        def new_snake():
            return Snake([Point(0, 0)], [RED])

        # shouldn't move with Direction.NONE
        snake = new_snake()
        snake.set_direction(Direction.NONE)
        snake.move()
        self.assertEqual(snake.points, [Point(0, 0)])

        # should simple move
        snake = new_snake()
        snake.set_direction(Direction.RIGHT)
        snake.move()
        self.assertEqual(snake.points, [Point(RECT_SIZE, 0)])

        snake = new_snake()
        snake.set_direction(Direction.DOWN)
        snake.move()
        self.assertEqual(snake.points, [Point(0, RECT_SIZE)])

        # should move through walls
        snake = new_snake()
        snake.set_direction(Direction.UP)
        snake.move()
        self.assertEqual(snake.points, [Point(0, HEIGHT - RECT_SIZE)])

        snake = new_snake()
        snake.set_direction(Direction.LEFT)
        snake.move()
        self.assertEqual(snake.points, [Point(WIDTH - RECT_SIZE, 0)])

        # the position of the second segment should be equal to the previous position of the first
        snake = Snake([Point(0, RECT_SIZE), Point(0, 0)], [RED, RED])
        snake.set_direction(Direction.DOWN)
        snake.move()
        self.assertEqual(snake.points, [Point(0, RECT_SIZE * 2), Point(0, RECT_SIZE)])

    def test_eat(self):
        # should eat
        snake = Snake([Point(0, 0)], [RED])
        apple = Apple(Point(0, 0), WHITE)
        self.assertTrue(snake.eat(apple))
        self.assertEqual(snake.size, 2)
        self.assertEqual(snake.colors, [RED, WHITE])

        # different position, should't eat
        snake = Snake([Point(0, 0)], [RED])
        apple = Apple(Point(RECT_SIZE, RECT_SIZE), WHITE)
        self.assertFalse(snake.eat(apple))
        self.assertEqual(snake.size, 1)
        self.assertEqual(snake.colors, [RED])


if __name__ == "__main__":
    unittest.main()
