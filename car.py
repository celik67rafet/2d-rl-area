import pygame

# pygame kütüphanesini içe aktar:
import math

class Car:
    # Araç sınıfını başlat:
    def __init__( self, x, y ):
        # Aracın x konumu:
        self.x = x
        
        # Ön sensörün maksimum menzili:
        self.sensor_length = 150

        self.sensor_angles = [ -90, -60, -30, 0, 30, 60, 90 ]

        # Aracın y konumu:
        self.y = y

        # Aracın yön açısı:
        self.angle = 270

        # Aracın mevcut hızı:
        self.speed = 0

        # Aracın hızlanma miktarı:
        self.acceleration = 0.2

        # Aracın maksimum hızı:
        self.max_speed = 5

        # Aracın yavaşlama katsayısı:
        self.friction = 0.95

        # Aracın genişliği:
        self.width = 40

        # Aracın yüksekliği:
        self.height = 20

    # Aracı ekrana çiz:
    def draw( self, screen ):
        # Aracın yüzeyini oluştur:
        car_surface = pygame.Surface(( self.width, self.height ), pygame.SRCALPHA )

        # Aracın gövdesini çiz:
        pygame.draw.rect( car_surface, ( 220, 60, 60 ), (0, 0, self.width, self.height) )

        # Aracı yön açısına göre döndür:
        rotated_surface = pygame.transform.rotate( car_surface, -self.angle )

        # Döndürülmüş aracın dikdörtgenini merkezden hizala:
        rotate_rect = rotated_surface.get_rect( center = ( self.x, self.y ) )

        # Aracı ekrana çiz:
        screen.blit( rotated_surface, rotate_rect )

        # Aracın baktığı yönün açısını radyana çevir:
        radians = math.radians( self.angle )

        # Ön yön çizgisinin uzunluğu:
        line_length = 50

        # Çizginin bitiş noktası:
        end_x = self.x + math.cos( radians ) * line_length
        end_y = self.y + math.sin( radians ) * line_length

        # Aracın baktığı yönü göster:
        pygame.draw.line(
            screen,
            ( 255, 255, 0 ),
            ( self.x, self.y ),
            ( end_x, end_y ),
            3
        )

        # Aracın köşe noktalarını al:
        corners = self.get_corners()

        # her köşeyi küçük mavi nokta olarak çiz:
        for corner in corners:
            pygame.draw.circle(

                screen,
                ( 80, 160, 255 ),
                corner,
                4

            )


        # Her sensörü sırayla çiz:
        for sensor_angle in  self.sensor_angles:
            #Sensörün dünya açısını hesapla:
            angle = self.angle + sensor_angle

            # Sensör açısını radyana çevir:
            sensor_radians = math.radians( angle )

            # Sensör bitiş x konumu
            sensor_end_x = self.x + math.cos( sensor_radians ) * self.sensor_length

            # Sensör bitiş y konumu
            sensor_end_y = self.y + math.sin( sensor_radians ) * self.sensor_length

            # Ön sensörü çiz:
            pygame.draw.line(
                screen,
                ( 0, 255, 255 ),
                ( self.x, self.y ),
                ( sensor_end_x, sensor_end_y ),
                2
            )


    # Dışarıdan gelen aksiyonu uygula:
    def apply_action( self, action ):
        # Aksiyon 1 ise gaz ver:
        if action == 1:
            self.speed += self.acceleration

        # Aksiyon 2 ise sola dön:
        elif action == 2:
            self.angle -= 5
        
        # Aksiyon 3 ise sağa dön:
        elif action == 3:
            self.angle += 5

        elif action == 4:
            self.speed += self.acceleration
            self.angle -= 5
        
        elif action == 5:
            self.speed += self.acceleration
            self.angle += 5

        # Hızı maksimum sınırlar içinde tut:
        self.speed = max( -self.max_speed, min( self.speed, self.max_speed ) )

    # Aracın konumunu güncelle:
    def update( self ):
        # Sürtünme uygula:
        self.speed *= self.friction

        # Açıyı radyana çevir:
        radians = math.radians( self.angle )

        # Açıya göre x konumun güncelle
        self.x += math.cos( radians ) * self.speed

        # Açıya göre y konumun güncelle:
        self.y += math.sin( radians ) * self.speed
        
    
    # Aracın dört köşesini hesapla:
    def get_corners( self ):
        # Açıyı radyana çevir:
        radians = math.radians( self.angle )

        # Yarım genişlik:
        half_width = self.width / 2

        # Yarım yükseklik:
        half_height = self.height / 2

        # Yerel köşe koordinatları:
        local_corners = [
            ( -half_width, -half_height ),
            ( half_width, -half_height ),
            ( half_width, half_height ),
            ( -half_width, half_height )
        ]

        # Dünyas kordinatlarındaki köşeler:
        world_corners = []

        # Her köşeyi döndür ve taşı:
        for x,y in local_corners:

            rotated_x = (

                x * math.cos( radians )
                - y * math.sin( radians )

            )

            rotated_y = (

                x * math.sin( radians )
                + y * math.cos( radians )

            )

            world_corners.append(

                (

                    self.x + rotated_x,
                    self.y + rotated_y

                )

            )

        return world_corners
    
    # Aracı başlangıç durumuna döndür:
    def reset( self, x, y, angle ):
        # Başlangıç x konumu:
        self.x = x

        # Başlangıç y konumu:
        self.y = y

        # Başlangıç yön açısı
        self.angle = angle

        # Hızı sıfırla:
        self.speed = 0


    def get_sensor_end_point( self ):
        # Açıyı radyana çevir:
        radians = math.radians( self.angle )

        # Sensör bitiş noktası:
        end_x = self.x + math.cos( radians ) * self.sensor_length
        end_y = self.y + math.sin( radians )* self.sensor_length

        # Noktayı döndür:
        return end_x, end_y