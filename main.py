import math
import pygame
import os
import threading

#pygame insatllieren
pygame.init()
#Soundeffekte werden geladen und ein Bild für das Game-Over-Screen wird geladen.
pygame.mixer.init()
enemy_move_sound = pygame.mixer.Sound('sound/enemy_move.mp3')
sound = pygame.mixer.Sound('sound/shoot.mp3')
#die Lautstärke wird eingestellt,
sound.set_volume(0.5)  # 50% volumen 
#game over bild wird geladen 
game_over_image = pygame.image.load('img/wolfwin.jpg')

# Attribute für die Anzeige der score werden definiert
score_color = (255, 255, 255)  # weiße farbe für score
score_start_size = 36 # schrifft größe am anfang
score_end_size = 48 # scheifft größe am ende 
score_duration = 0.5  # Dauer der Animation in Sekunden

# attribute des scores
score_size = score_start_size
score_time = 0

#screen größen 
WIDTH, HEIGHT = 800, 600
#menü breite
GAME_WIDTH = WIDTH - 200  
MENU_WIDTH = 200
health = 100
FPS = 60

# erleichtert den späteren zugriff auf die images 
game_folder = os.path.dirname(__file__)
img_folder = os.path.join(game_folder, 'img')

# screen erstellen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("sheep Defender")

# hintergrund bild wird geladen
background = pygame.image.load(os.path.join(img_folder, 'background.png')).convert()
background = pygame.transform.scale(background, (GAME_WIDTH, HEIGHT))  # maße werden angepasst 
gray_background = pygame.Surface((MENU_WIDTH, HEIGHT))  
def draw_score():
    # Definiere die Attribute für die Anzeige des Punktestands
    score_color = (255, 255, 255)  # weiße farbe für das text 
    score_bg_color = (0, 0, 0)  # hintergrunds Farbe für das Text (score), schwarz
    score_font_size = 36
    score_pos = (650, 150)  # position der score auf der bildschirm 

    #  die Standard-Pygame-Schriftart wird verwendet
    score_font = pygame.font.Font(None, score_font_size)

    # score wort wird gerendert 
    score_text = score_font.render(f"Score: {Enemy.score}", True, score_color)

    #rect wird erstellt
    score_area = pygame.Rect(score_pos, score_text.get_size())

    # den rect als hintergrund für die score
    pygame.draw.rect(screen, score_bg_color, score_area)

    # den score auf dem bildenschirm zeigen
    screen.blit(score_text, score_pos)

#sound und image des intro , press , damit das spiel anfangen kann

def show_intro_screen():
    #Hier wird der Sound für die Einführungsmusik geladen
    pygame.mixer.music.load('sound/intro.mp3')
# der sound wird unendlcih geladen , bis es getoppt wird (-1)
    pygame.mixer.music.play(-1)  
#Der gesamte Bildschirm wird mit schwarzer Farbe gefüllt, um eine klare Leinwand für den Einführungsbildschirm zu schaffen.
    screen.fill((0, 0, 0))  
    intro_image = pygame.image.load('img/intro_image.jpg')
    intro_image = pygame.transform.scale(intro_image, (800, 500))
    screen.blit(intro_image, (0, 0))

    font = pygame.font.Font(None, 36) 
    text = font.render("Press any key or click to start", True, (255, 255, 255))
    #Der gerenderte Text wird auf den Bildschirm gezeigt
    screen.blit(text, (230,530))#postion des satzes 
    pygame.display.flip()
    #Wenn der Anwender eine Taste drückt oder auf die Maus klickt, wird der Startbildschirm beendet und geht zum nächsten Teil des Spiels über. Beim Schließen des Fensters wird das Spiel beendet. Das wird mit der folgenden while-Schleife realisiert:




    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                #sys.exit()
            elif event.type == pygame.KEYUP or event.type == pygame.MOUSEBUTTONUP:
                return

#schüsse der Hunter , sind Rot aus der Hunter Waffe
class Bullet(pygame.sprite.Sprite):
    #Zuerst werden die Attribute definiert. Wir haben uns für rote Projektile entschieden. 
    #Bei den Attributen werden auch die Startposition, das Ziel und die Geschwindigkeit angegeben.

    def __init__(self, start_pos, target):
        super().__init__()
        self.image = pygame.Surface((5, 5))
        self.image.fill((255, 0, 0))  
        self.rect = self.image.get_rect(center=start_pos)
        self.target = target
        self.speed = 15  # Geschwindigkeit der enemies anpassbar

        
        #Wölfe in der Range der hunter werden attakiert 
        dx, dy = self.target.rect.centerx - self.rect.centerx, self.target.rect.centery - self.rect.centery
        dist = math.hypot(dx, dy)
        self.dx, self.dy = dx / dist, dy / dist   
        self.pos = list(start_pos)

    def update(self):
         # hier  wird die Position des Projektils basierend auf der Geschwindigkeit und der Richtung aktualisiert.
        self.pos[0] += self.dx * self.speed
        self.pos[1] += self.dy * self.speed
        self.rect.center = self.pos  # Update the rect

        # Danach wird überprüft, ob der Gegner getroffen wird. Wenn ja, wird die Gesundheit des Gegners um 1 Punkt verringert und das Projektil verschwindet mit der Methode self.kill(), wenn es einen Gegner getroffen hat.

        
        if pygame.sprite.spritecollide(self, enemies, False):
            self.target.enemy_health -= 1
            self.kill()

#Die Klasse "Tower" repräsentiert  die Rolle eines Jägers
# Hunter Animation 
class Tower(pygame.sprite.Sprite):
    def __init__(self, pos):
        pygame.sprite.Sprite.__init__(self)
        self.frames = [pygame.transform.scale(pygame.image.load(os.path.join(img_folder, f'tower{i}.png')).convert_alpha(), (70, 70)) for i in range(6)]
        self.current_frame = 0 # frame wird auf 0 gesetzt, um das erste Bild der Animation zu repräsentieren.
        self.image = self.frames[self.current_frame]
        self.rect = self.image.get_rect()
        self.rect.center = pos# plazierung der hunter 
        self.range = 100 #reichweite für das hunter um due enmy (wölfe) zu erkennen
        self.last_anim = pygame.time.get_ticks()
        self.anim_delay = 100
        self.shoot_delay = 500  

    def update(self):
        #enemy wird in der range des hunter gesucht
        target = next((enemy for enemy in enemies if math.hypot(self.rect.centerx - enemy.rect.centerx, self.rect.centery - enemy.rect.centery) <= self.range), None)

        if target is not None:
            #zeit wird aktulisiert wenn ein enemy in der range eines hunters gefunden würde
            now = pygame.time.get_ticks()
            #Überprüft, ob genügend Zeit seit der letzten Animation vergangen ist, basierend auf der Animationsverzögerung des hunters.
            if now - self.last_anim >= self.anim_delay:
                self.current_frame = (self.current_frame + 1) % 6
                self.image = self.frames[self.current_frame]
                self.last_anim = now

                if self.current_frame == 3:# Überprüft, ob der aktuelle Frame den Wert 3 hat, damit die sound der schüsss gespielt wird 
                    sound.play()

                    bullet = Bullet(self.rect.center, target)
                    bullets.add(bullet)
                    all_sprites.add(bullet)
                    self.current_frame = (self.current_frame + 1) % 6  # Aktualisiert den aktuellen Frame  um 1 weiter.
                    self.image = self.frames[self.current_frame]#Aktualisiert das Bild des Objekts auf den neuen Frame.
                    self.last_anim = pygame.time.get_ticks()  # Setzt den Verzögerungstimer zurück, um die Zeit seit der letzten Animation zu speichern.
                
            
#spiel Variabelen 
enemies_reached_end = 0
killed_enemies = 0
killed_score = 0
#enemy class 
class Enemy(pygame.sprite.Sprite):
    score = 0  
    killed_enemies = 0  
    current_image_index = 0  

    def __init__(self, waypoints):
        pygame.sprite.Sprite.__init__(self)
        self.images = [pygame.image.load('img/wolf1.png'), pygame.image.load('img/wolf2.png'), pygame.image.load('img/wolf3.png'), pygame.image.load('img/wolf4.png')]
        self.image = pygame.transform.scale(self.images[Enemy.current_image_index], (30, 30))  # Skaliert das Bild auf 30x30 Pixel
        
        self.rect = self.image.get_rect()
        self.rect.center = waypoints[0]  # Start am ersten waypoint
        self.speed = 5

        self.waypoints = waypoints
        self.current_waypoint = 0
        self.enemy_health = 1  
        self.last_image_change = pygame.time.get_ticks()

    def update(self):
        # Berechne die Richtung zum nächsten waypoint
        global health  # health als globale Variable deklarieren
        #  Differenz in den x- und y-Koordinaten zwischen dem aktuellen Ort des enmeys und dem nächsten Waypoint berechnen
        dx, dy = self.waypoints[self.current_waypoint][0] - self.rect.x, self.waypoints[self.current_waypoint][1] - self.rect.y
        distance = math.sqrt(dx**2 + dy**2)# die Entfernung zum nächsten Waypoint mit dem Satz des Pythagoras wird hier berechnet 
        if distance < self.speed:  # Wenn der enemy  nahe am Wegpunkt ist, zum nächsten gehen
            self.current_waypoint += 1
            if self.current_waypoint >= len(self.waypoints):  # Wenn der enemy  nahe am Waypoint  ist, zum nächsten gehen
                self.current_waypoint = 0
        else:  # Wenn der enemy  nicht nahe am Waypoint  ist, bewege dich darauf zu
            self.rect.x += dx / distance * self.speed
            self.rect.y += dy / distance * self.speed
        
        if self.enemy_health == 0:
            self.kill()
            Enemy.killed_enemies += 1  # Erhöht die Anzahl der getöteten enemies
            if Enemy.killed_enemies % 20 == 0:
                Enemy.current_image_index = (Enemy.current_image_index + 1) % len(self.images)
                
            global killed_enemies
            killed_enemies += 1
            global killed_score
            killed_score += 1
        if self.rect.topleft == waypoints[-1]:
            self.kill()
            health -= 10  # Verringert die health um 10. Dies deutet darauf hin, dass das Erreichen des Zielbereichs(route vollendet) durch das enemy zu einer Strafe in Form von health abnahme führt.

            if health == 0:
                show_end_screen()

            

#  Definiere die Button-Klasse
def show_end_screen(): 
    #stoppt die Hintergrundmusik.
    pygame.mixer.music.stop()
    end_sound = pygame.mixer.Sound('sound/level-failed.mp3')
    end_sound.play()#spielt den Soundeffekt der spiel ende  ab.
    end_image = pygame.image.load('img/wolfwin.jpg')
    end_image = pygame.transform.scale(end_image, (800, 600))
    screen.blit(end_image, (0, 0))#game over bild zeigen
    font = pygame.font.Font(None, 36)
    text = font.render("Game Over!! You Suck!!", True, (255, 0, 0))#erstellt den Text mit roter Farbe.
    screen.blit(text, (230, 570))# Position des Textes auf dem Bildschirm.



    pygame.display.flip()#bildschirm aktuliesrieren

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                #sys.exit()
class Button:
    def __init__(self, image, x, y, width, height, text=''):
        self.image = pygame.image.load(f'img/{image}')
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text

    def draw(self, screen, outline=None):
        # button auf das bildschirm erscheinen lassen
        if outline:
            pygame.draw.rect(screen, outline, (self.x-2, self.y-2, self.width+4, self.height+4), 0)
        screen.blit(self.image, (self.x, self.y))
        
        if self.text != '':
            font = pygame.font.SysFont('comicsans', 50)
            text = font.render(self.text, 1, (0,0,0))
            screen.blit(text, (self.x + (self.width/2 - text.get_width()/2), self.y + (self.height/2 - text.get_height()/2)))#text in der mitte des button platzieren
            
    def clicked(self, pos):
        #  prüfen, ob die Mausposition innerhalb der Begrenzungen des Buttons liegt, und geben True zurück, wenn ja, andernfalls False
        if self.x < pos[0] < self.x + self.width:
            if self.y < pos[1] < self.y + self.height:
                return True
        return False

# Erstellung von Sprite-Gruppen
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
towers = pygame.sprite.Group()
bullets = pygame.sprite.Group()

# 1 block size = 40
waypoints = [
    (525, 50),(525, 125),
    (525, 125),(50, 125),
    (50, 205),(490, 205),
    (490, 325),(160, 325),
    (160, 360),(120, 360),
    (120, 480),(570, 480),
    (570, 560),(0, 560)
]


button = Button('start.png', WIDTH - MENU_WIDTH + 50, 50, 100, 50, '')

# Game loop
running = True
game_started = True
countdown = 3  # Countdown für 3 Sekunden 
font = pygame.font.Font(None, 74)  # größe des zahl für countdown
#health bar breite und höhe werden bestimmt, health bar  dient als Maßstab dafür, wie viele Feinde der Jäger nicht getötet hat.
HEALTH_BAR_WIDTH = 150
HEALTH_BAR_HEIGHT = 20
health_bar_x = WIDTH - MENU_WIDTH + (MENU_WIDTH - HEALTH_BAR_WIDTH) // 2  # health bar im munü platzieren
health_bar_y = 100   
enemies_created = False
last_enemy_creation_time = 0
score_font = pygame.font.Font(None, 36)

# Hier werden die Variablen für die Anzahl der platzierten hunters (towers_placed) und die Anzahl der Credits (credits) initialisiert.
towers_placed = 0
credits = 0  # start mit 0 credits
font = pygame.font.Font(None, 36)
previous_enemy_count = len(enemies)#
show_intro_screen()
pygame.mixer.music.load('sound/theme.mp3')#Lädt die Hintergrundmusik
pygame.mixer.music.play(-1)  # musik theme wird unendlich wiederholt

while running:
    
  

    pygame.time.Clock().tick(FPS)
   
    

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if button.clicked(pygame.mouse.get_pos()):
                game_started = True
            elif game_started and event.button == 1:  # Erlaubt nur das Platzieren von Türmen, wenn das Spiel gestartet wurde und die linke Maustaste geklickt wurde
                if towers_placed < 2 or credits >= 5:
                    mouse_pos = pygame.mouse.get_pos()
                    tower = Tower(mouse_pos)
                    all_sprites.add(tower)
                    towers.add(tower)
                    towers_placed += 1
                    killed_enemies = 0
                    if credits >= 5:
                        credits -= 5
    credits = killed_enemies#  Die Anzahl der Credits wird auf die Anzahl der getöteten Feinde gesetzt
    Enemy.score = killed_score
    menu_background = pygame.Surface((MENU_WIDTH, HEIGHT))
    menu_background.fill((128, 128, 128))  

    #  Zeichnet den Menü-Hintergrund auf den Bildschirm
    screen.blit(menu_background, (GAME_WIDTH, 0))                
    if game_started:
            if countdown > 0:
                countdown -= 1/FPS  # Verringere den Countdown um 1 jede Sekunde
                health_bar_width = (1 - countdown / 3) * HEALTH_BAR_WIDTH  # The health bar ffüllt sich während des Countdowns
                pygame.draw.rect(screen, (255, 255, 255), pygame.Rect(health_bar_x, health_bar_y, health_bar_width, HEALTH_BAR_HEIGHT))  # health bar in weiß
            else:
                pygame.draw.rect(screen, (150, 0, 0), pygame.Rect(health_bar_x, health_bar_y, health, HEALTH_BAR_HEIGHT))  # health bar in Rot zeigen

                current_time = pygame.time.get_ticks()
                if current_time - last_enemy_creation_time >= 1000:  # 1000 milliseconds = 1 second
                    # Erstelle einen Feind
                    e = Enemy(waypoints)
                    all_sprites.add(e)
                    enemies.add(e)
                    last_enemy_creation_time = current_time#Aktualisiert den Zeitpunkt der letzten Feinderstellung
            
    MENU_WIDTH = 200  # breite des panel


    # Update
    all_sprites.update()

    # Draw 
    screen.blit(background, (0, 0))

    all_sprites.draw(screen) # Alle Spielobjekte zeichnen
    #menu_background = pygame.Surface((MENU_WIDTH, HEIGHT))
    #menu_background.fill((128, 128, 128))  # Fill with gray color

    # Draw the menu background onto the screen
    #screen.blit(menu_background, (GAME_WIDTH, 0))
    


    
    
    # zeichne die button
    button.draw(screen)

    if game_started and countdown > 0:
        countdown_text = font.render(str(int(countdown)), True, (255, 255, 255))  #  Erstelle eine Oberfläche mit dem Countdown
        screen.blit(countdown_text, ((WIDTH - countdown_text.get_width()) // 2, (HEIGHT - countdown_text.get_height()) // 2))  
        # Zeichne den Countdown in der Mitte des Bildschirms

    draw_score()  # score erscheien lassen
    text = font.render(f"Credits: {credits}", True, (255, 255, 255))
    screen.blit(text, (640, 210))#  Zeichne den Text "Credits" auf den Bildschirm

    # Umschaltet den Bildschirm, um die gezeichneten Änderungen anzuzeigen.
    pygame.display.flip()

pygame.quit()