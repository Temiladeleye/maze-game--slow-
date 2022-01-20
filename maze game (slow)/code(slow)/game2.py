from __future__ import annotations
from typing import Optional, List
from actors2 import *
import pygame
import random

LEVEL_MAPS = ["maze1.txt", "maze3.txt", "final_maze.txt"]


def load_map(filename: str) -> List[List[str]]:
    """
    Load the map data from the given filename and return as a list of lists.
    """

    with open(filename) as f:
        map_data = [line.split() for line in f]
    return map_data


class Game:
    """
    This class represents the main game.

    === Public Attributes ===
    screen: the screen that the game will be displayed
    player: the player of this game
    keys_pressed: the keys pressed to control the player in this game
    stage_width: the width of the screen of this game
    stage_height: the height of the screen of this game
    size: the size of the screen that this game is displayed
    goal_message: the objective of this game that the player needs to achieve to win
    goal_stars: the number of stars the player needs to collect to win the game
    monster_count: the number of monsters that has been added to this game
    key_collected: true iff the player has collected the key in level 2 of this game

    === Private Attributes ===
    _running: true when the game is running
    _level: the level of this game the player is currently on
    _max_level: the maxium level of this game
    _actors: the actors in this game
    """
    # Attribute types
    screen: pygame.Surface
    player: Player
    keys_pressed: str
    stage_width: float
    stage_height: float
    size: int
    goal_message: str
    goal_stars: int
    monster_count: int
    key_collected: bool
    _running: bool
    _level: int
    _max_level: int
    _actors: Actor

    def __init__(self) -> None:
        """
        Initialize a game that has a display screen and game actors.
        """

        self._running = False
        self._level = 0
        self._max_level = len(LEVEL_MAPS) - 1
        self.screen = None
        self.player = None
        self.keys_pressed = None

        # Attributes that get set during level setup
        self._actors = None
        self.stage_width, self.stage_height = 0, 0
        self.size = None
        self.goal_message = None

        # Attributes that are specific to certain levels
        self.goal_stars = 0
        self.monster_count = 0
        self.key_collected = False

        # Method that takes care of level setup
        self.setup_current_level()

    def get_level(self) -> int:
        """
        Return the current level the game is at.
        """

        return self._level

    def set_player(self, player: Player) -> None:
        """
        Set the game's player to be the given <player> object.
        """

        self.player = player

    def add_actor(self, actor: Actor) -> None:
        """
        Add the given <actor> to the game's list of actors.
        """

        self._actors.append(actor)

    def remove_actor(self, actor: Actor) -> None:
        """
        Remove the given <actor> from the game's list of actors.
        """

        self._actors.remove(actor)

    def get_actor(self, x: int, y: int) -> Optional[Actor]:
        """
        Return the actor object that exists in the location given by
        <x> and <y>. If no actor exists in that location, return None.
        """

        for actor in self._actors:
            if actor.x == x:
                if actor.y == y:
                    return actor

    def on_init(self) -> None:
        """
        Initialize the game's screen, and begin running the game.
        """

        pygame.init()
        self.screen = pygame.display.set_mode(self.size, pygame.HWSURFACE | pygame.DOUBLEBUF)
        self._running = True

    def on_event(self, event: pygame.Event) -> None:
        """
        React to the given <event> as appropriate.
        """

        if event.type == pygame.QUIT:
            self._running = False
        elif event.type == pygame.KEYDOWN:
            self.player.register_event(event.key)

    def game_won(self) -> bool:
        """
        Return True iff the game has been won, according to the current level.
        """
        if self._level == 0:
            if isinstance(self.get_actor(self.player.x, self.player.y), Door):
                if not self.player._stars_collected >= self.goal_stars:
                    print("Door won't open unless you collect enough stars")
                    self.player.x -= 1
                    return False
                else:
                    return True
        if self._level == 1:
            if isinstance(self.get_actor(self.player.x, self.player.y), Door):
                if not self.monster_count == 0:
                    print("Door won't open unless all the monsters are dead")
                    self.player.x -= 1
                    return False
                else:
                    return True
        if self._level == 2:
            if isinstance(self.get_actor(self.player.x, self.player.y), Door):
                if not self.monster_count == 0:
                    print("Door won't open unless all the monsters are dead and you get the key")
                    self.player.x -= 1
                    return False
                elif not self.key_collected:
                    print("Door won't open unless all the monsters are dead and you get the key")
                    self.player.x -= 1
                    return False
                else:
                    return True

    def on_loop(self) -> None:
        """
        Move all actors in the game as appropriate.
        Check for win/lose conditions and stop the game if necessary.
        """
        self.keys_pressed = pygame.key.get_pressed()
        for actor in self._actors:
            actor.move(self)

        if isinstance(self.player, Actor):
            if self.game_won():
                if self._level == self._max_level:
                    print("Congratlations, you won!")
                    self._running = False
                elif isinstance(self.get_actor(self.player.x, self.player.y), Door):
                    self._level += 1
                    self.setup_current_level()

        if isinstance(self.player, type(None)):
            print("You lose! :( Better luck next time.")
            self._running = False

    def on_render(self) -> None:
        """
        Render all the game's elements onto the screen.
        """

        self.screen.fill(BLACK)
        for a in self._actors:
            rect = pygame.Rect(a.x * ICON_SIZE, a.y * ICON_SIZE, ICON_SIZE, ICON_SIZE)
            self.screen.blit(a.icon, rect)

        font = pygame.font.Font('freesansbold.ttf', 9)
        text = font.render(self.goal_message, True, WHITE, BLACK)
        textRect = text.get_rect()
        textRect.center = (self.stage_width * ICON_SIZE // 2,
                           (self.stage_height + 0.5) * ICON_SIZE)
        self.screen.blit(text, textRect)

        pygame.display.flip()

    def on_cleanup(self) -> None:
        """
        Clean up and close the game.
        """

        pygame.quit()

    def on_execute(self) -> None:
        """
        Run the game until the game ends.
        """

        self.on_init()

        while self._running:
            pygame.time.wait(100)
            for event in pygame.event.get():
                self.on_event(event)
            self.on_loop()
            self.on_render()

        self.on_cleanup()

    def game_over(self) -> None:
        """
        Set the game as over (remove the player from the game).
        """

        self.player = None

    def setup_current_level(self):
        """
        Set up the current level of the game.
        """

        data = load_map(
            "../data/" + LEVEL_MAPS[self._level])  # Set the file where maze data is stored

        if self._level == 0:
            self.setup_ghost_game(data)
        elif self._level == 1:
            self.setup_squishy_monster_game(data)
        elif self._level == 2:
            self.setup_level2_game(data)

    def setup_ghost_game(self, data) -> None:
        """
        Set up a game with a ghost that chases the player, and stars to collect.
        """

        w = len(data[0])
        h = len(
            data) + 1

        self._actors = []
        self.stage_width, self.stage_height = w, h - 1
        self.size = (w * ICON_SIZE, h * ICON_SIZE)

        player, chaser = None, None

        for i in range(len(data)):
            for j in range(len(data[i])):
                key = data[i][j]
                if key == 'P':
                    player = Player("../images/boy-24.png", j, i)
                elif key == 'C':
                    chaser = GhostMonster("../images/ghost-24.png", j, i)
                elif key == 'X':
                    self.add_actor(Wall("../images/wall-24.png", j, i))
                elif key == 'D':
                    self.add_actor(Door("../images/door-24.png", j, i))

        self.set_player(player)
        self.add_actor(player)
        player.set_smooth_move(True)
        self.add_actor(chaser)
        self.goal_stars = 5
        self.goal_message = "Objective: Collect {}".format(self.goal_stars) + \
            " stars before the ghost gets you and head for the door"

        num_stars = 0
        while num_stars < 7:
            x = random.randrange(self.stage_width)
            y = random.randrange(self.stage_height)
            if not isinstance(self.get_actor(x, y), Actor):
                self.add_actor(Star("../images/star-24.png", x, y))
                num_stars += 1

    def setup_squishy_monster_game(self, data) -> None:
        """
        Set up a game with monsters that the player must squish with boxes.
        """

        w = len(data[0])
        h = len(
            data) + 1

        self._actors = []
        self.stage_width, self.stage_height = w, h - 1
        self.size = (w * ICON_SIZE, h * ICON_SIZE)
        self.goal_message = "Objective: Squish all the monsters with the boxes " \
            + " and head for the door"

        player, chaser = None, None

        for i in range(len(data)):
            for j in range(len(data[i])):
                key = data[i][j]
                if key == 'P':
                    player = Player("../images/boy-24.png", j, i)
                elif key == 'M':
                    chaser = SquishyMonster("../images/monster-24.png", j, i)
                    self.add_actor(chaser)
                    self.monster_count += 1
                elif key == 'X':
                    self.add_actor(Wall("../images/wall-24.png", j, i))
                elif key == 'D':
                    self.add_actor(Door("../images/door-24.png", j, i))

        self.set_player(player)
        self.add_actor(player)
        player.set_smooth_move(True)

        num_boxes = 0
        while num_boxes < 12:
            x = random.randrange(self.stage_width)
            y = random.randrange(self.stage_height)
            if not isinstance(self.get_actor(x, y), Actor):
                self.add_actor(Box("../images/box-24.png", x, y))
                num_boxes += 1

    def setup_level2_game(self, data) -> None:
        """
        Set up a game with monsters that the player must squish with boxes and collect a key to win.
        """

        w = len(data[0])
        h = len(
            data) + 1
        self._actors = []
        self.stage_width, self.stage_height = w, h - 1
        self.size = (w * ICON_SIZE, h * ICON_SIZE)
        self.goal_message = "Objective: Squish all the monsters with the boxes, " \
            + "get the key and head for the door"

        player, chaser, chaser2 = None, None, None
        for i in range(len(data)):
            for j in range(len(data[i])):
                key = data[i][j]
                if key == 'P':
                    player = Player("../images/boy-24.png", j, i)
                elif key == 'K':
                    self.add_actor(Key("../images/key-24.png", j, i))
                elif key == 'M':
                    chaser = SquishyMonster2("../images/monster2-24.png", j, i)
                    self.add_actor(chaser)
                    self.monster_count += 1
                elif key == 'N':
                    chaser2 = SquishyMonster3("../images/monster3-24.png", j, i)
                    self.add_actor(chaser2)
                    self.monster_count += 1
                elif key == 'X':
                    self.add_actor(Wall("../images/wall-24.png", j, i))
                elif key == 'D':
                    self.add_actor(Door("../images/door-24.png", j, i))

        self.set_player(player)
        self.add_actor(player)
        player.set_smooth_move(True)

        num_boxes = 0
        while num_boxes < 12:
            x = random.randrange(self.stage_width)
            y = random.randrange(self.stage_height)
            if not isinstance(self.get_actor(x, y), Actor):
                self.add_actor(Box("../images/box-24.png", x, y))
                num_boxes += 1
