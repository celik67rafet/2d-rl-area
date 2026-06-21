import torch
import torch.nn as nn
import torch.nn.functional as F
import os
import torch.optim as optim

# Yapay Sinir Ağı Sınıfımız ( PyTorch'un nn.Module sınıfından miras alır )
class Linear_QNet( nn.Module ):

    def __init__( self, input_size, hidden_size, output_size ):
        
        super().__init__()

        # 1. Katman ( Giriş katmanından -> Gizli katmana )
        # input_size: Sensör sayısı + Hız bilgisi
        self.linear1 = nn.Linear( input_size, hidden_size )

        self.linear2 = nn.Linear( hidden_size, output_size )

    def forward( self, x ):
        # İleri besleme ( Forward Pass ): Veri ağın içinden geçer.

        # Gelen veriyi (x) ilk katmandan geçir ve ReLU aktivasyon fonksiyonunu uygula.
        # ReLU ( ( Rectified Linear Unit ), negaitif değerleri 0 ypaar, pozitifleri aynen bırakır.
        # Bu, ağın doğrusal olmayan ( karmaşık ) problemleri öğrenmesini sağlar.
        x = F.relu( self.linear1(x) )

        # Sonucu ikinci katmandan geçirip her aksiyon için bir Q-değeri ( puan ) üret:
        x = self.linear2(x)

        return x
    
    def save( self, file_name='model.pth' ):
        # Eğitilen modeli kaydetmek için 'model' adında bir klasör oluştur ( yoksa )
        model_folder_path = './model'
        if not os.path.exists( model_folder_path ):
            os.makedirs( model_folder_path )

        # Ağırlıkları ( öğrenilen verileri ) belirtilen isimle ( .pth formatında ) kaydet
        file_name = os.path.join( model_folder_path, file_name )
        torch.save( self.state_dict(), file_name )


# Modeli eğitecek ( Ağırlıkları güncelleyecek ) Antrenör Sınıfı:
class QTrainer:

    def __init__( self, model, lr, gamma ):

        self.lr = lr #Öğrenme Hızı ( Learning Rate )
        self.gamma = gamma # Gelecek ödüllerin ne kadar önemseneceği ( Discount Factor )
        self.model = model

        # Adam optimizasyonu ( Yapay zeka dünyasının en popüler ağırlık güncelleyicisi )
        self.optimizer = optim.Adam( model.parameters(), lr = self.lr )

        # Hata hesaplama fonksiyonu ( Mean Squared Error - Ortalama Kare Hatası )
        self.criterion = nn.MSELoss()

    def train_step( self, state, action, reward, next_state, done ):
        # PyTorch kullanabilmek için normal Python listelerini Torchg Tensor'lerine ( matrislere ) çeviriyoruz:
        state = torch.tensor( state, dtype = torch.float )
        next_state = torch.tensor( next_state, dtype = torch.float )
        action = torch.tensor( action, dtype = torch.long )
        reward = torch.tensor( reward, dtype = torch.float )

        # Eğer tek bir veri geldiyse, onu batch ( grup ) formatına uydurmak için 1 boyut ekle
        if len( state.shape ) == 1:
            state = torch.unsqueeze( state, 0 )
            next_state = torch.unsqueeze( next_state, 0 )
            action = torch.unsqueeze( action, 0 )
            reward = torch.unsqueeze( reward, 0 )
            done = (done,)

        # 1. Adım: Mevcut durum için ağın tahmin ettiği Q değerlerini al:
        pred = self.model( state )

        # Hedef Q değerlerini, tahminlerin bir kopyası olarak başlat:
        target = pred.clone()

        # 2. Adım: Q-Learning( formülünü uygula ( Q_new = reward + gamma * max( next_Q ) )
        for idx in range( len( done ) ):
            
            Q_new = reward[idx]

            # Eğer çarpışma yoksa ( oyun bitmediyse ), gelecekteki tahmini de ekle:
            if not done[idx]:
                Q_new = reward[idx] + self.gamma * torch.max( self.model( next_state[idx] ) )
            
            # Sadece  seçilen aksiyonun hedefini güncelle ( diğer aksiyonların değeri aynı kalsın ki hata üretmesin )
            target[ idx ][ action[ idx ].item() ] = Q_new

        # 3. Adım: Ağırlıkları güncelle ( Geri yayılım - Backpropagation )
        self.optimizer.zero_grad() # Önceki hesaplamaları sıfırla
        loss = self.criterion( target, pred ) # Hedef değer ile tahmin edilen değer arasındaki hatayı hesapla
        loss.backward() # Hatayı geriye doğru dağıt
        self.optimizer.step() # Nöron ağırlıklarını güncelle

