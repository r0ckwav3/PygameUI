from tkinter import font
import pygame

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

def drawRoundedRect(surface, color, rect, rad=None):
    if rad is None:
        rad = min(rect[2], rect[3])//3

    pygame.draw.rect(surface, color,
                     [rect[0]+rad, rect[1], rect[2]-(rad*2), rect[3]])
    pygame.draw.rect(surface, color,
                     [rect[0], rect[1]+rad, rect[2], rect[3]-(rad*2)])

    circlecenters = [(rect[0]+rad, rect[1]+rad),
                     (rect[0]+rect[2]-(rad+1), rect[1]+rad),
                     (rect[0]+rad, rect[1]+rect[3]-(rad+1)),
                     (rect[0]+rect[2]-(rad+1), rect[1]+rect[3]-(rad+1))]

    for cc in circlecenters:
        pygame.gfxdraw.aacircle(surface, cc[0], cc[1], rad, color)
        pygame.gfxdraw.filled_circle(surface, cc[0], cc[1], rad, color)

#############
## Classes ##
#############

# base ui object
# if used, draws a solid rectangle
class UIObject:
    # initialization see handleEvent for use of onUpdate
    # rect: int[4]
    # color: int[3] or pygame.color
    # onUpdate: function
    def __init__(self, rect, color, onUpdate = None):
        self.rect = rect
        self.color = color
        self.onUpdate = onUpdate
        all_objects.addObject(self)
        
    
    # draws the object onto the given surface and returns that surface
    # surface: pygame.Surface
    # -> pygame.Surface
    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
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
# also note that the width and height of the rect will be ignored
class Textbox(UIObject):
    def __init__(self, rect, color, text = "", fontname = None, fontsize = None, bgcolor = None, onUpdate = None):
        super().__init__(rect,color,onUpdate)
        self.text = text
        self.bgcolor = bgcolor

        if fontname is None:
            fontname = "sfns"
        if fontsize is None:
            fontsize = 12
        self.font = getFont(fontname, fontsize)

    def draw(self, surface):
        textsurface = self.font.render(self.text, True, self.color, self.bgcolor)
        surface.blit(textsurface, self.rect)

class Button(UIObject):
    ...

class Slider(UIObject):
    ...

class Toggle(UIObject):
    ...

#############
## Globals ##
#############

all_objects = UIObjectGroup()