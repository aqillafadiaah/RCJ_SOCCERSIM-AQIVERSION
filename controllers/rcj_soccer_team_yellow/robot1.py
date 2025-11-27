import utils
from rcj_soccer_robot import RCJSoccerRobot, TIME_STEP

class MyRobot1(RCJSoccerRobot):
    def run(self):
        while self.robot.step(TIME_STEP) != -1:
            if self.is_new_data():
                left_speed = 0
                right_speed = 0
                
                if self.is_new_ball_data():
                    ball_data = self.get_new_ball_data()
                    direction = utils.get_direction(ball_data["direction"])
                    
                    # LOGIKA BRASIL: GAS POL!
                    if direction == 0:
                        left_speed = 10
                        right_speed = 10
                    else:
                        # Belok tajam dan cepat
                        left_speed = direction * 9
                        right_speed = direction * -9
                else:
                    # Jika bola hilang, putar cepat cari bola
                    left_speed = -6
                    right_speed = 6

                self.left_motor.setVelocity(left_speed)
                self.right_motor.setVelocity(right_speed)
                self.send_data_to_team(self.player_id)