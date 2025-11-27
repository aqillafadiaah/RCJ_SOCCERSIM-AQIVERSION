import utils
from rcj_soccer_robot import RCJSoccerRobot, TIME_STEP

class MyRobot2(RCJSoccerRobot):
    def run(self):
        # Setup kickoff timer...
        kickoff_start_time = None
        kickoff_duration = 2.0

        while self.robot.step(TIME_STEP) != -1:
            if self.is_new_data():
                current_time = self.robot.getTime()
                if kickoff_start_time is None: kickoff_start_time = current_time

                left_speed = 0
                right_speed = 0
                
                # Baca Sonar
                sonar = self.get_sonar_values()
                is_blocked_front = 0 < sonar['front'] < 60 # Jarak bahaya

                # Komunikasi Tim
                striker_has_ball = False
                while self.is_new_team_data():
                    msg = self.get_new_team_data()
                    if msg.get('has_ball') and msg['robot_id'] == 1:
                        striker_has_ball = True

                i_have_ball = False
                if self.is_new_ball_data():
                    ball_data = self.get_new_ball_data()
                    if ball_data["strength"] > 0.5: i_have_ball = True

                    # LOGIKA GERAK
                    if is_blocked_front:
                        # Jika macet di depan, mundur sedikit untuk kasih ruang
                        left_speed = -6
                        right_speed = -8
                        
                    elif ball_data["strength"] > 0.05:
                        # ... (Logika Kejar Bola Normal & Slow Start) ...
                        # Copy logika normal Robot 2 Anda di sini
                        # Pastikan memasukkan logika kickoff delay
                        
                        direction = utils.get_direction(ball_data["direction"])
                        
                        # Speed Control
                        time_since_start = current_time - kickoff_start_time
                        current_max_speed = 4 if time_since_start < kickoff_duration else 8
                        
                        if direction == 0:
                            left_speed = current_max_speed
                            right_speed = current_max_speed
                        else:
                            turn_speed = current_max_speed * 0.8
                            left_speed = direction * turn_speed
                            right_speed = direction * -turn_speed
                            
                    else:
                        left_speed = 0
                        right_speed = 0

                else:
                    left_speed = -4
                    right_speed = 4

                self.left_motor.setVelocity(left_speed)
                self.right_motor.setVelocity(right_speed)
                self.send_data_to_team(self.player_id, has_ball=i_have_ball)