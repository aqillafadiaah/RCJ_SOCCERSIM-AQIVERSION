import json
import math

TIME_STEP = 32
ROBOT_NAMES = ["B1", "B2", "B3", "Y1", "Y2", "Y3"]
N_ROBOTS = len(ROBOT_NAMES)


class RCJSoccerRobot:
    def __init__(self, robot):
        self.robot = robot
        self.name = self.robot.getName()
        self.team = self.name[0]
        self.player_id = int(self.name[1])

        self.receiver = self.robot.getDevice("supervisor receiver")
        self.receiver.enable(TIME_STEP)

        self.team_emitter = self.robot.getDevice("team emitter")
        self.team_receiver = self.robot.getDevice("team receiver")
        self.team_receiver.enable(TIME_STEP)

        self.ball_receiver = self.robot.getDevice("ball receiver")
        self.ball_receiver.enable(TIME_STEP)

        self.gps = self.robot.getDevice("gps")
        self.gps.enable(TIME_STEP)

        self.compass = self.robot.getDevice("compass")
        self.compass.enable(TIME_STEP)

        self.sonar_left = self.robot.getDevice("distancesensor left")
        self.sonar_left.enable(TIME_STEP)
        self.sonar_right = self.robot.getDevice("distancesensor right")
        self.sonar_right.enable(TIME_STEP)
        self.sonar_front = self.robot.getDevice("distancesensor front")
        self.sonar_front.enable(TIME_STEP)
        self.sonar_back = self.robot.getDevice("distancesensor back")
        self.sonar_back.enable(TIME_STEP)

        self.left_motor = self.robot.getDevice("left wheel motor")
        self.right_motor = self.robot.getDevice("right wheel motor")

        self.left_motor.setPosition(float("+inf"))
        self.right_motor.setPosition(float("+inf"))

        self.left_motor.setVelocity(0.0)
        self.right_motor.setVelocity(0.0)

    def parse_supervisor_msg(self, data: str) -> dict:
        return json.loads(data)

    def get_new_data(self) -> dict:
        data = self.receiver.getString()
        self.receiver.nextPacket()
        return self.parse_supervisor_msg(data)

    def is_new_data(self) -> bool:
        return self.receiver.getQueueLength() > 0

    def parse_team_msg(self, data: str) -> dict:
        return json.loads(data)

    def get_new_team_data(self) -> dict:
        data = self.team_receiver.getString()
        self.team_receiver.nextPacket()
        return self.parse_team_msg(data)

    def is_new_team_data(self) -> bool:
        return self.team_receiver.getQueueLength() > 0

    # --- PERBAIKAN: Tambahkan has_ball di sini ---
    def send_data_to_team(self, robot_id: int, has_ball: bool = False) -> None:
        """Send data to the team including ball possession status"""
        data = {
            "robot_id": robot_id,
            "has_ball": has_ball
        }
        self.team_emitter.send(json.dumps(data))
    # ---------------------------------------------

    def get_new_ball_data(self) -> dict:
        _ = self.ball_receiver.getString()
        data = {
            "direction": self.ball_receiver.getEmitterDirection()[:3],
            "strength": self.ball_receiver.getSignalStrength(),
        }
        self.ball_receiver.nextPacket()
        return data

    def is_new_ball_data(self) -> bool:
        return self.ball_receiver.getQueueLength() > 0

    def get_gps_coordinates(self) -> list:
        gps_values = self.gps.getValues()
        return [gps_values[0], gps_values[1]]

    def get_compass_heading(self) -> float:
        """Mengambil data mentah kompas dalam radian"""
        compass_values = self.compass.getValues()
        # KHUSUS TIM BIRU (Menyerang ke Bawah/Selatan)
        # Offset +1.57 (90 derajat)
        rad = math.atan2(compass_values[0], compass_values[1]) + 1.57
        
        if rad < -math.pi: rad += 2 * math.pi
        return rad

    def get_sonar_values(self) -> dict:
        return {
            "left": self.sonar_left.getValue(),
            "right": self.sonar_right.getValue(),
            "front": self.sonar_front.getValue(),
            "back": self.sonar_back.getValue(),
        }

    def run(self):
        raise NotImplementedError