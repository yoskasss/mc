from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import random

app = Ursina()

# Oyuncu ve ortam
player = FirstPersonController()
Sky()

# Blok türleri ve dokuları
block_types = {
    '1': 'textures/grass.png',
    '2': 'textures/stone.png',
    '3': 'textures/diamond.png',
}

block_list = list(block_types.keys())  # Blokları liste olarak sakla
current_block_index = 0  # Varsayılan blok indexi
current_block = block_list[current_block_index]

boxes = []

# **Zemin oluşturma** (40x40 daha büyük alan)
terrain_size = 40
for i in range(terrain_size):
    for j in range(terrain_size):
        box = Button(color=color.white, model='cube', position=(j, 0, i),
                     texture=block_types['1'], parent=scene, origin_y=0.5)
        boxes.append(box)

# **Gerçekçi tepecikler oluşturma** (Çim dokusu)
for _ in range(5):  # 15 büyük tepe oluştur
    x, z = random.randint(5, terrain_size-5), random.randint(5, terrain_size-5)
    peak_height = random.randint(3, 7)  # Tepe yüksekliği 3 ile 7 arasında olacak
    
    for h in range(peak_height):  
        spread = peak_height - h  # Yükseklik arttıkça alan küçülüyor (piramit etkisi)
        
        for dx in range(-spread, spread+1):
            for dz in range(-spread, spread+1):
                if random.random() > 0.3:  # Hafif rastgelelik ekle
                    box = Button(color=color.white, model='cube',
                                 position=(x+dx, h, z+dz),
                                 texture=block_types['1'], parent=scene, origin_y=0.5)
                    boxes.append(box)

# **Elde tutulan blok simgesi**
block_icon = Entity(
    model='cube',
    texture=block_types[current_block],
    scale=0.2,
    position=(0.75, -0.4),  # Sağ alt köşeye yerleştirme
    rotation=(30, -45, 0),
    parent=camera.ui  # UI öğesi olarak ekleniyor
)

def update_block_icon():
    """Blok değiştiğinde simgenin görünümünü güncelle ve animasyon ekle"""
    block_icon.texture = block_types[current_block]
    
    # Küçülüp büyüme animasyonu (hafif geçiş efekti)
    block_icon.animate_scale(0.15, duration=0.1, curve=curve.linear)
    invoke(block_icon.animate_scale, 0.2, duration=0.1, delay=0.1, curve=curve.linear)

def input(key):
    global current_block, current_block_index
    
    # Klavyeden blok değiştirme
    if key in block_types:
        current_block = key
        update_block_icon()
    
    # Mouse tekerleği ile blok değiştirme
    if key == 'scroll up':
        current_block_index = (current_block_index + 1) % len(block_list)
    elif key == 'scroll down':
        current_block_index = (current_block_index - 1) % len(block_list)
    
    current_block = block_list[current_block_index]
    update_block_icon()
    
    # Blok yerleştirme ve kırma
    for box in boxes:
        if box.hovered:
            if key == 'right mouse down':
                new = Button(color=color.white, model='cube', position=box.position + mouse.normal,
                             texture=block_types[current_block], parent=scene, origin_y=0.5)
                boxes.append(new)
            if key == 'left mouse down':
                boxes.remove(box)
                destroy(box)

def update():
    # Eğer oyuncu çok aşağı düşerse başlangıç noktasına dön
    if player.y < -5:
        player.position = (terrain_size//2, 5, terrain_size//2)

app.run()
