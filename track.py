# pygame kütüphanesini içe aktar:
import pygame
import math
import random

class Track:
    # Pist sınıfını başlat:
    def __init__(self):

        # Yeni ve daha karmaşık pisti oluşturan yol parçaları ( dikdörtlenler ):
        # Sol alt köşeden başlayıp dolambaçlı bir tur atıyoruz.
        self.road_rects = [
            pygame.Rect(100, 500, 900, 150), # 1. Alt düzlük
            pygame.Rect(850, 100, 150, 550), # 2. Sağ düzlük ( Yukarı çıkış )
            pygame.Rect(400, 100, 600, 150), # 3. Üst düzlük ( Sola gidiş )
            pygame.Rect(400, 100, 150, 300), # 4. Orta dikey ( aşağı iniş )
            pygame.Rect(100, 250, 450, 150), # 5. Orta Dikey ( Sola gidiş )
            pygame.Rect(100, 250, 150, 400), # 6. Sol dikey ( Başlangıç dönüş )

        ]

        # Yeni piste uygun checkpoint'ler ( Sırasıyla geçilmesi gereken çizgiler )
        self.checkpoints = [
            (( 300, 500 ), ( 300, 650 )), # 1. Alt düzlük ortası
            (( 650, 500 ), ( 650, 650 )), # 2. Alt düzlük sonu 
            (( 850, 400 ), ( 1000, 400 )), # 3. Sağ düzlük tırmanış
            (( 850, 250 ), ( 1000, 250 )), # 4. Sağ düzlük üst
            (( 650, 100 ), ( 650, 250 )), # 5. Üst düzlük dönüşü
            (( 400, 246 ), ( 550, 250 )), # 6. Orta dikey iniş
            (( 300, 250 ), ( 300, 400 )), # 7. Orta yatay
            (( 100, 450 ), ( 250, 450 )), # 8. Sol dikey iniş
        ]

        # Checkpoint algılama yarıçapı
        self.checkpoint_radius = 30

        # Yeni başlangıç noktaları ( Alt düzlüğün başında, sağa ( açı: 0 ) bakacak şekilde )
        self.start_positions = [
            ( 180, 550, 0 ),
            ( 180, 600, 0 ),
            ( 150, 575, 0 ),
            ( 200, 575, 0 )
        ]

    # Listeden rastgele bir başlangıç pozisyonu seç:
    def get_random_start_position( self ):
        return random.choice( self.start_positions )
    
    # Pisti ekrana çiz:
    def draw( self, screen, target_checkpoint_index ):

        # Arka plan çim ( Yeşil )
        screen.fill(( 35, 120, 55 ))

        # Tüm yol parçalarını gri çiz:
        for rect in self.road_rects:
            pygame.draw.rect( screen, ( 90, 90, 90 ), rect )

        # Checkpointleri çiz:
        for index, self.checkpoint in enumerate( self.checkpoints ):

            color = ( 255, 255, 0 ) # Normal Checkpoint sarı
            if index == target_checkpoint_index:
                color = ( 0, 255 ,0 ) # Hedef checkpoint yeşil

            pygame.draw.line( screen, color, self.checkpoint[0], self.checkpoint[1], 4 )

    # Koordinat pist üzerinde mi kontrol et:
    def is_on_track( self, x, y ):
        # Nokta yol parçalarında ( dikdörtgenlerden ) HERHANGİ BİRİNİN içindeyse pisttedir:
        for rect in self.road_rects:
            if rect.collidepoint( x, y ):
                return True
        return False
    
    # Aracın tamamı pist üzerinde mi kontrol et:
    def is_car_on_track( self, car ):
        corners = car.get_corners()
        for x, y in corners:
            if not self.is_on_track( x, y ):
                return False
        return True
    
    # Aracın tüm sensörlerinin mesafesini ölç:
    def get_sensor_distances( self, car ):
        distances = []
        for sensor_angle in car.sensor_angles:
            angle = car.angle + sensor_angle
            radians = math.radians( angle )
            measured_distance = car.sensor_length

            for distance in range( car.sensor_length ):
                test_x = car.x + math.cos( radians ) * distance
                test_y = car.y + math.sin( radians ) * distance

                if not self.is_on_track( test_x, test_y ):
                    measured_distance = distance
                    break
            distances.append( measured_distance )
        return distances
    
    # Araç checkpoint'e ulaştı mı:
    def reached_checkpoint( self, car, checkpoint ):
        x1, y1 = checkpoint[0]
        x2, y2 = checkpoint[1]
        px, py = car.x, car.y
        dx, dy = x2 - x1, y2 - y1
        line_length_squared = dx * dx + dy * dy

        if line_length_squared == 0:
            return False
        
        t = (((px - x1) * dx + (py - y1) * dy) / line_length_squared)
        t = max(0, min(1, t))

        nearest_x = x1 + t * dx
        nearest_y = y1 + t * dy

        distance = math.sqrt((px - nearest_x) ** 2 + (py - nearest_y) ** 2)
        return distance <= 25
    
    # Hedef checkpoint'e olan mesafeyi hesapla:
    def get_checkpoint_distance( self, car, checkpoint ):
        x1, y1 = checkpoint[0]
        x2, y2 = checkpoint[1]
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2
        dx = car.x - center_x
        dy = car.y - center_y

        return ( dx * dx + dy * dy ) ** 0.5