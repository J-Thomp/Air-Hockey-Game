import arcade
import math
import random

# Switch width and height for vertical orientation
SCREEN_WIDTH = 500
SCREEN_HEIGHT = 700
SCREEN_TITLE = "Air Hockey"

PADDLE_RADIUS = 30
PUCK_RADIUS = 20
FRICTION = 0.99
WALL_BOUNCE_DAMPING = 0.8

# Adjust goal constants for vertical orientation
GOAL_WIDTH = 200
GOAL_HEIGHT = 10

class AirHockeyGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(arcade.color.BLACK)

        # Player paddles
        self.player1_paddle = None
        self.player2_paddle = None
        
        # Puck
        self.puck = None
        
        # Scores
        self.player1_score = 0
        self.player2_score = 0
        
        # Mouse control variables
        self.player1_holding = False
        self.player2_holding = False
        self.mouse_x = 0
        self.mouse_y = 0

    def setup(self):
        # Create player paddles (adjusted for vertical layout)
        self.player1_paddle = {
            'x': SCREEN_WIDTH // 2,
            'y': SCREEN_HEIGHT // 4,
            'dx': 0,
            'dy': 0,
            'target_x': SCREEN_WIDTH // 2,
            'target_y': SCREEN_HEIGHT // 4
        }
        
        self.player2_paddle = {
            'x': SCREEN_WIDTH // 2,
            'y': 3 * SCREEN_HEIGHT // 4,
            'dx': 0,
            'dy': 0,
            'target_x': SCREEN_WIDTH // 2,
            'target_y': 3 * SCREEN_HEIGHT // 4
        }
        
        # Create puck
        self.puck = {
            'x': SCREEN_WIDTH // 2,
            'y': SCREEN_HEIGHT // 2,
            'dx': 0,
            'dy': 0
        }
        
        # Reset scores
        self.player1_score = 0
        self.player2_score = 0

    def on_draw(self):
        self.clear()
        
        # Draw court
        arcade.draw_lrbt_rectangle_outline(
            left=0, 
            right=SCREEN_WIDTH, 
            top=SCREEN_HEIGHT, 
            bottom=0, 
            color=arcade.color.WHITE, 
            border_width=4
        )
        
        # Draw center line (horizontal now)
        arcade.draw_line(
            0,
            SCREEN_HEIGHT // 2,
            SCREEN_WIDTH,
            SCREEN_HEIGHT // 2,
            arcade.color.WHITE,
            2
        )
        
        # Draw center circle
        arcade.draw_circle_outline(
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2,
            100,
            arcade.color.WHITE,
            2
        )
        
        # Draw goal areas
        # Player 1 goal (bottom)
        arcade.draw_lrbt_rectangle_outline(
            left=SCREEN_WIDTH // 2 - GOAL_WIDTH // 2,
            right=SCREEN_WIDTH // 2 + GOAL_WIDTH // 2,
            top=GOAL_HEIGHT,
            bottom=0,
            color=arcade.color.RED,
            border_width=4
        )
        
        # Player 2 goal (top)
        arcade.draw_lrbt_rectangle_outline(
            left=SCREEN_WIDTH // 2 - GOAL_WIDTH // 2,
            right=SCREEN_WIDTH // 2 + GOAL_WIDTH // 2,
            top=SCREEN_HEIGHT,
            bottom=SCREEN_HEIGHT - GOAL_HEIGHT,
            color=arcade.color.BLUE,
            border_width=4
        )
        
        # Draw paddles
        arcade.draw_circle_filled(
            self.player1_paddle['x'],
            self.player1_paddle['y'],
            PADDLE_RADIUS,
            arcade.color.RED
        )
        
        arcade.draw_circle_filled(
            self.player2_paddle['x'],
            self.player2_paddle['y'],
            PADDLE_RADIUS,
            arcade.color.BLUE
        )
        
        # Draw puck
        arcade.draw_circle_filled(
            self.puck['x'],
            self.puck['y'],
            PUCK_RADIUS,
            arcade.color.GRAY
        )
        
        # Draw scores (adjusted positions)
        arcade.draw_text(
            f"Player 1: {self.player1_score}",
            10,
            10,
            arcade.color.WHITE,
            20
        )
        
        arcade.draw_text(
            f"Player 2: {self.player2_score}",
            10,
            SCREEN_HEIGHT - 30,
            arcade.color.WHITE,
            20
        )

    def update_paddle_position(self, paddle, holding):
        if holding:
            # Calculate distance to target
            dx = paddle['target_x'] - paddle['x']
            dy = paddle['target_y'] - paddle['y']
            
            # Direct movement to target position
            paddle['x'] = paddle['target_x']
            paddle['y'] = paddle['target_y']
            
            # Update velocity for collision physics
            paddle['dx'] = dx
            paddle['dy'] = dy
        else:
            # When not held, gradually slow down
            paddle['dx'] *= 0.8
            paddle['dy'] *= 0.8

    def on_update(self, delta_time):
        # Update paddle positions based on mouse
        self.update_paddle_position(self.player1_paddle, self.player1_holding)
        self.update_paddle_position(self.player2_paddle, self.player2_holding)

        # Constrain paddles to screen and their respective sides
        self.player1_paddle['x'] = max(PADDLE_RADIUS, 
            min(SCREEN_WIDTH - PADDLE_RADIUS, 
                self.player1_paddle['x']))
        self.player1_paddle['y'] = max(PADDLE_RADIUS, 
            min(SCREEN_HEIGHT // 2 - PADDLE_RADIUS, 
                self.player1_paddle['y']))
        
        self.player2_paddle['x'] = max(PADDLE_RADIUS, 
            min(SCREEN_WIDTH - PADDLE_RADIUS, 
                self.player2_paddle['x']))
        self.player2_paddle['y'] = max(SCREEN_HEIGHT // 2 + PADDLE_RADIUS, 
            min(SCREEN_HEIGHT - PADDLE_RADIUS, 
                self.player2_paddle['y']))

        # Move puck
        self.puck['x'] += self.puck['dx']
        self.puck['y'] += self.puck['dy']
        
        # Apply friction to puck
        self.puck['dx'] *= FRICTION
        self.puck['dy'] *= FRICTION
        
        # Puck wall collision
        if (self.puck['x'] - PUCK_RADIUS <= 0 or 
            self.puck['x'] + PUCK_RADIUS >= SCREEN_WIDTH):
            self.puck['dx'] *= -WALL_BOUNCE_DAMPING
        
        if (self.puck['y'] - PUCK_RADIUS <= 0 or 
            self.puck['y'] + PUCK_RADIUS >= SCREEN_HEIGHT):
            self.puck['dy'] *= -WALL_BOUNCE_DAMPING
        
        # Check for goals
        self.check_goals()
        
        # Paddle-puck collision
        self.handle_paddle_puck_collision(
            self.player1_paddle, self.player2_paddle
        )

    def check_goals(self):
        # Check for goals (adjusted for vertical orientation)
        GOAL_LEFT = SCREEN_WIDTH // 2 - GOAL_WIDTH // 2
        GOAL_RIGHT = SCREEN_WIDTH // 2 + GOAL_WIDTH // 2
        
        if (self.puck['y'] <= GOAL_HEIGHT and 
            GOAL_LEFT <= self.puck['x'] <= GOAL_RIGHT):
            # Player 2 scores
            self.player2_score += 1
            self.reset_puck()
        
        elif (self.puck['y'] >= SCREEN_HEIGHT - GOAL_HEIGHT and 
              GOAL_LEFT <= self.puck['x'] <= GOAL_RIGHT):
            # Player 1 scores
            self.player1_score += 1
            self.reset_puck()

    def reset_puck(self):
        # Reset puck to center with random initial velocity
        self.puck = {
            'x': SCREEN_WIDTH // 2,
            'y': SCREEN_HEIGHT // 2,
            'dx': random.uniform(-3, 3),
            'dy': random.uniform(-3, 3)
        }

    # Mouse control methods remain the same
    def on_mouse_motion(self, x, y, dx, dy):
        self.mouse_x = x
        self.mouse_y = y
        
        if self.player1_holding:
            self.player1_paddle['target_x'] = x
            self.player1_paddle['target_y'] = y
        elif self.player2_holding:
            self.player2_paddle['target_x'] = x
            self.player2_paddle['target_y'] = y

    def on_mouse_press(self, x, y, button, modifiers):
        dist_to_player1 = math.sqrt((x - self.player1_paddle['x'])**2 + 
                                  (y - self.player1_paddle['y'])**2)
        dist_to_player2 = math.sqrt((x - self.player2_paddle['x'])**2 + 
                                  (y - self.player2_paddle['y'])**2)
        
        if dist_to_player1 <= PADDLE_RADIUS:
            self.player1_holding = True
            self.player1_paddle['target_x'] = x
            self.player1_paddle['target_y'] = y
        elif dist_to_player2 <= PADDLE_RADIUS:
            self.player2_holding = True
            self.player2_paddle['target_x'] = x
            self.player2_paddle['target_y'] = y

    def on_mouse_release(self, x, y, button, modifiers):
        self.player1_holding = False
        self.player2_holding = False

    def handle_paddle_puck_collision(self, *paddles):
        for paddle in paddles:
            dx = self.puck['x'] - paddle['x']
            dy = self.puck['y'] - paddle['y']
            distance = math.sqrt(dx**2 + dy**2)
            
            if distance <= PADDLE_RADIUS + PUCK_RADIUS:
                angle = math.atan2(dy, dx)
                speed = math.sqrt(self.puck['dx']**2 + self.puck['dy']**2)
                
                self.puck['dx'] = (math.cos(angle) * speed * 1.2 + 
                                 paddle['dx'] * 0.5)
                self.puck['dy'] = (math.sin(angle) * speed * 1.2 + 
                                 paddle['dy'] * 0.5)

def main():
    window = AirHockeyGame()
    window.setup()
    arcade.run()

if __name__ == "__main__":
    main()