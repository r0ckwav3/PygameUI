import pygame
import PygameUI

# pygame initialization
SCREENSIZE = (480, 240)

pygame.init()
screen = pygame.display.set_mode(SCREENSIZE)

clock = pygame.time.Clock()

# ui elements
PygameUI.UIObject((20,20,100,100))
movingrect = PygameUI.UIObject((20,120,100,100))
movespeed = 100 # pixels per second

PygameUI.Button(
    (50,50,50,30),
    text = "Button",
    onUpdate = lambda : print("clicked!")
)

PygameUI.Textbox((50,100,0,0), (0,0,0), text = "Text", fontsize = 24)

PygameUI.Slider((140,20,100,20), 0, 10, sliderdefault=4)

flag = True
while flag:
    clock.tick(40)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            flag = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                flag = False
        
        PygameUI.all_objects.handleEvent(event)
    
    movingrect.move((clock.get_time()/1000 * movespeed, 0))
    if movingrect.getRect()[0] > SCREENSIZE[0]:
        rwidth = movingrect.getRect()[2]
        movingrect.setRect([-rwidth, None, None, None])

    screen.fill((255, 255, 255))
    PygameUI.all_objects.draw(screen)
    pygame.display.flip()

        