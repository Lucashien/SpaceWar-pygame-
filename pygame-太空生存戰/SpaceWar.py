import pygame
import random
import os

from pygame import key
from pygame.constants import K_SPACE

# Tips:
# 遊戲為一個迴圈
# 1. 取的玩家輸入(滑鼠點擊、鍵盤......)
# 2. 更新遊戲
# 3. 畫面顯示

# 基本參數設定
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
WIDTH = 500
HEIGHT = 600
FPS = 60

# 遊戲初始化 & 創建視窗
pygame.init()
pygame.init()  # 初始化函式,如果此檔案命明為pygame會出錯
pygame.mixer.init()  # 音效模組初始化
screen = pygame.display.set_mode((WIDTH, HEIGHT))  # 參數(寬,高)
Title = pygame.display.set_caption("SpaceWar")
clock = pygame.time.Clock()  # 因為每個使用者電腦更新速度不一樣，所以在此統一定義
running = True

# 載入圖片
background_img = pygame.image.load(os.path.join("img",
                                                "background.png")).convert()
player_img = pygame.image.load(os.path.join("img", "player.png")).convert()
player_mini_img = pygame.transform.scale(player_img, (25, 25))
player_mini_img.set_colorkey(BLACK)
icon = pygame.display.set_icon(player_mini_img)

rock_imgs = []
for i in range(7):
    rock_imgs.append(
        pygame.image.load(os.path.join("img", f"rock{i}.png")).convert())

bullet_img = pygame.image.load(os.path.join("img", "bullet.png")).convert()

explosion_animation = {}  # dictionary to store list
explosion_animation['large'] = []  # list
explosion_animation['small'] = []
explosion_animation['Player'] = []
for i in range(9):
    explosion_img = pygame.image.load(os.path.join("img",
                                                   f"expl{i}.png")).convert()
    explosion_img.set_colorkey(BLACK)
    large = (75, 75)
    PLAYER = (100, 100)
    small = (30, 30)
    explosion_animation['large'].append(
        pygame.transform.scale(explosion_img, large))
    explosion_animation['small'].append(
        pygame.transform.scale(explosion_img, small))

    player_explosion_img = pygame.image.load(
        os.path.join("img", f"player_expl{i}.png")).convert()
    player_explosion_img.set_colorkey(BLACK)
    explosion_animation['Player'].append(
        pygame.transform.scale(player_explosion_img, PLAYER))

power_imgs = {}
power_imgs['shield'] = pygame.image.load(os.path.join("img",
                                                      "shield.png")).convert()
power_imgs['gun'] = pygame.image.load(os.path.join("img", "gun.png")).convert()

# 載入音樂
shoot_sound = pygame.mixer.Sound(os.path.join("sound", "shoot.wav"))
explosion_sound = [
    pygame.mixer.Sound(os.path.join("sound", "expl0.wav")),
    pygame.mixer.Sound(os.path.join("sound", "expl1.wav"))
]
pygame.mixer.music.load(os.path.join("sound", "background.ogg"))
pygame.mixer.music.set_volume(0.5)

die_sound = pygame.mixer.Sound(os.path.join("sound", "rumble.ogg"))

shield_sound = pygame.mixer.Sound(os.path.join("sound", "pow0.wav"))
gun_sound = pygame.mixer.Sound(os.path.join("sound", "pow1.wav"))

# 遊戲分數
score = 0
font_name = os.path.join("font.ttf")  # 載入字體


def draw_text(surf, text, size, x, y):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, WHITE)  # 渲染出文字
    text_rect = text_surface.get_rect()
    text_rect.centerx = x
    text_rect.top = y
    surf.blit(text_surface, text_rect)


def draw_HP(surf, HP, x, y):
    if HP < 0:
        HP = 0
    BAR_LENGTH = 100
    BAR_HEIGHT = 10
    fill = (HP / 100) * BAR_LENGTH
    outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
    pygame.draw.rect(surf, GREEN, fill_rect)  # 畫填充物
    pygame.draw.rect(surf, WHITE, outline_rect, 2)  # 畫外框


def draw_lives(surf, lives, img, x, y):
    for i in range(lives):
        img_rect = img.get_rect()
        img_rect.x = x + 30 * i  # 間隔距離
        img_rect.y = y
        surf.blit(img, img_rect)


def draw_init():
    screen.blit(background_img, (0, 0))
    draw_text(screen, '太空生存戰', 64, WIDTH / 2, HEIGHT / 4)
    draw_text(screen, '方向鍵：移動飛船 / 空白鍵：發射子彈', 22, WIDTH / 2, HEIGHT / 2)
    draw_text(screen, "按任意鍵開始遊戲", 18, WIDTH / 2, HEIGHT * 3 / 4)
    pygame.display.update()
    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # 跳出迴圈機制:使用者按叉叉
                pygame.quit()
                return True
            elif event.type == pygame.KEYDOWN:  # KEYUP是鬆開
                waiting = False
                return False


# 設定遊戲物件(石頭,子彈......) -> 利用 pygame 內的Sprite
class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.Surface((50, 40))  # 建立此物件長寬
        self.image = pygame.transform.scale(player_img, (50, 38))  # 轉換大小
        self.image.set_colorkey(BLACK)  # 把黑色變透明

        # 將圖片框起來(讓圖片有屬性)
        self.rect = self.image.get_rect()
        self.radius = 22
        #  pygame.draw.circle(self.image, RED, self.rect.center, self.radius)
        self.rect.centerx = WIDTH / 2
        self.rect.bottom = HEIGHT - 10

        self.speedx = 8
        self.speedy = 8
        self.Margin = 5
        self.HP = 100
        self.lives = 3

        self.hidden = False
        self.hide_time = 0

        self.gun = 1
        self.gun_time = 0

    def update(self):
        if self.gun > 1 and pygame.time.get_ticks() - self.gun_time > 8000:
            self.gun -= 1
            self.gun_time = pygame.time.get_ticks()

        if self.hidden and pygame.time.get_ticks(
        ) - self.hide_time > 1000:  # 隱藏1000毫秒後
            self.hidden = False
            self.rect.centerx = WIDTH / 2
            self.rect.bottom = HEIGHT - 10

        key_pressed = pygame.key.get_pressed()  # 回傳是否有按按鍵
        if key_pressed[pygame.K_RIGHT]:
            self.rect.x += self.speedx
        if key_pressed[pygame.K_LEFT]:
            self.rect.x -= self.speedx
        if key_pressed[pygame.K_UP]:
            self.rect.y -= self.speedy
        if key_pressed[pygame.K_DOWN]:
            self.rect.y += self.speedy
        if self.rect.right > WIDTH - self.Margin:
            self.rect.right = WIDTH - self.Margin
        if self.rect.left < self.Margin:
            self.rect.left = self.Margin

    # 射擊指令
    def shoot(self):
        if not (self.hidden):
            if self.gun == 1:
                bullet = Bullet(self.rect.centerx, self.rect.top)
                all_sprites.add(bullet)
                bullets.add(bullet)
                shoot_sound.play()
            elif self.gun == 2:
                bullet1 = Bullet(self.rect.left, self.rect.centery)
                bullet2 = Bullet(self.rect.right, self.rect.centery)

                all_sprites.add(bullet1)
                all_sprites.add(bullet2)
                bullets.add(bullet1)
                bullets.add(bullet2)
                shoot_sound.play()

            elif self.gun >= 3:
                bullet1 = Bullet(self.rect.left, self.rect.centery)
                bullet2 = Bullet(self.rect.centerx, self.rect.top)
                bullet3 = Bullet(self.rect.right, self.rect.centery)

                all_sprites.add(bullet1)
                all_sprites.add(bullet2)
                all_sprites.add(bullet3)

                bullets.add(bullet1)
                bullets.add(bullet2)
                bullets.add(bullet3)
                shoot_sound.play()

    def hide(self):
        self.hidden = True
        self.hide_time = pygame.time.get_ticks()
        self.rect.center = (10000000, 1000000000)

    def gun_up(self):
        self.gun += 1
        self.gun_time = pygame.time.get_ticks()


class Rock(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((30, 40))  # 建立此物件長寬
        self.image_origin = random.choice(rock_imgs)  # 保留因為旋轉而失真的圖片
        self.image = self.image_origin.copy()
        self.image_origin.set_colorkey(BLACK)  # 把黑色變透明

        # 將圖片框起來(讓圖片有屬性)
        self.rect = self.image.get_rect()
        self.radius = self.rect.width * 0.88 / 2
        # pygame.draw.circle(self.image, RED, self.rect.center, self.radius)

        self.rect.x = random.randrange(0, WIDTH - self.rect.width)  # 減去石頭寬度
        self.rect.y = random.randrange(-300, -200)
        self.speedy = random.randrange(2, 8)
        self.speedx = random.randrange(-3, 3)

        self.total_degree = 0
        self.rotate_degree = random.randrange(-3, 3)

    def update(self):
        self.rotate()
        self.rect.y += self.speedy
        self.rect.x += self.speedx
        if self.rect.top > HEIGHT or self.rect.left > WIDTH or self.rect.right < 0:  # 超過畫面就重製
            self.rect.x = random.randrange(0,
                                           WIDTH - self.rect.width)  # 減去 石頭寬度
            self.rect.y = random.randrange(-100, -40)  # 減去石頭寬度
            self.speedy = random.randrange(2, 10)
            self.speedx = random.randrange(-3, 3)

    def rotate(self):
        self.total_degree += self.rotate_degree
        self.total_degree = self.total_degree % 360
        self.image = pygame.transform.rotate(self.image_origin,
                                             self.total_degree)

        # 處理中心定位問題
        center = self.rect.center  # 保留原中心點
        self.rect = self.image.get_rect()  #重新取得屬性
        self.rect.center = center  # 將新屬性變回原本中心點


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):  # 因為子彈跟隨飛船，所以要傳入飛船的x,y
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((10, 20))  # 建立此物件長寬
        self.image = bullet_img
        self.image.set_colorkey(BLACK)  # 把黑色變透明

        # 將圖片框起來(讓圖片有屬性)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speedy = -10

    def update(self):
        self.rect.y += self.speedy
        if self.rect.bottom < 0:
            self.kill()  # Sprite內的刪除物件


class Explotion(pygame.sprite.Sprite):
    def __init__(self, center, size):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = explosion_animation[self.size][0]  # 屬於大爆炸 or 小爆炸
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()  # 回傳從初始化到現在經過的毫秒數
        self.frame_rate = 10  # 更新的時間單位 p.s.怕圖片更新太快

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now  # reset
            self.frame += 1
            if self.frame == len(explosion_animation[self.size]):  # 跑完一輪就刪掉
                self.kill()
            else:
                self.image = explosion_animation[self.size][self.frame]
                center = self.rect.center  # 記錄當下中心點
                self.rect = self.image.get_rect()
                self.rect.center = center


class Power(pygame.sprite.Sprite):
    def __init__(self, center):  # 傳入石頭座標
        pygame.sprite.Sprite.__init__(self)
        self.type = random.choice(['shield', 'gun'])
        self.image = power_imgs[self.type]
        self.image.set_colorkey(BLACK)  # 把黑色變透明

        # 將圖片框起來(讓圖片有屬性)
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.speedy = 3

    def update(self):
        self.rect.y += self.speedy
        if self.rect.top > HEIGHT:
            self.kill()  # Sprite內的刪除物件


pygame.mixer.music.play(-1)  # 無限播放BGM

# 遊戲迴圈
show_init = True
while running:

    if show_init:
        close = draw_init()
        if close:
            break
        show_init = False
        all_sprites = pygame.sprite.Group()  # 設定Sprite(物件)群組
        rocks = pygame.sprite.Group()
        bullets = pygame.sprite.Group()
        players = pygame.sprite.Group()
        powers = pygame.sprite.Group()

        player = Player()
        players.add(player)
        all_sprites.add(player)  # 把 Player 加入群組
        for i in range(8):
            rock = Rock()
            all_sprites.add(rock)
            rocks.add(rock)

    clock.tick(FPS)  # 一秒鐘執行60次
    # 取得輸入
    # 以使用者輸入為迴圈次數，pygame.event.get()為list，所以會跑過list內的所有值
    # e.g. 使用者輸入4個東西就跑4次

    for event in pygame.event.get():
        if event.type == pygame.QUIT:  # 跳出迴圈機制:使用者按叉叉
            running = False
        elif event.type == pygame.KEYDOWN:  # 當按下鍵盤建
            if event.key == pygame.K_SPACE:
                player.shoot()

    # 更新畫面
    all_sprites.update()  # 執行all_sprites內的所有update函式

    # 子彈撞石頭
    hits = pygame.sprite.groupcollide(
        rocks, bullets, True, True,
        pygame.sprite.collide_circle)  # 判斷是否碰到的Sprite函式(回傳dictionary)

    # 把消失的石頭加回來
    for hit in hits:
        random.choice(explosion_sound).play()
        rock = Rock()
        all_sprites.add(rock)
        rocks.add(rock)
        score += int(hit.radius)
        expl = Explotion(hit.rect.center, 'large')
        all_sprites.add(expl)

        if random.random() > 0.8:
            power = Power(hit.rect.center)
            all_sprites.add(power)
            powers.add(power)

    # 石頭撞飛船
    hits = pygame.sprite.groupcollide(players, rocks, False, True,
                                      pygame.sprite.collide_circle)
    for hit in hits:
        rock = Rock()
        all_sprites.add(rock)
        rocks.add(rock)
        player.HP -= hit.radius
        expl = Explotion(hit.rect.center, 'small')
        all_sprites.add(expl)
        if player.HP <= 0:
            die = Explotion(player.rect.center, "Player")
            all_sprites.add(die)
            die_sound.play()
            player.lives -= 1
            player.HP = 100  # 復活
            player.hide()

    if player.lives == 0 and not (die.alive()):
        show_init = True

    # 寶物撞飛船
    hits = pygame.sprite.spritecollide(player, powers, True)

    for hit in hits:
        if hit.type == 'shield':
            player.HP += 10
            shield_sound.play()
            if player.HP >= 100:
                player.HP = 100
        elif hit.type == 'gun':
            gun_sound.play()
            player.gun_up()

    # 畫面顯示
    screen.fill(BLACK)  # (R,G,B)
    screen.blit(background_img, (0, 0))
    all_sprites.draw(screen)
    draw_text(screen, "Score:" + str(score), 18, WIDTH / 2, 10)
    draw_HP(screen, player.HP, 10, 15)
    draw_lives(screen, player.lives, player_mini_img, WIDTH - 100, 15)

    pygame.display.update()

pygame.quit()  # 最後關閉遊戲
