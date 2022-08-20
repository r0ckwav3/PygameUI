import pygame

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
    def __init__(self, rect, color, onUpdate):
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
    
    # moves the uiobject to a new location
    # newrect: int[4]
    def move(self, newrect):
        self.rect = newrect

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

class Button(UIObject):
    ...

class Slider(UIObject):
    ...

class Button(UIObject):
    ...

#############
## Globals ##
#############
all_objects = UIObjectGroup()

###############
## Functions ##
###############