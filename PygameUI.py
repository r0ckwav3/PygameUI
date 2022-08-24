from unittest import TextTestRunner
import pygame
import copy
import math

#########################
## Font Initialization ##
#########################

defaultfont = "sfns"
fontpathdict = {}
fontdict = {}

# I might add support for bold and italics here
def getFont(fontname, fontsize):
    if fontname not in fontpathdict:
        if fontname in pygame.font.get_fonts():
            fontpathdict[fontname] = pygame.font.match_font(fontname)
        else:
            message = """You do not have the font %s installed. A list of avalible fonts may be found with pygame.font.get_fonts().""" % fontname
            raise pygame.error(message)

    if (fontname, fontsize) not in fontdict:
        fontdict[(fontname, fontsize)] = pygame.font.Font(fontpathdict[fontname], fontsize)

    return fontdict[(fontname, fontsize)]


#############
## Helpers ##
#############

def inRect(pos, rect):
    return (0 <= pos[0]-rect[0] <= rect[2]) and (0 <= pos[1]-rect[1] <= rect[3])

# renders text to a surface (very similar to font.render) but supports newlines
# spacing does not count the text's height, so single spaced is spacing=1
def multilineFontRender(font, text, antialiased, textcolor, bgcolor, spacing=1.15):
    splittext = text.split("\n")
    neededwidth = 0
    neededheight = 0
    for line in splittext:
        rendersize = font.size(line)
        neededwidth = max(neededwidth, rendersize[0])
        neededheight += rendersize[1] * spacing
        # this gets us slightly more space than we need on the last line, but that shouldn't affect anything

    textsurface = pygame.surface.Surface((neededwidth, neededheight), pygame.SRCALPHA)
    textsurface.fill((0,0,0,0))
    accumheight = 0

    for line in splittext:
        textsurface.blit(
            font.render(line, antialiased, textcolor, bgcolor),
            [0,accumheight,0,0]
        )
        rendersize = font.size(line)
        accumheight += rendersize[1] * spacing
    
    return textsurface


#############
## Classes ##
#############

# base ui object
# if used, draws a solid magenta rectangle
class UIObject:
    # initialization see handleEvent for use of onUpdate
    # rect: int[4]
    # color: int[3] or pygame.color
    # onUpdate: function
    def __init__(self, rect, onUpdate = None):
        self.rect = rect
        self.onUpdate = onUpdate
        all_objects.addObject(self)
        
    
    # draws the object onto the given surface and returns that surface
    # surface: pygame.Surface
    # -> pygame.Surface
    def draw(self, surface):
        pygame.draw.rect(surface, (255,0,255), self.rect)
        return surface

    # handles any events that would affect the UI object. When an event changes the state of the UI element,
    # it calls onUpdate(getState()).
    # event: pygame.event
    def handleEvent(self, event):
        pass
    
    # moves the uiobject by a certain amount
    # drect: int[4]
    def move(self, dpos):
        self.rect = [self.rect[0]+dpos[0],self.rect[1]+dpos[1],self.rect[2],self.rect[3]]

    # moves the uiobject to a new location. put None in the list to keep something the same
    # newrect: int[4]
    def setRect(self, newrect):
        for i in range(4):
            if newrect[i] is not None:
                self.rect[i] = newrect[i]

    # gets the current rectangle
    # -> int[4]
    def getRect(self):
        return self.rect

    # returns the state of the UI object. The return type depends on the object.
    # -> NoneType
    def getState(self):
        return None

    # resets the state of the UI object. e.g. clearing a text box.
    def reset(self):
        pass

# a helpful way to group UIObjects, almost all of these functions just call the same functions on the members
class UIObjectGroup:
    def __init__(self, objects = None):
        if objects is None:
            self.objects = []
        else:
            self.objects = objects
    
    # adds an object to the group
    # object: UIObject
    def addObject(self, object):
        self.objects.append(object)
    
    # removes an object from the group
    # object: UIObject
    def removeObject(self, object):
        self.objects.remove(object)
    
    # returns a list of the objects in this group.
    # This list is mutable, but it is advised to use addObject and removeObject instead.
    # -> UIObject[]
    def getObjects(self):
        return self.objects
    
    def draw(self, surface):
        for o in self.objects:
            o.draw(surface)

    def handleEvent(self, event):
        for o in self.objects:
            o.handleEvent(event)

    def reset(self):
        for o in self.objects:
            o.reset()

# a box containing text. Due to the way that pygame's fonts work, this currently does not support newlines.
# also note that the width and height of the rect will be ignored, instead only using the corner to place text.
# onUpdate is ignored
class Textbox(UIObject):
    def __init__(self, rect, textcolor = (0,0,0), bgcolor = None, text = "", fontname = "sfns", fontsize = 12, spacing = 1.15, onUpdate = None):
        super().__init__(rect,onUpdate)
        self.text = text
        self.spacing = spacing

        self.textcolor = pygame.Color(textcolor)
        self.bgcolor = None if bgcolor is None else pygame.Color(bgcolor)

        self.font = getFont(fontname, fontsize)

    def draw(self, surface):
        # textsurface = self.font.render(self.text, True, self.textcolor, self.bgcolor)
        textsurface = multilineFontRender(self.font, self.text, True, self.textcolor, self.bgcolor, self.spacing)
        surface.blit(textsurface, self.rect)

# similar to a textbox, but will change color when hovered over and activates the onUpdate() function when clicked.
# notably, unlike the other UIObjects, it does not pass anything to onUpdate
class Button(UIObject):
    def __init__(self, rect, textcolor=(0,0,0), bgcolor=(192,192,192), bgcolor2=None, bgcolor3=None, text = "", fontname = "sfns", fontsize = 12, onUpdate = None):
        super().__init__(rect,onUpdate)
        self.text = text
        self.textcolor = pygame.Color(textcolor)

        # self.bgcolor is the active one
        # self.bgcolor1 is when not hovered over
        # self.bgcolor2 is when hovered over
        # self.bgcolor3 is when clicked
        self.bgcolor1 = pygame.Color(bgcolor)

        if bgcolor2 is None:
            self.bgcolor2 = copy.deepcopy(self.bgcolor1)
            oldhsva = self.bgcolor2.hsva
            self.bgcolor2.hsva = (oldhsva[0],oldhsva[1],oldhsva[2]*0.9,oldhsva[3])
        else:
            self.bgcolor2 = bgcolor2

        if bgcolor3 is None:
            self.bgcolor3 = copy.deepcopy(self.bgcolor1)
            oldhsva = self.bgcolor3.hsva
            self.bgcolor3.hsva = (oldhsva[0],oldhsva[1],oldhsva[2]*0.8,oldhsva[3])
        else:
            self.bgcolor3 = bgcolor3

        self.bgcolor = self.bgcolor1

        if fontname is None:
            fontname = "sfns"
        if fontsize is None:
            fontsize = 12
        self.font = getFont(fontname, fontsize)

    def draw(self, surface):
        pygame.draw.rect(
            surface,
            self.bgcolor,
            self.rect,
            border_radius=min(self.rect[2],self.rect[3])//3
        )
        textsurface = multilineFontRender(self.font, self.text, True, self.textcolor, self.bgcolor)
        blitrect = [
           self.rect[0] + ((self.rect[2]-textsurface.get_width())//2),
           self.rect[1] + ((self.rect[3]-textsurface.get_height())//2),
           0,
           0]
        surface.blit(textsurface, blitrect)

    def handleEvent(self, event):
        # handle colors
        if event.type in [pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP]:
            if not inRect(event.pos, self.rect):
                self.bgcolor = self.bgcolor1
            elif pygame.mouse.get_pressed()[0]:
                self.bgcolor = self.bgcolor3
            else:
                self.bgcolor = self.bgcolor2
        
        # handle clicks
        if event.type == pygame.MOUSEBUTTONDOWN:
            if inRect(event.pos, self.rect) and event.button == 1:
                if self.onUpdate is not None:
                    self.onUpdate()

# a line with a handle that slides between a given max and min
# if discrete is true, the slider will snap to the nearest integer.
# if false, it snaps to the nearest pixel.
class Slider(UIObject):
    def __init__(self, rect, slidermin, slidermax, discrete=True, sliderdefault=None, linecolor=(128,128,128), handlecolor=(192,192,192), linesize=None, onUpdate=None):
        super().__init__(rect, onUpdate)
        self.slidermin = slidermin
        self.slidermax = slidermax
        self.discrete = discrete
        
        self.linecolor = pygame.Color(linecolor)
        self.handlecolor = pygame.Color(handlecolor)

        self.linesize = rect[3]//3 if linesize is None else linesize
        self.sliderdefault = slidermin if sliderdefault is None else sliderdefault

        self.slidervalue = self.sliderdefault
        self.clickedon = False
        
    def draw(self, surface):
        pygame.draw.rect(
            surface,
            self.linecolor,
            [
                self.rect[0],
                self.rect[1]+(self.rect[3]-self.linesize)//2,
                self.rect[2],
                self.linesize
            ],
            border_radius = self.linesize//2
        )

        sliderfrac = (self.slidervalue-self.slidermin)/(self.slidermax-self.slidermin)
        pygame.draw.circle(
            surface,
            self.handlecolor,
            (
                self.rect[0] + int(sliderfrac*self.rect[2]),
                self.rect[1] + self.rect[3]//2
            ),
            self.rect[3]//2
        )
        return surface

    def handleEvent(self, event):
        # handle self.clickedon
        if event.type == pygame.MOUSEBUTTONDOWN:
            if inRect(event.pos, self.rect) and event.button == 1:
                self.clickedon = True
        
        elif event.type == pygame.MOUSEBUTTONUP:
            self.clickedon = False
        
        # update slider position
        if event.type == pygame.MOUSEMOTION or event.type == pygame.MOUSEBUTTONDOWN:
            if self.clickedon:
                sliderfrac = (event.pos[0] - self.rect[0])/self.rect[2]
                
                # enforce bounds
                if sliderfrac < 0: 
                    sliderfrac = 0
                if sliderfrac > 1:
                    sliderfrac = 1
                
                # calculate value and round if necessary
                self.slidervalue = (sliderfrac * (self.slidermax - self.slidermin)) + self.slidermin
                if self.discrete:
                    self.slidervalue = int(round(self.slidervalue))

                # call onupdate
                if self.onUpdate is not None:
                    self.onUpdate(self.getState())
    
    def getState(self):
        return self.slidervalue

    def reset(self):
        self.slidervalue = self.sliderdefault
        self.onUpdate(self.getState())

# very similar to a button, but is toggled by clicking
class Toggle(UIObject):
    def __init__(self, rect, textcolor=(0,0,0), bgcolor=(192,192,192), bgcolor2=None, bgcolor3=None, bgcolor4=None, text = "", fontname = "sfns", fontsize = 12, onUpdate = None):
        super().__init__(rect,onUpdate)
        self.text = text
        self.textcolor = pygame.Color(textcolor)

        self.state = False

        # self.bgcolor is the active one
        # self.bgcolor1 is when off 
        # self.bgcolor2 is when off, hovered over
        # self.bgcolor3 is when on
        # self.bgcolor4 is when on, hovered over
        self.bgcolor1 = pygame.Color(bgcolor)

        if bgcolor2 is None:
            self.bgcolor2 = copy.deepcopy(self.bgcolor1)
            oldhsva = self.bgcolor2.hsva
            self.bgcolor2.hsva = (oldhsva[0],oldhsva[1],oldhsva[2]*0.9,oldhsva[3])
        else:
            self.bgcolor2 = bgcolor2

        if bgcolor3 is None:
            self.bgcolor3 = copy.deepcopy(self.bgcolor1)
            oldhsva = self.bgcolor3.hsva
            self.bgcolor3.hsva = (oldhsva[0],oldhsva[1],oldhsva[2]*0.8,oldhsva[3])
        else:
            self.bgcolor3 = bgcolor3
        
        if bgcolor4 is None:
            self.bgcolor4 = copy.deepcopy(self.bgcolor1)
            oldhsva = self.bgcolor4.hsva
            self.bgcolor4.hsva = (oldhsva[0],oldhsva[1],oldhsva[2]*0.7,oldhsva[3])
        else:
            self.bgcolor4 = bgcolor4

        self.bgcolor = self.bgcolor1

        self.font = getFont(fontname, fontsize)

    def draw(self, surface):
        pygame.draw.rect(
            surface,
            self.bgcolor,
            self.rect,
            border_radius=min(self.rect[2],self.rect[3])//3
        )
        textsurface = self.font.render(self.text, True, self.textcolor)
        textsurface = self.font.render(self.text, True, self.textcolor, self.bgcolor)
        blitrect = [
           self.rect[0] + ((self.rect[2]-textsurface.get_width())//2),
           self.rect[1] + ((self.rect[3]-textsurface.get_height())//2),
           0,
           0]
        surface.blit(textsurface, blitrect)

    def handleEvent(self, event):
        # handle clicks
        if event.type == pygame.MOUSEBUTTONDOWN:
            if inRect(event.pos, self.rect) and event.button == 1:
                self.state = not self.state
                if self.onUpdate is not None:
                    self.onUpdate(self.getState())

        # handle colors
        if event.type in [pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN]:
            if inRect(event.pos, self.rect):
                if self.state:
                    self.bgcolor = self.bgcolor4
                else:
                    self.bgcolor = self.bgcolor2
            else:
                if self.state:
                    self.bgcolor = self.bgcolor3
                else:
                    self.bgcolor = self.bgcolor1
    
    def getState(self):
        return self.state
    
    def reset(self):
        self.state = False


class Textfield(UIObject):
    def __init__(self, rect, textcolor=(0,0,0), bgcolor=(192,192,192), bordercolor=(0,0,0), defaulttext = "", allownewlines=False, fontname = "sfns", fontsize = 12, spacing=1.15, padding=5, onUpdate=None):
        super().__init__(rect, onUpdate)
        self.textcolor = textcolor
        self.bgcolor = bgcolor
        self.bordercolor = bordercolor
        self.allownewlines = allownewlines
        self.infocus = False
        self.font = getFont(fontname, fontsize)
        self.padding = padding
        self.spacing = spacing

        self.defaulttext = defaulttext
        self.text = defaulttext
        self.textoffset = [0,0]

        self.cursor = 0
        self.rcp = self.getrelativecursorpos()
    
    def draw(self, surface):
        # bg color and box
        pygame.draw.rect(
            surface,
            self.bgcolor,
            self.rect
        )
        pygame.draw.rect(
            surface,
            self.bordercolor,
            self.rect,
            width=1
        )

        # text and cursor
        textsurface = multilineFontRender(self.font, self.text, True, self.textcolor, None, self.spacing)
        constrainedtextsurface = pygame.surface.Surface((self.rect[2]-self.padding, self.rect[3]-self.padding), pygame.SRCALPHA)
        constrainedtextsurface.blit(textsurface, self.textoffset)

        if self.infocus:
            cursorcoords = [self.textoffset[0] + self.rcp[0], self.textoffset[1] + self.rcp[1]]
            pygame.draw.rect(
                constrainedtextsurface,
                self.textcolor,
                [
                    cursorcoords[0],
                    cursorcoords[1],
                    1,                  # I might make cursor width a parameter
                    self.rcp[2]
                ]
            )

        surface.blit(constrainedtextsurface, (self.rect[0]+self.padding//2, self.rect[1]+self.padding//2))



    # returns three values, xpos, ypos and height
    # getrelativecursorpos + textoffset should always be in the box
    def getrelativecursorpos(self, cursor=None):
        if cursor is None:
            cursor = self.cursor
        
        subtext = self.text[0:cursor]
        splittext = subtext.split("\n")
        yoffset = 0
        for line in splittext[:-1]:
            yoffset += self.font.size(line)[1]*self.spacing

        xoffset = self.font.size(splittext[-1])[0]
        height = self.font.size(splittext[-1])[1]

        return (xoffset, yoffset, height)
        

    def handleEvent(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if inRect(event.pos, self.rect):
                if event.button == 1:
                    self.infocus = True
            else:
                self.infocus = False
        elif event.type == pygame.KEYDOWN:
            if self.infocus:
                # TODO: add command and option to backspace and arrow keys
                # print(event)
                if event.key == pygame.K_ESCAPE:
                    self.infocus = False
                elif event.key == pygame.K_BACKSPACE:
                    if self.cursor > 0:
                        nextcursor = 0 
                        if event.mod & 1024 or event.mod & 2048: # command
                            for i in range(self.cursor-1, -1, -1):
                                if self.text[i] == "\n":
                                    nextcursor = i
                                    break
                        elif event.mod & 256 or event.mod & 512: # option
                            for i in range(self.cursor-2, -1, -1):
                                if self.text[i] == "\n" or self.text[i] == " ":
                                    nextcursor = i
                                    break
                        else:
                            nextcursor = self.cursor - 1
                        self.text = self.text[:nextcursor] + self.text[self.cursor:]
                        self.cursor = nextcursor
                        self.rcp = self.getrelativecursorpos()
                elif event.key == pygame.K_RIGHT:
                    if self.cursor < len(self.text):
                        if event.mod & 1024 or event.mod & 2048: # command
                            nextcursor = len(self.text)
                            for i in range(self.cursor, len(self.text)):
                                if self.text[i] == "\n":
                                    nextcursor = i
                                    break
                            self.cursor = nextcursor
                        elif event.mod & 256 or event.mod & 512: # option
                            nextcursor = len(self.text)
                            for i in range(self.cursor+1, len(self.text)):
                                if self.text[i] == "\n" or self.text[i] == " ":
                                    nextcursor = i
                                    break
                            self.cursor = nextcursor
                        else:
                            self.cursor += 1
                        self.rcp = self.getrelativecursorpos()
                elif event.key == pygame.K_LEFT:
                    if self.cursor > 0:
                        if event.mod & 1024 or event.mod & 2048: # command
                            nextcursor = 0
                            for i in range(self.cursor-1, -1, -1):
                                if self.text[i] == "\n":
                                    nextcursor = i+1
                                    break
                            self.cursor = nextcursor
                        elif event.mod & 256 or event.mod & 512: # option
                            nextcursor = 0
                            for i in range(self.cursor-2, -1, -1):
                                if self.text[i] == "\n" or self.text[i] == " ":
                                    nextcursor = i+1
                                    break
                            self.cursor = nextcursor
                        else:
                            self.cursor -= 1
                        self.rcp = self.getrelativecursorpos()
                elif event.key == pygame.K_RETURN:
                    self.text = self.text[:self.cursor] + "\n" + self.text[self.cursor:]
                    self.cursor += 1
                    self.rcp = self.getrelativecursorpos()
                elif event.key in [pygame.K_UP, pygame.K_DOWN]:
                    pass
                else:
                    self.text = self.text[:self.cursor] + event.unicode + self.text[self.cursor:]
                    self.cursor += len(event.unicode)
                    self.rcp = self.getrelativecursorpos()
                
                # horizontal textoffset
                if self.textoffset[0] + self.rcp[0] < 0:
                    self.textoffset[0] = -self.rcp[0]
                elif self.textoffset[0] + self.rcp[0] >= self.rect[2]-self.padding:
                    self.textoffset[0] = self.rect[2]-self.padding-self.rcp[0]-1
                # vertical offset
                if self.textoffset[1] + self.rcp[1] < 0:
                    self.textoffset[1] = -self.rcp[1]
                elif self.textoffset[1] + self.rcp[1] + self.rcp[2] >= self.rect[3]-self.padding:
                    self.textoffset[1] = self.rect[3]-self.padding-self.rcp[1]-self.rcp[2]
                
                if self.onUpdate is not None:
                    self.onUpdate(self.getState())
                    
    
    def getState(self):
        return self.text
    
    def reset(self):
        self.text = self.defaulttext
        self.cursor = 0
        self.textoffset = [0,0]

        self.cursor = 0
        self.rcp = self.getrelativecursorpos()

#############
## Globals ##
#############

all_objects = UIObjectGroup()