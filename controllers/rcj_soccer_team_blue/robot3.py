# File: robot3.py (Kiper Smooth - Anti Jitter & Anti Spin)
import math
import utils
from rcj_soccer_robot import RCJSoccerRobot, TIME_STEP

class MyRobot3(RCJSoccerRobot):
    def run(self):
        self.left_motor.setVelocity(0)
        self.right_motor.setVelocity(0)
        
        # --- KONFIGURASI HALUS ---
        # 1. Batas Gawang (GPS X)
        LIMIT_X = 0.22  
        
        # 2. Target Heading (Wajib 0 / Menghadap Timur)
        TARGET_HEADING = 0.0
        
        # 3. Anti-Keder (Gain Koreksi)
        # TURUNKAN ANGKA INI. 
        # Jika 15.0 bikin getar, kita pakai 2.0 atau 3.0 saja.
        HEADING_GAIN = 3.0 
        
        # 4. Toleransi Sudut (Deadzone)
        # Jika miring kurang dari 3 derajat (0.05 rad), anggap lurus.
        # Ini mencegah robot "gelisah" membetulkan hal kecil.
        HEADING_TOLERANCE = 0.05

        while self.robot.step(TIME_STEP) != -1:
            if self.is_new_data():
                
                # ==========================================================
                # 1. HEADING CALCULATION (ANTI-SPIN 180)
                # ==========================================================
                compass_val = self.compass.getValues()
                current_heading = math.atan2(compass_val[0], compass_val[1])
                
                # Hitung selisih sudut
                heading_error = TARGET_HEADING - current_heading
                
                # --- RUMUS PENTING: ANGLE WRAP FIX ---
                # Memastikan robot mengambil jalan terpendek.
                # Jika error > 180 derajat, kurangi 360.
                while heading_error > math.pi: 
                    heading_error -= 2 * math.pi
                while heading_error < -math.pi: 
                    heading_error += 2 * math.pi
                
                # --- FILTER KEDER (DEADZONE) ---
                # Jika error sangat kecil, nol-kan saja (biar robot tenang)
                if abs(heading_error) < HEADING_TOLERANCE:
                    heading_error = 0
                
                # Hitung nilai koreksi motor (Lembut)
                correction = heading_error * HEADING_GAIN

                # ==========================================================
                # 2. LOGIKA GERAK (SLIDING)
                # ==========================================================
                base_speed = 0
                
                if self.is_new_ball_data():
                    ball_data = self.get_new_ball_data()
                    
                    # Sudut bola relatif terhadap muka robot
                    # Positif = Kanan (Maju), Negatif = Kiri (Mundur)
                    ball_angle = ball_data['direction'][0]
                    
                    # Deadzone bola (biar ga gerak kalau bola diem didepan muka)
                    if abs(ball_angle) > 0.05:
                        # Kecepatan Proporsional (Makin jauh bola, makin cepat)
                        # Kita batasi max speed tracking biar ga liar
                        base_speed = ball_angle * 60.0 
                
                # Clamp base_speed (Max 10)
                if base_speed > 10: base_speed = 10
                if base_speed < -10: base_speed = -10

                # ==========================================================
                # 3. SAFETY GPS (MISTAR GAWANG)
                # ==========================================================
                my_pos = self.get_gps_coordinates()
                
                # Cek Tiang Kanan
                if my_pos[0] > LIMIT_X and base_speed > 0:
                    base_speed = 0
                # Cek Tiang Kiri
                if my_pos[0] < -LIMIT_X and base_speed < 0:
                    base_speed = 0

                # ==========================================================
                # 4. EKSEKUSI MOTOR
                # ==========================================================
                # Prioritas Utama: LURUSKAN BADAN DULU
                # Jika robot miring parah (> 30 derajat/0.5 rad), stop sliding, putar dulu.
                if abs(heading_error) > 0.5:
                    base_speed = 0
                
                left_speed = base_speed - correction
                right_speed = base_speed + correction
                
                # Final Clamp
                left_speed = max(min(left_speed, 10), -10)
                right_speed = max(min(right_speed, 10), -10)

                self.left_motor.setVelocity(left_speed)
                self.right_motor.setVelocity(right_speed)
                self.send_data_to_team(self.player_id)