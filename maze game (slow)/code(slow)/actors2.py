from __future__ import annotations
import pygame
from typing import Optional
from settings import *


class Actor:
    """
    A class to represent all the game's actors. This class includes any
    attributes/methods that every actor in the game must have.

    This is an abstract class. Only subclasses should be instantiated.

    === Public Attributes ===
    x:
        x coordinate of this actor's location on the stage
    y:
        y coordinate of this actor's location on the stage
    icon:
        the image representing this actor
    """
    x: int
    y: int
    icon: pygame.Surface

    def __init__(self, icon_file, x, y):
        """Initialize an actor with the given image <icon_file> and the
        given <x> and <y> position on the game's stage.
        """

        self.x, self.y = x, y
        self.icon = pygame.image.load(icon_file)

    def move(self, game: 'Game') -> None:
        """Move this actor by taking one step of its animation."""

        raise NotImplementedError


class Player(Actor):
    """
    A class to represent a Player in the game.
    """
    # === Private Attributes ===
    # _stars_collected:
    #       the number of stars the player has collected so far
    # _last_event:
    #       keep track of the last key the user pushed down
    # _smooth_move:
    #       represent on/off status for smooth player movement

    x: int
    y: int
    icon: pygame.Surface
    _stars_collected: int
    _last_event: Optional[int]
    _smooth_move: bool

    def __init__(self, icon_file: str, x: int, y: int) -> None:
        """Initalize a Player with the given image <icon_file> at the position
        <x> and <y> on the stage."""

        super().__init__(icon_file, x, y)
        self._stars_collected = 0
        self._last_event = None  # This is used for precise movement
        self._smooth_move = False  # Turn this on for smooth movement

    def set_smooth_move(self, status: bool) -> None:
        """
        Set the <status> of whether or not the player will move smoothly.
        """

        self._smooth_move = status

    def get_star_count(self) -> int:
        """
        Return the number of stars collected.
        """

        return self._stars_collected

    def register_event(self, event: int) -> None:
        """
        Keep track of the last key <event> the user made.
        """

        self._last_event = event

    def move(self, game: 'Game') -> None:
        """
        Move the player on the <game>'s stage based on keypresses.
        """

        evt = self._last_event

        if self._last_event:
            dx, dy = 0, 0
            if self._smooth_move:

                actor_left, actor_right = game.get_actor(self.x - 1, self.y), game.get_actor(self.x + 1, self.y)
                actor_up, actor_down = game.get_actor(self.x, self.y - 1), game.get_actor(self.x, self.y + 1)

                if game.keys_pressed[pygame.K_LEFT] or game.keys_pressed[pygame.K_a]:
                    if not isinstance(actor_left, Wall):
                        dx -= 1
                        if isinstance(actor_left, Box):
                            if not actor_left.be_pushed(game, dx, dy):
                                dx += 1
                if game.keys_pressed[pygame.K_RIGHT] or game.keys_pressed[pygame.K_d]:
                    if not isinstance(actor_right, Wall):
                        dx += 1
                        if isinstance(actor_right, Box):
                            if not actor_right.be_pushed(game, dx, dy):
                                dx -= 1
                if game.keys_pressed[pygame.K_UP] or game.keys_pressed[pygame.K_w]:
                    if not isinstance(actor_up, Wall):
                        dy -= 1
                        if isinstance(actor_up, Box):
                            if not actor_up.be_pushed(game, dx, dy):
                                dy += 1
                if game.keys_pressed[pygame.K_DOWN] or game.keys_pressed[pygame.K_s]:
                    if not isinstance(actor_down, Wall):
                        dy += 1
                        if isinstance(actor_down, Box):
                            if not actor_down.be_pushed(game, dx, dy):
                                dy -= 1

            else:  # Precise movement used by the squishy monster level
                if evt == pygame.K_LEFT or evt == pygame.K_a:
                    dx -= 1
                if evt == pygame.K_RIGHT or evt == pygame.K_d:
                    dx += 1
                if evt == pygame.K_UP or evt == pygame.K_w:
                    dy -= 1
                if evt == pygame.K_DOWN or evt == pygame.K_s:
                    dy += 1
                self._last_event = None

            new_x, new_y = self.x + dx, self.y + dy

            if isinstance(game.get_actor(new_x, new_y), Star):
                self._stars_collected += 1
                game.remove_actor(game.get_actor(new_x, new_y))
            if isinstance(game.get_actor(new_x, new_y), Key):
                game.key_collected = True
                game.remove_actor(game.get_actor(new_x, new_y))
            self.x, self.y = new_x, new_y

# === Classes for immobile objects === #


class Star(Actor):
    """
    A class to represent a Star in the game.
    """
    x: int
    y: int
    icon: pygame.Surface

    def move(self, game: 'Game') -> None:
        """
        A Star cannot move, so do nothing.
        """

        pass


class Wall(Actor):
    """
    A class to represent a Wall in the game.
    """
    x: int
    y: int
    icon: pygame.Surface

    def move(self, game: 'Game') -> None:
        """
        A Wall cannot move, so do nothing.
        """

        pass


# === Classes for movable objects === #

class Box(Actor):
    """
    A class to represent a Box in the game.
    """
    x: int
    y: int
    icon: pygame.Surface

    def move(self, game: 'Game') -> None:
        """
        A Box cannot move, so do nothing.
        """

        pass

    def be_pushed(self, game: 'Game', dx: int, dy: int) -> bool:
        """
        Move the box in the direction that it is being pushed,
        represented by <dx> and <dy> if the way is not blocked by a wall.
        If there is another box in the way, move both boxes at once. maybe: use be_pushed (recursion)
        If there is a monster in the way, squish the monster.
        Return True if a move was possible, and False otherwise.
        """

        new_x, new_y = self.x + dx, self.y + dy
        pushed = False
        actor = game.get_actor(new_x, new_y)
        if not isinstance(actor, Wall):
            pushed = True
            self.x, self.y = new_x, new_y
            if isinstance(actor, Box):
                actor.be_pushed(game, dx, dy)
            if isinstance(actor, Monster):
                actor.die(game)

        return pushed

# === Classes for monsters === #


class Monster(Actor):
    """
    A class to represent monsters that kill the player upon contact.
    """
    # === Private attributes ===
    # _dx:
    #   the horizontal distance this monster will move during each step
    # _dy:
    #   the vertical distance this monster will move during each step
    # _delay:
    #   the speed the monster moves at
    # _delay_count:
    #   used to keep track of the monster's delay in speed
    x: int
    y: int
    icon: pygame.Surface
    _dx: float
    _dy: float
    _delay: int
    _delay_count: int

    def __init__(self, icon_file: str, x: int, y: int, dx: float, dy: float) -> None:
        """Initalize a monster with the given <icon_file> as its image,
        <x> and <y> as its position, and <dx> and <dy> being how much
        it moves by during each animation in the game. The monster also
        has a delay which could optionally be used to slow it down."""

        super().__init__(icon_file, x, y)
        self._dx = dx
        self._dy = dy
        self._delay = 5
        self._delay_count = 1

    def move(self, game: 'Game') -> None:
        """Move the monster by taking one step in its animation."""

        raise NotImplementedError

    def check_player_death(self, game: 'Game') -> None:
        """Make the game over if this monster has hit the player."""

        if isinstance(game.get_actor(self.x, self.y), Player):
            game.game_over()
        if game.player:
            if self.x == game.player.x:
                if self.y == game.player.y:
                    game.game_over()


class GhostMonster(Monster):
    """
    A class to represent a ghost in the game who chases the Player.
    """
    x: int
    y: int
    icon: pygame.Surface
    _dx: float
    _dy: float
    _delay: int
    _delay_count: int

    def __init__(self, icon_file: str, x: int, y: int) -> None:
        """Initalize a ghost with the given <icon_file> and <x> and <y>
        as its position."""

        # Set movement with each animation to be 0.5
        super().__init__(icon_file, x, y, 0.5, 0.5)  # uses Monster.__init__

    def move(self, game: 'Game') -> None:
        """
        Move the ghost on the <game>'s screen based on the player's location.
        Check if the ghost has caught the player after each move.
        """

        if game.player.x > self.x:
            self.x += self._dx * 0.25
        elif game.player.x < self.x:
            self.x -= self._dx * 0.25
        elif game.player.y > self.y:
            self.y += self._dy * 0.25
        elif game.player.y < self.y:
            self.y -= self._dy * 0.25

        self.check_player_death(game)


class SquishyMonster(Monster):
    """
    A class to represent a monster in the game that can kill the player, or
    get squished by a box.
    """
    x: int
    y: int
    icon: pygame.Surface
    _dx: float
    _dy: float
    _delay: int
    _delay_count: int

    def __init__(self, icon_file: str, x: int, y: int) -> None:
        """Initalize a monster with the given <icon_file> and <x> and <y>
        as its position."""

        # Set movement with each animation to be 1 step
        super().__init__(icon_file, x, y, 1, 1)  # uses Monster.__init__

    def move(self, game: 'Game') -> None:
        """
        Move one step, if possible. If the way is blocked, bounce back in
        the opposite direction. After each move, check if the player has been
        hit.
        """

        if self._delay_count == 0:  # delay the monster's movement
            if not (isinstance(game.get_actor(self.x + self._dx, self.y + self._dy), Wall) or isinstance(game.get_actor(self.x + self._dx, self.y + self._dy), Box)):
                self.x += self._dx
                self.y += self._dy
            if (isinstance(game.get_actor(self.x + self._dx, self.y + self._dy), Wall) or isinstance(game.get_actor(self.x + self._dx, self.y + self._dy), Box)):
                self._dx = -1 * self._dx
                self._dy = -1 * self._dy

        self._delay_count = (self._delay_count + 1) % self._delay

        self.check_player_death(game)

    def die(self, game: 'Game') -> None:
        """Remove this monster from the <game>."""
        game.monster_count -= 1
        game.remove_actor(self)


class SquishyMonster2(SquishyMonster):
    """
    A class to represent a monster in the game that can kill the player, or
    get squished by a box.
    """
    x: int
    y: int
    icon: pygame.Surface
    _dx: float
    _dy: float
    _delay: int
    _delay_count: int

    def move(self, game: 'Game') -> None:
        """
        Move one step horizontally, if possible. If the way is blocked, bounce back in
        the opposite direction. After each move, check if the player has been
        hit.
        """

        if self._delay_count == 0:
            if not (isinstance(game.get_actor(self.x + self._dx, self.y), Wall) or isinstance(game.get_actor(self.x + self._dx, self.y), Box)):
                self.x += self._dx
            if (isinstance(game.get_actor(self.x + self._dx, self.y), Wall) or isinstance(game.get_actor(self.x + self._dx, self.y), Box)):
                self._dx = -1 * self._dx

        self._delay_count = (self._delay_count + 1) % self._delay

        self.check_player_death(game)


class SquishyMonster3(SquishyMonster):
    """
    A class to represent a monster in the game that can kill the player, or
    get squished by a box.
    """
    x: int
    y: int
    icon: pygame.Surface
    _dx: float
    _dy: float
    _delay: int
    _delay_count: int

    def move(self, game: 'Game') -> None:
        """
        Move one step vertically, if possible. If the way is blocked, bounce back in
        the opposite direction. After each move, check if the player has been
        hit.
        """

        actor = game.get_actor(self.x, self.y + self._dy)
        if self._delay_count == 0:
            if not (isinstance(actor, Wall) or isinstance(actor, Box) or isinstance(actor, SquishyMonster)):
                self.y += self._dy
            if (isinstance(actor, Wall) or isinstance(actor, Box)):
                self._dy = -1 * self._dy

        self._delay_count = (self._delay_count + 1) % self._delay

        self.check_player_death(game)


class Door(Actor):
    """
    A class to represent a Door in the game.
    """
    x: int
    y: int
    icon: pygame.Surface

    def move(self, game: 'Game') -> None:
        """
        A Door cannot move, so do nothing.
        """

        pass


class Key(Actor):
    """
    A class to represent a Key in the game.
    """
    x: int
    y: int
    icon: pygame.Surface

    def move(self, game: 'Game') -> None:
        """
        A Key cannot move, so do nothing.
        """

        pass
