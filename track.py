# pygame kütüphanesini içe aktar:
import pygame

# math import
import math

class Track:
    # Pist sınıfını başlat:
    def __init__( self ):
        # Pist dış sınıır:
        self.outer_rect = pygame.Rect( 140,80,1000,560 )
        
        # Checkpoint çizgileri
        self.checkpoints = [
            ((140, 300), (340, 300)),    # Sol orta / başlangıç sonrası
            ((450, 80), (450, 220)), 
            ((800, 80), (800, 220)),
            ((940, 300), (1135, 300)),
            ((800, 420), (800, 635)),
            ((450, 420), (450, 635)), 
        ]

        # Checkpoint algılama yarıçağı
        self.checkpoint_radius = 30

        # Pist iç boşluğu
        self.inner_rect = pygame.Rect( 340, 220, 600, 200 )

    # Pisti ekrana çiz:
    def draw( self, screen, target_ceheckpoint_index ):
        # Tüm arka planı çim alan gibi yeşil çiz:
        screen.fill(( 35,120,55 ))

        # Pist dış alanını gri çiz:
        pygame.draw.rect( screen, ( 90, 90, 90 ), self.outer_rect )

        # Pist iç boşluğu tekrar yeşil çiz
        pygame.draw.rect( screen, ( 35, 120, 55 ), self.inner_rect )

        # Pist dış kenar çizgisi:
        pygame.draw.rect( screen, ( 230, 230, 230 ), self.outer_rect, 4 )

        # Pist iç kenar çizgisi:
        pygame.draw.rect( screen, ( 230, 230, 230 ), self.inner_rect, 4 )

        # Tüm checkpointleri çiz:
        for index, checkpoint in enumerate( self.checkpoints ):

            # Varsayılan checkpoint rengi:
            color = ( 255, 255 , 0 )

            # Hedef checkpoint'i yeşil göster:
            if index == target_ceheckpoint_index:
                color = ( 0, 255, 0 )

            # Çizginin başlangıç noktası:
            start_point = checkpoint[0]

            # Çizginin bitiş noktası:
            end_point = checkpoint[1]

            #Checkpoint noktasını çiz:
            pygame.draw.line(
                screen,
                color,
                start_point,
                end_point,
                4
            )

    def is_on_track( self, x, y ):
        # Nokta dış pist dikdörtgeninin içinde mi?
        inside_outer = self.outer_rect.collidepoint( x, y )

        # Nokta iç boşluk dikdörtgeninin içinde mi?
        inside_inner = self.inner_rect.collidepoint( x, y )

        # Pistte olmak için dış sınır içinde ve iç boşluk dışında olmalı:
        return inside_outer and not inside_inner
    

    # Aracın tamamı pist üzerinde mi kontrol et:
    def is_car_on_track( self, car ):
         # Aracın dört köşesini al:
        corners = car.get_corners()

        # Her köşeyi tek tek kontrol et:
        for x,y in corners:

            # Herhangi bir köşe pist dışında ise araç pist dışındadır.
            if not self.is_on_track( x,y ):
                return False
            
        # Tüm köşeler pist üzerindeyse araç pisttedir:
        return True
    
    # Aracın tüm sensörlerinin piste çıkmadan önceki mesafesini ölç:
    def get_sensor_distances( self, car ):
        # Ölçülen sensör mesafeleri:
        distances = []

        #Her sensör açısını sırayla işle:
        for sensor_angle in car.sensor_angles:

            # Sensörün dünya açısını hesapla:
            angle = car.angle + sensor_angle

            # Sensörün bakış açısını radyana çevir
            radians = math.radians( angle )

            # Varsayılan mesafe maksimum sensör uzunluğu:
            measured_distance = car.sensor_length

            # Sensörü piksel piksel ilerlet:
            for distance in range( car.sensor_length ):

                # Sensör üzerindeki test noktasının x konumu:
                test_x = car.x + math.cos( radians ) * distance

                # Sensör üzerindeki test noktasının y konumu:
                test_y = car.y + math.sin( radians ) * distance

                # Test notkası pist dışına çıktıysa mesafeyi kaydet:
                if not self.is_on_track( test_x, test_y ):
                    measured_distance = distance
                    break

            # Ölçülen mesafeyi listeye ekle:
            distances.append( measured_distance )

        # Sol, ön, sağ sensör mesafelerini döndür:
        return distances
    
    #Araç belirtilen checkpoint'e ulaştı mı?
    def reached_checkpoint( self, car, checkpoint ):
        # Çizginin başlangıç noktası:
        x1,y1 = checkpoint[0]

        # Çizginin bitiş noktası:
        x2,y2 = checkpoint[1]

        # Araç merkezinin koordinatları:
        px = car.x
        py = car.y

        # Çizginin vektörü:
        dx = x2 - x1
        dy = y2 - y1

        # Çizgi uzunluğunun karesi:
        line_length_squared = dx * dx + dy * dy

        # Güvenlik kontrolü:
        if line_length_squared == 0:
            return False
        
        # Araç merkezinin çizgi üzerindeki en yakın noktasını bul:
        t = (
            (( px - x1 ) * dx + ( py - y1 ) * dy)
            / line_length_squared
        )

        # Çizgi segmenti içinde sınırla:
        t = max( 0, min( 1, t ) )

        # En yakın noktanın koordinatları:
        nearest_x = x1 + t * dx
        nearest_y = y1 + t * dy

        # Araç ile çizgi arasındaki mesafe:
        distance = math.sqrt(
            ( px - nearest_x ) ** 2
            + ( py - nearest_y ) ** 2
        )

        # Çizgiye yeterince yakınsa checkpoint geçilmiş say:
        return distance <= 25
    
    # Araç ile checkpoint çizgisinin merkezi arasındaki mesafeyi hesapla:
    def get_checkpoint_distance( self, car, checkpoint ):
        # Çizginin başlangıç noktası:
        x1, y1 = checkpoint[0]

        # Çizginin bitiş noktası:
        x2, y2 = checkpoint[1]

        # Checkpoint çizgisinin merkez x konumu:
        center_x = ( x1 + x2 ) / 2

        #Checkpoint çizgisinin merkez y konumu:
        center_y = ( y1 + y2 ) / 2

        # Araç ile checkpoint merkezi arasındaki fark:
        dx = car.x - center_x
        dy = car.y - center_y

        # Mesafeyi döndür:
        return ( dx * dx + dy * dy ) ** 0.5