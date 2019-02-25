import kivy

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.properties import NumericProperty
from kivy.clock import Clock
from kivy.graphics import Rectangle
from random import randint
from kivy.config import Config

Config.set('graphics', 'resizable', 0)
Window.clearcolor = (0, 0, 0, 1.)


class WidgetDrawer(Widget):

    def __init__(self, imageStr, **kwargs):
        super(WidgetDrawer, self).__init__(**kwargs)
        with self.canvas:
            self.size = (Window.width * .002 * 25, Window.width * .002 * 25)
            self.rect_bg = Rectangle(source=imageStr, pos=self.pos, size=self.size)
            self.bind(pos=self.update_graphics_pos)
            self.x = self.center_x
            self.y = self.center_y
            self.pos = (self.x, self.y)
            self.rect_bg.pos = self.pos

    def update_graphics_pos(self, instance, value):
        self.rect_bg.pos = value

    def setSize(self, width, height):
        self.size = (width, height)

    def setPos(xpos, ypos):
        self.x = xpos
        self.y = ypos


class Asteroid(WidgetDrawer):
    # Asteroid class. The flappy ship will dodge these
    velocity_x = NumericProperty(0)  # initialize velocity_x and velocity_y
    velocity_y = NumericProperty(0)  # declaring variables is not necessary in python

    # update the position using the velocity defined here. every time move is called we change the position by velocity_x
    def move(self):
        self.x = self.x + self.velocity_x
        self.y = self.y + self.velocity_y

    def update(self):
        # the update function moves the astreoid. Other things could happen here as well (speed changes for example)
        self.move()


class Ship(WidgetDrawer):
    # Ship class. This is for the main ship object.
    # velocity of ship on x/y axis
    impulse = 3
    grav = -0.1

    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)

    def move(self):
        self.x = self.x + self.velocity_x
        self.y = self.y + self.velocity_y
        # don't let the ship go too far
        if self.y == Window.height * 0.95:  # don't let the ship go up too high
            self.impulse = -3

    def determineVelocity(self):
        self.grav = self.grav * 1.05
        if self.grav < -4:
            self.grav = -4
        self.velocity_y = self.impulse + self.grav
        self.impulse = 0.95 * self.impulse

    def update(self):
        self.determineVelocity()
        self.move()


class MyButton(Button):
    # class used to get uniform button styles
    def __init__(self, **kwargs):
        super(MyButton, self).__init__(**kwargs)
        # setting the font size
        self.font_size = Window.width * 0.018


class GUI(Widget):
    # this is the main widget that contains the game.
    asteroidList = []  # use this to keep track of asteroids
    minProb = 1700  # this variable used in spawning asteroids

    def __init__(self, **kwargs):
        super(GUI, self).__init__(**kwargs)
        l = Label(text='Flappy Ship')  # give the game a title
        l.x = Window.width / 2 - l.width / 2
        l.y = Window.height * 0.8
        self.add_widget(l)  # add the label to the screen

        # now we create a ship object
        # notice how we specify the ship image
        self.ship = Ship(imageStr='./ship.png')
        self.ship.x = Window.width / 4
        self.ship.y = Window.height / 2
        self.add_widget(self.ship)

    def addAsteroid(self):
        # add an asteroid to the screen
        # self.asteroid
        imageNumber = randint(1, 4)
        imageStr = './sandstone_' + str(imageNumber) + '.png'
        tmpAsteroid = Asteroid(imageStr)
        tmpAsteroid.x = Window.width * 0.99

        # randomize y position
        ypos = randint(1, 16)

        ypos = ypos * Window.height * .0625

        tmpAsteroid.y = ypos
        tmpAsteroid.velocity_y = 0
        vel = 10
        tmpAsteroid.velocity_x = -0.1 * vel

        self.asteroidList.append(tmpAsteroid)
        self.add_widget(tmpAsteroid)

    # handle input events
    # kivy has a great event handler. the on_touch_down function is already recognized
    # and doesn't need t obe setup. Every time the screen is touched, the on_touch_down function is called
    def on_touch_down(self, touch):
        self.ship.impulse = 3  # give the ship an impulse
        self.ship.grav = -0.1  # reset the gravitational velocity

    def gameOver(self):  # this function is called when the game ends
        # add a restart button
        restartButton = MyButton(text='Restart')

        # restartButton.background_color = (.5,.5,1,.2)
        def restart_button(obj):
            # this function will be called whenever the reset button is pushed
            print('restart button pushed')
            # reset game
            for k in self.asteroidList:
                self.remove_widget(k)

                self.ship.xpos = Window.width * 0.25
                self.ship.ypos = Window.height * 0.5
                self.minProb = 1700
            self.asteroidList = []

            self.parent.remove_widget(restartButton)
            # stop the game clock in case it hasn't already been stopped
            Clock.unschedule(self.update)
            # start the game clock
            Clock.schedule_interval(self.update, 1.0 / 60.0)

        restartButton.size = (Window.width * .3, Window.width * .1)
        restartButton.pos = (Window.width * 0.5 - restartButton.width / 2, Window.height * 0.5)
        # bind the button using the built-in on_release event
        # whenever the button is released, the restart_button function is called
        restartButton.bind(on_release=restart_button)

        # *** It's important that the parent get the button so you can click on it
        # otherwise you can't click through the main game's canvas
        self.parent.add_widget(restartButton)

    def update(self, dt):
        # This update function is the main update function for the game
        # All of the game logic has its origin here
        # events are setup here as well
        # update game objects
        # update ship
        self.ship.update()
        # update asteroids
        # randomly add an asteroid
        tmpCount = randint(1, 1800)
        if tmpCount > self.minProb:
            self.addAsteroid()
            if self.minProb < 1300:
                self.minProb = 1300
            self.minProb = self.minProb - 1

        for k in self.asteroidList:
            # check for collision with ship
            if k.collide_widget(self.ship):
                print('death')
                # game over routine
                self.gameOver()
                Clock.unschedule(self.update)
                # add reset button
            k.update()


class ClientApp(App):

    def build(self):
        # this is where the root widget goes
        # should be a canvas
        parent = Widget()  # this is an empty holder for buttons, etc

        app = GUI()
        # Start the game clock (runs update function once every (1/60) seconds
        Clock.scheimport kivy


from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.properties import NumericProperty
from kivy.clock import Clock
from kivy.graphics import Rectangle
from random import randint
from kivy.config import Config

Config.set('graphics','resizable',0)
Window.clearcolor = (0,0,0,1.)

class WidgetDrawer(Widget):

    def __init__(self, imageStr, **kwargs):
        super(WidgetDrawer, self).__init__(**kwargs)
        with self.canvas:
            self.size = (Window.width*.002*25,Window.width*.002*25)
            self.rect_bg=Rectangle(source=imageStr,pos=self.pos,size = self.size)
            self.bind(pos=self.update_graphics_pos)
            self.x = self.center_x
            self.y = self.center_y
            self.pos = (self.x,self.y)
            self.rect_bg.pos = self.pos

    def update_graphics_pos(self, instance, value):
        self.rect_bg.pos = value
    def setSize(self,width, height):
        self.size = (width, height)
    def setPos(xpos,ypos):
        self.x = xpos
        self.y = ypos

class Asteroid(WidgetDrawer):
    #Asteroid class. The flappy ship will dodge these
    velocity_x = NumericProperty(0) #initialize velocity_x and velocity_y
    velocity_y = NumericProperty(0) #declaring variables is not necessary in python
 #update the position using the velocity defined here. every time move is called we change the position by velocity_x
    def move(self):
        self.x = self.x + self.velocity_x
        self.y = self.y + self.velocity_y
    def update(self):
#the update function moves the astreoid. Other things could happen here as well (speed changes for example)
        self.move()

class Ship(WidgetDrawer):
    #Ship class. This is for the main ship object.
    #velocity of ship on x/y axis
    impulse = 3
    grav = -0.1

    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)

    def move(self):
        self.x = self.x + self.velocity_x
        self.y = self.y + self.velocity_y
        #don't let the ship go too far
        if self.y == Window.height*0.95: #don't let the ship go up too high
            self.impulse = -3

    def determineVelocity(self):
        self.grav = self.grav*1.05
        if self.grav < -4:
           self.grav = -4
        self.velocity_y = self.impulse + self.grav
        self.impulse = 0.95*self.impulse

    def update(self):
        self.determineVelocity()
        self.move()

class MyButton(Button):
    #class used to get uniform button styles
    def __init__(self, **kwargs):
        super(MyButton, self).__init__(**kwargs)
    #setting the font size
        self.font_size = Window.width*0.018

class GUI(Widget):
    #this is the main widget that contains the game.
    asteroidList =[] #use this to keep track of asteroids
    minProb = 1700 #this variable used in spawning asteroids
    def __init__(self, **kwargs):
        super(GUI, self).__init__(**kwargs)
        l = Label(text='Flappy Ship') #give the game a title
        l.x = Window.width/2 - l.width/2
        l.y = Window.height*0.8
        self.add_widget(l) #add the label to the screen

        #now we create a ship object
 #notice how we specify the ship image
        self.ship = Ship(imageStr = './ship.png')
        self.ship.x = Window.width/4
        self.ship.y = Window.height/2
        self.add_widget(self.ship)

    def addAsteroid(self):
        #add an asteroid to the screen
        #self.asteroid
        imageNumber = randint(1,4)
        imageStr = './sandstone_'+str(imageNumber)+'.png'
        tmpAsteroid = Asteroid(imageStr)
        tmpAsteroid.x = Window.width*0.99

        #randomize y position
        ypos = randint(1,16)

        ypos = ypos*Window.height*.0625

        tmpAsteroid.y = ypos
        tmpAsteroid.velocity_y = 0
        vel = 10
        tmpAsteroid.velocity_x = -0.1*vel

        self.asteroidList.append(tmpAsteroid)
        self.add_widget(tmpAsteroid)

    #handle input events
    #kivy has a great event handler. the on_touch_down function is already recognized
    #and doesn't need t obe setup. Every time the screen is touched, the on_touch_down function is called
    def on_touch_down(self, touch):
        self.ship.impulse = 3 #give the ship an impulse
        self.ship.grav = -0.1 #reset the gravitational velocity

    def gameOver(self): #this function is called when the game ends
        #add a restart button
        restartButton = MyButton(text='Restart')

        #restartButton.background_color = (.5,.5,1,.2)
        def restart_button(obj):
        #this function will be called whenever the reset button is pushed
            print ('restart button pushed')
            #reset game
            for k in self.asteroidList:
                self.remove_widget(k)

                self.ship.xpos = Window.width*0.25
                self.ship.ypos = Window.height*0.5
                self.minProb = 1700
            self.asteroidList = []

            self.parent.remove_widget(restartButton)
 #stop the game clock in case it hasn't already been stopped
            Clock.unschedule(self.update)
 #start the game clock
            Clock.schedule_interval(self.update, 1.0/60.0)
        restartButton.size = (Window.width*.3,Window.width*.1)
        restartButton.pos = (Window.width*0.5-restartButton.width/2, Window.height*0.5)
        #bind the button using the built-in on_release event
        #whenever the button is released, the restart_button function is called
        restartButton.bind(on_release=restart_button)

        #*** It's important that the parent get the button so you can click on it
        #otherwise you can't click through the main game's canvas
        self.parent.add_widget(restartButton)

    def update(self,dt):
                #This update function is the main update function for the game
                #All of the game logic has its origin here
                #events are setup here as well
        #update game objects
        #update ship
        self.ship.update()
        #update asteroids
        #randomly add an asteroid
        tmpCount = randint(1,1800)
        if tmpCount > self.minProb:
            self.addAsteroid()
            if self.minProb < 1300:
                self.minProb = 1300
            self.minProb = self.minProb -1

        for k in self.asteroidList:
            #check for collision with ship
            if k.collide_widget(self.ship):
                print ('death')
                #game over routine
                self.gameOver()
                Clock.unschedule(self.update)
                #add reset button
            k.update()

class ClientApp(App):

    def build(self):
        #this is where the root widget goes
        #should be a canvas
        parent = Widget() #this is an empty holder for buttons, etc

        app = GUI()
        #Start the game clock (runs update function once every (1/60) seconds
        Clock.schedule_interval(app.update, 1.0/60.0)
        parent.add_widget(app) #use this hierarchy to make it easy to deal w/buttons
        return parent
if __name__ == '__main__' :
    ClientApp().run()











dule_interval(app.update, 1.0 / 60.0)
        parent.add_widget(app)  # use this hierarchy to make it easy to deal w/buttons
        return parent


if __name__ == '__main__':
    ClientApp().run()











