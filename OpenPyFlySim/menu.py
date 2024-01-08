import pygame 
import sys 
import main
from maths_module import getDatafileData, writeDatafileData
import crash_handler

class Button:
    def __init__(self, screen, x, y, w, h, text, font):
        self._x = x # x pos
        self._y = y # y pos

        self._w = w # width
        self._h = h # height

        self._light = (170,170,170) 
        self._dark = (100,100,100)

        self._screen = screen   # Pointer to the screen
        self._text = font.render(text , True , (255,255,255))

    def render(self, mouse):
        if self._x <= mouse[0] <= self._x+self._w and self._y <= mouse[1] <= self._y+self._h:
            pygame.draw.rect(self._screen,self._light,[self._x,self._y,self._w,self._h]) 
        else: 
            pygame.draw.rect(self._screen,self._dark,[self._x,self._y,self._w,self._h])

        self._screen.blit(self._text, (self._x+90, self._y+55))

    def checkForClick(self,mouse):
        if self._x <= mouse[0] <= self._x+self._w and self._y <= mouse[1] <= self._y+self._h:
            return True # Success
        else:
            return False    # Failiure

class Checkbox(Button):
    def __init__(self, screen, x, y, w, h):
        Button.__init__(self, screen, x, y, w, h, "", pygame.font.SysFont('Corbel',60))
        self.flag = False   # Determines whether the checkbox is on or off

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
            return True # Success
        else:
            return False    # Failiure


def menu():
    try:
        crash_handler.sendErrorLogs()
    except:
        print("Servers offline.")
    pygame.init() 

    width = 1500
    height = 1000

    screen = pygame.display.set_mode((width,height))
    
    # Define fonts
    font = pygame.font.SysFont('Corbel',60)
    smallfont = pygame.font.SysFont('Corbel',30)

    # Define texts
    textTitle = font.render('OpenPyFlySin' , True , (255,100,100) )
    textCredits = font.render('Adrian Draber 22018721' , True , (255,100,100) )
    checkboxLine1 = smallfont.render('I consent to my data being collected and' , True , (255,255,255) )
    checkboxLine2 = smallfont.render('used in crash reports to improve this program' , True , (255,255,255) )

    # Define buttons
    buttonA = Button(screen, (width/2)+100, (height/2)-100, 300, 150, "START", font)
    buttonB = Button(screen, (width/2)+100, (height/2)+100, 300, 150, "QUIT", font)
    checkBox = Checkbox(screen, (width/2)+100, (height/2)+300, 100, 100)

    checkon = getDatafileData("datacheckboxon")
    print(checkon)
    if checkon == "1":
        checkBox.flag = True

    # Map of the game world
    mapImg = pygame.image.load("colourmap.bmp").convert()
    
    while True:     
        for event in pygame.event.get(): 
            
            if event.type == pygame.QUIT: 
                pygame.quit()
                
            #   Checks if a mouse is clicked 
            if event.type == pygame.MOUSEBUTTONDOWN: 
                
                #   This option starts the game
                if buttonA.checkForClick(mouse): 
                    pygame.quit()
                    if checkBox.flag: #save state of checkbox
                        binary_bool = 1
                    else:
                        binary_bool = 0
                    writeDatafileData("datacheckboxon", binary_bool)
                    main.main(checkBox.flag)

                #   This option closes the launcher
                if buttonB.checkForClick(mouse): 
                    if checkBox.flag: #save state of checkbox
                        binary_bool = 1
                    else:
                        binary_bool = 0
                    writeDatafileData("datacheckboxon", binary_bool)
                    pygame.quit()

                checkBox.checkForClick(mouse)   # Toggles the checkbox
                    
        screen.fill((0,0,0)) 
        mouse = pygame.mouse.get_pos() 
        
        buttonA.render(mouse)
        buttonB.render(mouse)
        checkBox.render(mouse)
        
        screen.blit(textTitle, ((width/2)+100,100))
        screen.blit(textCredits, ((width/2)+100,200))

        screen.blit(checkboxLine1, ((width/2)+230,(height/2)+320))
        screen.blit(checkboxLine2, ((width/2)+230,(height/2)+350))

        screen.blit(mapImg, (100, 220))

        pygame.display.update() 

if __name__ == "__main__":
    menu()