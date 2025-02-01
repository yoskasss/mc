from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import random
import json

t = int(input("Tepecik sayısı: "))
y = int(input("Yükseklik: "))
x = int(input("Genişlik: "))

app = Ursina()

# JSON dosyasını okuyarak blok türlerini yükleyin
with open('block_types.json', 'r') as f:
    block_types = json.load(f)

# ---------- ANA MENÜ (MAIN MENU) ----------
# Ana menü ekranını kaplayan panel (UI'da en üstte)
main_menu = Entity(parent=camera.ui, scale=(1,1))

# Arka plan resmi (assets klasörünüzde 'main_menu_bg.png' adında bir resim olduğundan emin olun)
menu_bg = Sprite(
    parent=main_menu,
    scale=(2,2),        # Ekranı tamamen kaplayacak şekilde ölçeklendirin
    color=color.clear, # Arka plan rengi
    z=1                 # UI sıralamasında öne çıkması için
)

# Başlık metni
menu_title = Text(
    text="""Minecraft Clone\nwith Ursina""",
    parent=main_menu,
    origin=(0,0),
    scale=2,
    position=(0, 0.3)
)

# Start butonu: Tıklandığında oyunu başlatacak
start_button = Button(
    text="Start",
    parent=main_menu,
    mouse_enter=Audio('audio/mouse.ogg'),  # Üzerine gelindiğinde ses efekti
    scale=(0.2, 0.1),
    position=(0, 0)
)

# Server butonu: Tıklandığında henüz hiçbir işlem yapmıyor
server_button = Button(
    text="Server",
    parent=main_menu,
    scale=(0.2, 0.1),
    position=(0.3, -0.3),
    on_click=lambda: None  # Henüz hiçbir şey yapmıyor.
)

# ---------- PAUSE MENÜ (PAUSE MENU) ----------
pause_menu = Entity(parent=camera.ui, scale=(1,1), enabled=False)
def resume_game():
    pause_menu.disable()
    window.exit_button.visible = False
    mouse.locked = True

pause_bg = Sprite(
    parent=pause_menu,
    scale=(2,2),
    color=color.clear,
    z=1
)

pause_title = Text(
    text="Paused",
    parent=pause_menu,
    origin=(0,0),
    scale=2,
    position=(0, 0.3)
)

resume_button = Button(
    text="Resume",
    parent=pause_menu,
    scale=(0.2, 0.1),
    position=(0, 0),
    on_click=lambda: resume_game()
)

# ---------- OYUN İÇERİĞİ (GAME CONTENT) ----------
# Oyun içeriği, ana menü kapatıldığında yükleniyor.
game_loaded = False  # Oyun henüz yüklenmedi

def load_game():
    """Ana menü kapatıldığında çağrılır. Oyun dünyasını oluşturur."""
    global player, boxes, block_types, block_icon, game_loaded

    # Arka plan müziği (1 saniye sonra başlayacak)
    invoke(Audio, 'audio/bg.ogg', delay=1)

    # Oyuncu (ilk başta oluşturuluyor ve load_game sonrasında aktif hale getiriliyor)
    player = FirstPersonController()
    Sky()

    block_list = list(block_types.keys())
    global current_block_index, current_block
    current_block_index = 0
    current_block = block_list[current_block_index]

    # Tüm kutuları saklamak için liste
    global boxes
    boxes = []
    invoke(Audio, 'audio/bg.ogg', delay=2)

    # **Zemin oluşturma** (40x40 alana yerleştirme)
    terrain_size = 40
    for i in range(terrain_size):
        for j in range(terrain_size):
            b = Button(
                color=color.white, 
                model='cube', 
                position=(j, 0, i),
                texture=block_types['1'], 
                parent=scene, 
                origin_y=0.5
            )
            boxes.append(b)

    # **Gerçekçi tepecikler oluşturma** (Çim dokusu kullanılarak)
    for _ in range(t):
        x, z = random.randint(5, terrain_size - 5), random.randint(5, terrain_size - 5)
        peak_height = random.randint(3, 7)
        for h in range(peak_height):
            spread = peak_height - h
            for dx in range(-spread, spread + 1):
                for dz in range(-spread, spread + 1):
                    if random.random() > 0.3:
                        b = Button(
                            color=color.white, 
                            model='cube',
                            position=(x + dx, h, z + dz),
                            texture=block_types['1'], 
                            parent=scene, 
                            origin_y=0.5
                        )
                        boxes.append(b)

    # **Elde tutulan blok simgesi (UI'da sağ alt köşe)**
    global block_icon
    block_icon = Entity(
        model='cube',
        texture=block_types[current_block],
        scale=0.2,
        position=(0.75, -0.4),
        rotation=(30, -45, 0),
        parent=camera.ui
    )

    # FPS sayacı (UI'da sol üst köşe)
    global fps_counter
    fps_counter = Text(
        text="FPS: 0",
        position=(-0.85, 0.45),
        scale=1.5,
        parent=camera.ui
    )

    game_loaded = True

def update_block_icon():
    """Blok değiştiğinde simgeyi günceller."""
    block_icon.texture = block_types[current_block]
    block_icon.animate_scale(0.15, duration=0.1, curve=curve.linear)
    invoke(block_icon.animate_scale, 0.2, duration=0.1, delay=0.1, curve=curve.linear)

def start_game():
    """Start butonuna tıklandığında ana menüyü kapatır ve oyunu yükler."""
    main_menu.disable()  # Ana menü panelini kapatıyoruz.
    load_game()          # Oyun dünyasını oluşturuyoruz.

start_button.on_click = start_game

# ---------- OYUN İÇİ GİRİŞ VE GİRİŞ İŞLEMLERİ (OYUN AKTİF OLDUGUNDA) ----------
def input(key):
    global current_block, current_block_index
    if not game_loaded:
        return

    if key == 'escape':
        if pause_menu.enabled:
            resume_game()
        else:
            pause_menu.enable()
            window.exit_button.visible = True
            mouse.locked = False
        return

    # Klavyeden blok değiştirme (1,2,3,4 tuşları)
    if key in block_types:
        current_block = key
        update_block_icon()

    # Mouse tekerleği ile blok değiştirme
    if key == 'scroll up':
        current_block_index = (current_block_index + 1) % len(list(block_types.keys()))
    elif key == 'scroll down':
        current_block_index = (current_block_index - 1) % len(list(block_types.keys()))
    current_block = list(block_types.keys())[current_block_index]
    update_block_icon()

    # Blok yerleştirme ve silme işlemleri
    target = mouse.hovered_entity
    if target and target in boxes:
        if key == 'right mouse down':
            new_position = target.position + mouse.normal
            if current_block == '4':
                new_entity = Entity(
                    color=color.white,
                    model='cube',
                    position=new_position,
                    texture=block_types[current_block],
                    parent=scene,
                    origin_y=0.5
                )
                new_entity.normal = mouse.normal
                new_entity.look_at(player.position, up=new_entity.normal)
            else:
                new_block = Button(
                    color=color.white,
                    model='cube',
                    position=new_position,
                    texture=block_types[current_block],
                    parent=scene,
                    origin_y=0.5
                )
                boxes.append(new_block)
        elif key == 'left mouse down':
            boxes.remove(target)
            destroy(target)

def update():
    # Oyun yüklenmediyse update işlemlerine devam etmiyoruz.
    if not game_loaded:
        return

    # FPS sayacını güncelle
    if time.dt > 0:
        fps_counter.text = f"FPS: {int(1 / time.dt)}"

    # Eğer oyuncu düşerse, başlangıç konumuna geri getir
    if player.y < -5:
        player.position = (20, 5, 20)  # terrain_size//2 varsayılan olarak 20 kabul edildi.

    # Text Box'ların oyuncuya dönük kalması
    for b in boxes:
        if hasattr(b, 'normal') and b.texture == block_types['4']:
            b.look_at(player.position, up=b.normal)

app.run()
