import torch
import random
import os
from collections import deque
import matplotlib.pyplot as plt

# model.py dosytasından az önce oluşturduğumuz Beyin ve Antrenörü içe aktarıyoruz:
from model import Linear_QNet, QTrainer

# DQM Hiperparametreleri ( Ayarları )
MAX_MEMORY = 100_100 # Hafızada tutulacak maksimum adım sayısı
BATCH_SIZE = 1000 # Bölüm sonunda hafızadan rastgele çekilip öğrenilecek anı sayısı
LR = 0.001 # Öğrenme hızı ( Learning Rate )

class Agent:
    def __init__( self ):
        self.epsilon = 1.0 # Başlangıçta %100 rastgele ( Keşif )
        self.epsilon_decay = 0.99 # Rastgeleliğin azalma hızı ( Artık daha hızlı azaltıyoruz )
        self.epsilon_min = 0.01 # Rastgelelik en az %1'e düşebilir
        self.gamma = 0.95 # Gelecekteli ödüllerin önemi ( Discount Factor )

        # Ajanın anılarını tutacağı hafıza ( Dolduğunda en eski anıları otomatik siler )
        self.memory = deque( maxlen = MAX_MEMORY )

        # YAPAY SİNİR AĞI ( BEYİN ) OLUŞTURULOR:
        # GİRDİ: 8 ( 7 Sensör + 1 Hız )
        # Gizli Katman: 256 Nöron
        # ÇIKTI: 6 ( Yapılabilecek 6 farklı aksiyon )
        self.model = Linear_QNet( 8, 256, 6 )

        # ANTRENÖR OLUŞTURULUYOR:
        self.trainer = QTrainer( self.model, lr = LR, gamma = self.gamma )

        # İstatistikler için değişkenler:
        self.best_score = 0
        self.score_history = []
        self.epsilon_history = []

    # O anki adımı anında ( tekil olarak ) öğren ve hafızaya kaydet:
    def update_q_value( self, state, action, reward, next_state, done=False ):

        # 1. Kısa vadeli hafıza ( O anki tek adımı öğren )
        self.trainer.train_step( state, action, reward, next_state, done )

        # 2. Bu deneyimi gelecekte tekrar hatırlamak üzere hafızaya kaydet:
        self.memory.append(( state, action, reward, next_state, done ))

    # Bölüm ( Episode ) bittiğinde hafızadaki eski anılardan toplu ders çıkar:
    def train_kong_memory( self ):
        # Hafızada yeterli anı varsa BATCH_SIZE kadar rastgele örnek al, yoksa hepsini al
        if len( self.memory ) > BATCH_SIZE:
            mini_sample = random.sample( self.memory, BATCH_SIZE )
        else:
            mini_sample = self.memory

        # Alınan rastgele anıları gruplarına göre ayır ( Örn: Tüm durumlar bir araya, Ödüller bir araya )
        states, actions, rewards, next_states, dones = zip( *mini_sample )

        # Antrenöre bu toplu anıları ver ve beyni ( ağırlıkları ) güncelle
        self.trainer.train_step( states, actions, rewards, next_states, dones )

    # Duruma bakarak bir aksiyon seç ( Epsilon-Greedy ):
    def choose_action( self, state ):
        # Rastgele ( Keşif ) mi, yoksa Model ( Sömürü ) mi kullanılacak?
        if random.random() < self.epsilon:
            action = random.randint( 0, 5 ) # Rastgele bir aksiyon seç
        else:
            # Durum verisini ( listeyi ) PyTorch'un anlayacağı Tensor formatına çevir:
            state_tensor = torch.tensor( state, dtype = torch.float )

            # Veriyi sinir ağına ( beyne ) yolla ve tahminleri ( Q-değerlerini ) al:
            prediction = self.model( state_tensor )

            # En büyük Q-değerine sahip ( en avantajlı ) aksiyonun index'ini seç:
            action = torch.argmax( prediction ).item()

        return action
    
    # Her bölüm sonunda rastgelelik oranını biraz azalt:
    def decay_epsilon( self, score ):
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
        
    # Bölüm bittiğinde uzun hafızayı eğit ve istatistikleri kaydet:
    def learn_from_episode( self, score ):
        # Bölüm bittiği için geçmiş anılardan toplu bir eğitim ( Experience Replay ) yap
        self.train_kong_memory()

        # İstatistikleri kaydet:
        self.score_history.append( score )
        self.epsilon_history.append( self.epsilon )

        # En iyi skoru güncelle:
        if score > self.best_score:
            self.best_score = score

    # Öğrenilmiş ağırlıkları ( Beyni ) kaydet:
    def save_q_table( self, filename="model.pth" ):
        self.model.save( filename )

    # Önceden öğrenilmiş beyni yükle:
    def load_q_table( self, filename = "model.pth" ):
        path = os.path.join('./model', filename)
        if os.path.exists( path ):
            self.model.load_state_dict( torch.load( path ) )
            self.model.eval() # Modeli test/kullanım moduna al
            print("Önceki öğrenmeler ( Yapay Sinir Ağı ) başarıyla yüklendi!")

    # Eğitim grafiğini çiz ( Eski sistemle birebir aynı )
    def plot_statistics( self ):

        if not self.score_history:
            return
        
        fig, ( ax1, ax2 ) = plt.subplots( 2, 1, figsize = ( 10, 8 ) )

        ax1.plot( self.score_history, color = 'blue' )
        ax1.set_title( "Bolum ( Episode ) Basina Skor" )
        ax1.set_ylabel( "Skor" )
        ax1.grid( True )

        ax2.plot( self.epsilon_history, color = 'red' )
        ax2.set_title( "Epsilon ( Kesif Orani ) Degisimi" )
        ax2.set_xlabel( "Epsilon" )
        ax2.set_ylabel( "Epsilon" )
        ax2.grid( True )

        plt.tight_layout()
        plt.show()
