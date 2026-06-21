# Rastgele aksiyon seçmek için random modülünü içe aktar:
import random

# Grafikleri çizmek için matplotlib kütüphanesini içe aktar:
import matplotlib.pyplot as plt

# Q-table'ı dosyaya kaydetmek ve dosyadan okumak için pickle modülünü içe aktar:
import pickle

class Agent:
    # Ajan sınıfını başlat:
    def __init__(self):
        # Ajanın seçebileceği aksiyon sayısı:
        self.action_count = 6

        # Ajanın gördüpü en iyi skor:
        self.best_score = 0

        # Q-Learning Table:
        self.q_table = {}
        
        # Eğitim istatikstiklerini tutacağımız geçmiş listeleri:
        self.score_history = []

        self.epsilon_history = []

        # Keşif oranı:
        self.epsilon = 0.2

        # Q-table kayıt dosyası:
        self.q_table_file = "q_table.pkl"

        # öğrenme katsayısı ( learning rate )
        self.learning_rate = 0.1

        # Gelecekteki ödüllerin önemi ( discount factor )
        self.discount_factor = 0.95

    # Ham sensör mesafelerini Q-Learning için basit kategorilere çevir:
    def discretize_state( self, state ):
        # Ayrıklaştırılmış state listesi:
        discrate_state = []

        # Sensörler ve hız bilgisini ayır:
        sensor_values = state[:-1]
        speed = state[-1]

        # Her sensör mesafesini işle:
        for distance in sensor_values:

            # Duvar çok yakınsa:
            if distance < 50:
                discrate_state.append(0)

            # Duvar yakınsa:
            elif distance < 100:
                discrate_state.append(1)

            # Duvar uzaktaysa:
            else:
                discrate_state.append(2)

        # Hız bilgisini ayrıklaştır:
        if speed < 1:
            discrate_state.append(0)
        elif speed <3:
            discrate_state.append(1)
        else:
            discrate_state.append(2)

        # Listeyi tuple olarak döndür: çünkü dictionary key olarak kullanılacak
        return tuple( discrate_state ) 

    # Şimdilik rastgele aksiyon seç:
    def choose_action(self, state):
        
        # Ham state'i ayrık state'e çevir:
        discrete_state = self.discretize_state( state )

        # Epsilon ihtimaliyle rastgele aksiyon seç:
        if random.random() < self.epsilon:
            return random.randint( 0, self.action_count - 1 )

        # Bu state için Q değerlerini al:
        q_values = self.get_q_values( discrete_state )

        # En yüksek Q değerine sahip aksiyonu seç:
        best_action = q_values.index( max( q_values ) )

        # En iyi aksiyonu döndür:
        return best_action

    # Episode sonunda skoru değerlendir:
    def learn_from_episode( self, score ):

        # Mevcut skoru geçmiş listesine ekle:
        self.score_history.append( score )

        # O anki epsilon değerini de geçmiş listesine ekle:
        self.epsilon_history.append( self.epsilon )

        # Eğer bu skoru şimdiye kadarki en iyi skorsa kaydet:
        if score > self.best_score:
            self.best_score = score

    # Verilen state içi Q değerlerini al:
    def get_q_values( self, state ):

        # State daha önce görülmediyse tabloya ekle:
        if state not in self.q_table:
            self.q_table[state] = [0] * self.action_count

        # State'e ait aksiyon değerlerini döndür:
        return self.q_table[ state ]
    
    # Q-Learning tablosunu güncelle:
    def update_q_value(
            self,
            state,
            action,
            reward,
            next_state
    ):
        # State'leri ayrık hale getir:
        state = self.discretize_state( state )
        next_state = self.discretize_state( next_state )

        # Mevcut state'in q değerlerini al:
        q_values = self.get_q_values( state )

        # Sonraki state'in q değerlerini al:
        next_q_values = self.get_q_values( next_state )

        # Mevcut Q değerleri:
        current_q = q_values[ action ]

        # Sonraki state'teki en iyi Q değeri:
        max_next_q = max( next_q_values )

        # Q-Learning hedef değeri:
        target_q = reward + (

            self.discount_factor * max_next_q

        )

        # q değerini güncelle:
        q_values[action] = current_q + (

            self.learning_rate * ( target_q - current_q )

        )

    # Q-table'ı dosyaya kaydet:
    def save_q_table( self, filename = None ):

        # Eğer özel bir dosya adı belirtilmediyse, varsayılan kayıt dosyasını kullan:
        if filename is None:
            filename = self.q_table_file

        #Kaydedilecek verileri bir sözlük ( dictionary ) içinde topla:
        data = {
            "q_table": self.q_table,
            "best_score": self.best_score,
            "epsilon": self.epsilon
        }

        # Belirlenen dosyayı yazma ( "wb" - write binary ) modunda aç:
        with open( filename, "wb" ) as file:

            # Verileri dosyaya yazdır:
            pickle.dump( data, file )




    # Q-table'ı dosyadan yükle:
    def load_q_table( self ):
        # Dosya yoksa hiçbir şey yapma:
        try:

            #Dosyayı okuma modunda aç:
            with open( self.q_table_file , "rb" ) as file:

                # Q-table'ı yükle:
                data = pickle.load( file )

                self.q_table = data["q_table"]
                self.best_score = data["best_score"]
                self.epsilon = data.get("epsilon", self.epsilon)
            
        # Dosya bulunamazsa ilk çalıştırma kabul et:
        except FileNotFoundError:
            pass

    # Her bölüm sonunda epsilon değerini, alınan skora göre dinamik olarak azalt:
    def decay_epsilon( self, score ):

        # Minimum epsilon sınırı:
        min_epsilon = 0.01

        # Azaltma oranı:
        decay_rate = 0.999

        # Eğer ajan yüksek bir skor aldıysa ( örneğin 500'den büyük ), ortamı iyi öğrenmeye başlamış demektir.
        if score > 500:
            decay_rate = 0.995

        #Eğer ajan hemen kaza yaptıysa ( örn score 100'den küçükse ) pisti yeterince öğrenmemiş demektr:
        elif score < 100:
            decay_rate = 0.999

        # Epsilon'u azalt:
        self.epsilon *= decay_rate

        # Alt sınır kontrolü:
        if self.epsilon < min_epsilon:

            # Epsilon'u minimum değerde sabitliyoruz ( sınırı koruyoruz ):
            self.epsilon = min_epsilon

    # Eğitim istatistiklerini ekrana grafik olarak çiz:
    def plot_statistics( self ):

        # Eğer veri yoksa ( henüz ilk episode bitmediyse ) çizim yapma:
        if not self.score_history:
            return
        
        # İki alt grafikli ( skor ve epsilon ) yeni bir pencere oluştur:
        fig, ( ax1, ax2 ) = plt.subplots( 2, 1, figsize = ( 10, 8 ) )

        # 1. Grafik: Bölüm başına alınan skorlar ( Mavi çizgi )
        ax1.plot( self.score_history, color = 'blue' )
        ax1.set_title( "Bolum ( Episode ) Basina Skor" )
        ax1.set_ylabel( "Skor" )
        ax1.grid( True ) # Arka plana ızgara ekle

        # 2. Grafik: Epsilon'un zamanla azalmasi ( Kırmızı çizgi )
        ax2.plot( self.epsilon_history, color='red' )
        ax2.set_title( "Epsilon ( Kesif Orani ) Degisimi" )
        ax2.set_xlabel( "Bolum (Episode)" )
        ax2.grid( True )

        # Grafikleri birbiriyle çakışmayacak şekilde düzenle:
        plt.tight_layout()

        # Çizilen grafiği ekranda göster:
        plt.show()