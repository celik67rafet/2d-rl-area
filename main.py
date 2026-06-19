import pygame

# Program kapanırken otomatik işlem yapmmak için atexit modülünü içe aktar:
import atexit

# Car sınıfını car.py dosyasından içe aktarıyoruz:
from car import Car

# Agent sınıfını agent.py dosyasından içe aktar:
from agent import Agent

# Track sınıfını track.py dosyasından içe aktar:
from track import Track

# pygame'i başlat
pygame.init()

# Pencere boyutları:
WIDTH = 1280
HEIGHT = 720

# Oyun penceresini oluştur:
screen = pygame.display.set_mode(( WIDTH, HEIGHT ))

# Pencere başlığını ayarla:
pygame.display.set_caption( "RL 2D Car" )

# FPS kontrolü için saat nesnesi oluştur:
clock = pygame.time.Clock()

# Ajan nesnesini oluştur:
agent = Agent()

# Daha önceki öğrenmeyi yükle:
agent.load_q_table()

# Program kapanırken Q-table'ı otomatik kaydet:
atexit.register( agent.save_q_table )

# Pist nesnesini oluştur:
track = Track()

# Araç nesnesini oluşturuyoruz:
car = Car( 220, 360 )

# Ana döngü kontrol değişkeni:
running = True

# Sıradaki hedef checkpoint index'i:
start_time = pygame.time.get_ticks()

# Araç çarpıştı mı?
crashed = False

# Çarpışma zamanı:
crash_time = 0

# Mevcut denemenin skoru:
score = 0

# Bir episode içinde en fazla kaç frame/step çalışacağını belirler.
# 60 FPS'te 3000 step yaklaşık 50 saniyeye denk gelir.
MAX_EPISODE_STEPS = 3000

# Mevcut episode içinde kaç step geçtiğini tutar.
# Araç restelenince bu değer tekrar 0 yapılacak.
episode_steps = 0

# Geçilen checkpoint sayısı:
checkpoint_count = 0

# tamamlanan tur sayısı:
lap_count = 0

# Son seçilen aksiyon:
last_action = None

# sıradaki hedef checkpoint index'i
next_checkpoint_index = 1

# En son başarıyla geçilen checkpoint index'ini tutar:
last_checkpoint_index = 0

# Hedef checkpoint'e olan önceki mesafe:
previous_checkpoint_distance = None

# Ana uygulama döngüsü:
while running:

    # Kullanıcı olaylarını işle:
    for event in pygame.event.get():

        # Pencere kapatılmak istendiğinde çık:
        if event.type == pygame.QUIT:

            # Öğrenilen Q-Table'ı kaydet:
            agent.save_q_table()

            running = False

    # Tüm sensör mesafelerini hesapla:
    sensor_distances = track.get_sensor_distances( car )

    # RL ajanının göreceği durum bilgisini oluştur:
    state = sensor_distances + [ car.speed ]

    if not crashed:

        # Önceki konumu sakla:
        old_x = car.x
        old_y = car.y

        # Ajan bir aksiyon seçsin:
        action = agent.choose_action( state )

        # Son seçilen aksiyonu kaydet:
        last_action = action

        # Seçilen aksiyonu araca uygula:
        car.apply_action( action )

        # Aracın konumunu güncelle:
        car.update()

        # Bu frame'de ne kadar ilerledi?
        distance_moved = (
            ( car.x - old_x ) ** 2
            + ( car.y - old_y ) ** 2
        ) ** 0.5

        # Varsayılan ödül: pistte kaldığı için küçük pozitif ödül:
        reward = 0.1
        
        # Nerdeyse hiç ilerlemiyorsa ceza ver:
        if distance_moved < 1:
            reward -= 2

        # Hedef checkpoint'i al:
        checkpoint = track.checkpoints[ next_checkpoint_index ]

        # Hedef checkpoint'e mevcut mesafeyi hesapla:
        current_checkpoint_distance = track.get_checkpoint_distance( car, checkpoint )

        # Önceki mesafe varsa yaklaşma/uzaklaşma farkını hesapla:
        if previous_checkpoint_distance is not None:

            # Pozitifse aracı checkpoint'e yaklaştırmıştır:
            progress = previous_checkpoint_distance - current_checkpoint_distance

            # Yaklaştıkça ödül, uzaklaştıkça ceza ver:
            reward += progress * 0.1
        
        # Mesafeyi bir sonraki frame için sakla:
        previous_checkpoint_distance = current_checkpoint_distance

        # Hareket sonrası yeni sensör mesafelerini hesapla:
        next_sensor_distances = track.get_sensor_distances( car )

        # Hareket sonrası yeni state bilgisini oluştur:
        next_state = next_sensor_distances + [ car.speed ]

        
        # Araç pistte kaldığı her frame için skor arttır:
        score += 1

        # Episode içinde bir step daha geçtiğini kaydeder.
        # Bu sayaç timeout kontrolünde kullanılacak:
        episode_steps += 1

        # Episode çok uzun sürüyorsa aracı başarısız kabul et.
        #Böylece ajan sonsuza kadar aynı yerde dolaşmaz.
        if episode_steps >= MAX_EPISODE_STEPS:

            # Timeout durumunu çarpışma gibi ele alacağız:
            crashed = True

            # Çarpışma zamanını kaydet.
            # Böylece mevcut reset sistemi çalışmaya devam edecek:
            if crash_time == 0:
                crash_time = pygame.time.get_ticks()

        # Sıradaki beklenen checkpoint'i hesaplar:
        expected_checkpoint_index = last_checkpoint_index + 1

        # Eğer listenin sonuna gelindiyse tekrar 1.checkpoint 1 olur:
        if expected_checkpoint_index >= len( track.checkpoints ):
            expected_checkpoint_index = 1


        # Araç checkpoint'e ulaştı mı?
        if track.reached_checkpoint( car, checkpoint ) and next_checkpoint_index == expected_checkpoint_index:

            # Geçilen checkpoint sayısını arttır:
            checkpoint_count += 1

            # Bu checkpoint başarıyla geçildiği için son geçilen checkpoint olarak kaydet:
            last_checkpoint_index = next_checkpoint_index

            #Checkpoint ödülü ver:
            reward += 500
            
            # Bir sonraki checkpoint'e geç:
            next_checkpoint_index += 1

            # Liste sonuna gelindiyse başa dön:
            if next_checkpoint_index >= len( track.checkpoints ):
                
                # Bir tur tamamlandı:
                lap_count += 1

                # Büyük ödül:
                reward += 1000

                next_checkpoint_index = 1
    
        # q tablosunu güncelle:
        agent.update_q_value( state, action, reward, next_state )
        
    # Pisti ekrana çiz:
    track.draw( screen, next_checkpoint_index )

    # Aracı ekrana çiz:
    car.draw( screen )

    # Yazı tipi oluştur:
    font = pygame.font.SysFont( None, 36 )

    # Ön sensör mesafesini hesapla:
    sensor_text = font.render(
        f"Sensors: {sensor_distances}",
        True,
        ( 255, 255 , 255 )

    )

    # Ön sensör mesafesi yazısını ekrana çiz:
    screen.blit( sensor_text, ( 40, 25 ) )

    # Skor yazısını oluştur:
    score_text = font.render( f"Score: {score}", True, ( 255, 255, 255 ) )

    
    #Skor yazısını ekrana çiz:
    screen.blit( score_text, ( 40, 50 ) )

    # En iyi score yazısını ekrana çiz:
    best_score_text = font.render(
        f"Best Score: {agent.best_score}",
        True,
        ( 255, 255, 255 )

        
    )

    screen.blit( best_score_text, ( 40, 75 ) )

    # Öğrenilen state sayısını göster:
    states_text = font.render(
        f"Known States: {len( agent.q_table )}",
        True,
        ( 255, 255, 255 )
    )

    #State sayısını ekrana çiz:
    screen.blit( states_text, ( 40, 100 ) )

    # Son aksiyon yazısını oluştur:
    action_text = font.render(
        f"Last Action: { last_action }",
        True,
        ( 255, 255, 255 )
    )

    # Son aksiyonu ekrana çiz:
    screen.blit( action_text, ( 40, 125 ) )

    # Hedef checkpoint bilgisini oluştur:
    checkpoint_text = font.render(
        f"Target Checkpoint: {next_checkpoint_index}",
        True,
        (255,255,255)
    )

    #Hedef checkpoint bilgisini ekrana çiz:
    screen.blit( checkpoint_text, ( 40, 150 ) )

    # Geçilen checkpoint sayısını göster:
    checkpoint_count_text = font.render(
        f"Checkpoints Passed: {checkpoint_count}",
        True,
        ( 255,255,255 )
    )

    # Yazıyı ekrana çiz:
    screen.blit( checkpoint_count_text, ( 40, 175 ) )

    # tamamlanan tur sayısı yazdırma:
    lap_text = font.render(
        f"Laps: {lap_count}",
        True,
        (255,255,255)
    )

    screen.blit( lap_text, ( 40, 200 ) )

    # Epsilon değerini göster:
    epsilon_text = font.render(
        f"Epsilon: {agent.epsilon:.3f}",
        True,
        ( 255,255,255 )
    )
    
    screen.blit( epsilon_text, ( 40,225 ) )

    #Geçen süreyi saniye olarak hesapla:
    elapsed_seconds = (
        pygame.time.get_ticks() - start_time
    ) // 1000

    # Dakika ve saniyeye çevir:
    minutes = elapsed_seconds // 60
    seconds = elapsed_seconds % 60

    # Süre yazısını
    time_text = font.render(
        f"Time: {minutes:02}:{seconds:02}",
        True,
        (255,255,255)
    )

    screen.blit( time_text, ( 40, 250 ) )

    # Episode içinde kaç step geçtiğini göster.
    # Timeout sisteminin doğru çalışıp çalışmadığını gözlemlemek için faydalıdır:
    steps_text = font.render(
        f"Episode Steps: {episode_steps}",
        True,
        (255,255,255)
    )
    
    # Yazıyı ekrana çiz:
    screen.blit( steps_text, ( 40, 275 ) )

    # Araç pist üzerinde değilse uyarı yazısı göster:
    if not crashed and not track.is_car_on_track( car ):

        # Aracı durdur:
        car.speed = 0

        # Araç artık çarpışmış durumda:
        crashed = True

        # Çarpışma cezası:
        reward = -100
        

        # Çarpışma sonrası state bilgisini al:
        next_state = track.get_sensor_distances( car ) + [ car.speed ]

        # Çarpışmaya sebep olan aksiyonu cezalandır:
        agent.update_q_value( state, action, reward, next_state )

        if crash_time == 0:
            crash_time = pygame.time.get_ticks()

        # Yazı tipi oluştur:
        font = pygame.font.SysFont( None, 48 )

        # Uyarı yazısını oluştur:
        text = font.render( "off track", True, ( 255, 60, 60 ) )

        # Uyarı yazısını ekrana çiz:
        screen.blit( text, ( 40, 90 ) )

    # Ekranı güncelle
    pygame.display.flip()

    # Çarpışmadan önce 1 saniye sonra reset at:
    if crashed:

        # Geçen süreyi hesapla:
        elapsed = pygame.time.get_ticks() - crash_time

        # 1000 ms geçtiyse:
        if elapsed >= 1000:

            # Aracı başlangıç noktasına döndür:
            car.reset( 220, 360, 270 )

            # Çarpışma durumunu temizle:
            crashed = False

            # Çarpışma zamanını sıfırla:
            crash_time = 0

            # Hedef checkpoint'i başlangıca döndür:
            next_checkpoint_index = 1

            # Yeni episode başladığı için son geçilen checkpoint'i başlangıç durumuna al:
            last_checkpoint_index = 0

            # Hedef checkpoint'e olan önceki mesafe:
            previous_checkpoint_distance = None

            # Geçilen checkpoint sayısını sıfırla:
            checkpoint_count = 0

            # lap count sıfırla:
            lap_count = 0

            # Son seçilen aksiyon
            last_action = None

            # Episode skorunu ajana bildir:
            agent.learn_from_episode( score )

            # keşif oranını azalt:
            agent.decay_epsilon()
            
            # Skoru sıfırla:
            score = 0

            # Yeni episode başlayacağı için step sayacını sıfırla:
            # Böylece timeout süresi her denemede baştan başlar:
            episode_steps = 0

    # Uygulamayı 60 FPS ile sınırlar:
    clock.tick(60)

# pygame'i düzgün şekilde kapat:
pygame.quit()