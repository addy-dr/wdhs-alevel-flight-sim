import pygame 
import sys 
import main

class Button:
    def __init__(self, screen, x, y, w, h, text, font):
        self._x = x # x pos
        self._y = y # y pos

        self._w = w # width
        self._h = h # height

        self._light = (170,170,170) 
        self._dark = (100,100,100)

        self._screen = screen # pointer to the screen
        self._text = font.render(text , True , (255,255,255) )

    def render(self, mouse):
        if self._x <= mouse[0] <= self._x+self._w and self._y <= mouse[1] <= self._y+self._h:
            pygame.draw.rect(self._screen,self._light,[self._x,self._y,self._w,self._h]) 
        else: 
            pygame.draw.rect(self._screen,self._dark,[self._x,self._y,self._w,self._h])

        self._screen.blit(self._text, (self._x+90, self._y+55))

    def checkForClick(self,mouse):
        if self._x <= mouse[0] <= self._x+self._w and self._y <= mouse[1] <= self._y+self._h:
            return True #success
        else:
            return False #failiure

class Checkbox(Button):
    def __init__(self, screen, x, y, w, h):
        Button.__init__(self, screen, x, y, w, h, "", pygame.font.SysFont('Corbel',60))
        self.flag = False #determines whether the checkbox is on or off

    def render(self, mouse):
        if self._x <= mouse[0] <= self._x+self._w and self._y <= mouse[1] <= self._y+self._h:
            pygame.draw.rect(self._screen,self._light,[self._x,self._y,self._w,self._h])
            pygame.draw.rect(self._screen,(0,0,0),[self._x+10,self._y+10,self._w-20,self._h-20])
            if self.flag:
                pygame.draw.rect(self._screen,self._light,[self._x+20,self._y+20,self._w-40,self._h-40]) 
        else: 
            pygame.draw.rect(self._screen,self._dark,[self._x,self._y,self._w,self._h])
            pygame.draw.rect(self._screen,(0,0,0),[self._x+10,self._y+10,self._w-20,self._h-20])
            if self.flag:
                pygame.draw.rect(self._screen,self._dark,[self._x+20,self._y+20,self._w-40,self._h-40])

    def checkForClick(self,mouse):
        if self._x <= mouse[0] <= self._x+self._w and self._y <= mouse[1] <= self._y+self._h:
            if self.flag:
                self.flag = False
            else:
                self.flag = True
            return True #success
        else:
            return False #failiure

def menu():
    pygame.init() 

    color_light = (170,170,170) 
    color_dark = (100,100,100) 
    
    width = 1500
    height = 1000

    screen = pygame.display.set_mode((width,height))
    
    font = pygame.font.SysFont('Corbel',60)
    smallfont = pygame.font.SysFont('Corbel',30)

    textTitle = font.render('OpenPyFlySin' , True , (255,100,100) )
    textCredits = font.render('Adrian Draber 22018721' , True , (255,100,100) )

    checkboxLine1 = smallfont.render('I consent to my data being collected and' , True , (255,255,255) )
    checkboxLine2 = smallfont.render('used in crash reports to improve this program' , True , (255,255,255) )

    buttonA = Button(screen, (width/2)+100, (height/2)-100, 300, 150, "START", font)
    buttonB = Button(screen, (width/2)+100, (height/2)+100, 300, 150, "QUIT", font)
    checkBox = Checkbox(screen, (width/2)+100, (height/2)+300, 100, 100)

    i = pygame.image.load("colourmap.bmp").convert()
    
    while True:     
        for event in pygame.event.get(): 
            
            if event.type == pygame.QUIT: 
                pygame.quit()
                
            #checks if a mouse is clicked 
            if event.type == pygame.MOUSEBUTTONDOWN: 
                
                #this option starts the game
                if buttonA.checkForClick(mouse): 
                    pygame.quit() 
                    main.main(checkBox.flag)

                #this option closes the launcher
                if buttonB.checkForClick(mouse): 
                    pygame.quit()

                checkBox.checkForClick(mouse) #no immediate effect
                    
        screen.fill((0,0,0)) 
        mouse = pygame.mouse.get_pos() 
        
        buttonA.render(mouse)
        buttonB.render(mouse)
        checkBox.render(mouse)
        
        screen.blit(textTitle, ((width/2)+100,100))
        screen.blit(textCredits, ((width/2)+100,200))

        screen.blit(checkboxLine1, ((width/2)+230,(height/2)+320))
        screen.blit(checkboxLine2, ((width/2)+230,(height/2)+350))

        screen.blit(i, (100, 220))

        pygame.display.update() 

if __name__ == "__main__":
    menu()