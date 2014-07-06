import Components
import libtcodpy as tcod

import Graphics.MapRenderer
import Funcs

menuHeight = 15

def CreatePanel( x, y, w, h, cb ):
    x = int( x )
    y = int( y )
    w = int( w )
    h = int( h )

    def render( panel ):
        cb( panel )
        tcod.console_blit( panel, 0, 0, w, h, 0, x, y )

    panel = tcod.console_new( w, h )
    return ( render, panel )


class Renderer():
    def __init__( self, world, renderWidth, renderHeight ):
        self.world = world

        self._map = None
        self.renderTarget = None

        self.renderWidth = renderWidth
        self.renderHeight = renderHeight

        self.rW = renderWidth
        self.rH = renderHeight - menuHeight

        self.hRW = self.rW / 2
        self.hRH = self.rH / 2

        self.cameraX = 0
        self.cameraY = 0

        self.uiRenderTarget = tcod.console_new( renderWidth, menuHeight )
        self.panels = []

        self.panels.append( ( self.renderUI, self.uiRenderTarget ) )

    def setMap( self, _map ):
        self._map = _map

        self.renderTarget = Graphics.MapRenderer.Render( self._map, self.renderTarget )

    def setCamera( self, x, y ):
        self.cameraX = int( x )
        self.cameraY = int( y )
    def moveCamera( self, x, y ):
        self.cameraX += int( x )
        self.cameraY += int( y )

    def renderMap( self ):
        if self.renderTarget is not None:
            tcod.console_blit( self.renderTarget,
                    int(self.cameraX-self.hRW), #X
                    int(self.cameraY-self.hRH), #Y
                    self.rW,
                    self.rH,
                    0, #Target map
                    0,0) #Target XY

    def renderUI( self, panel ):
        tcod.console_clear( panel )

        tcod.console_set_default_background( panel, tcod.Color( 210, 125, 44 ) )
        tcod.console_rect( panel, 0, 0, self.rW, menuHeight, True, tcod.BKGND_SET )

        tcod.console_set_default_background( panel, tcod.Color( 132,126,135 ) )
        tcod.console_rect( panel, 1, 1, self.rW - 2, menuHeight - 2, True, tcod.BKGND_SET )

        while len( Funcs.messageLines ) > 11:
            Funcs.messageLines.pop( 0 )

        for i in range( len( Funcs.messageLines ) ):
            tcod.console_print_ex( panel, 5, i + 2, tcod.BKGND_NONE, tcod.LEFT, Funcs.messageLines[ i ] )

        tcod.console_blit( panel,
                    0, #X
                    0, #Y
                    self.rW,
                    menuHeight,
                    0, #Target map
                    0,self.rH) #Target XY


    def render( self ):
        tcod.console_clear( 0 )
        self.renderMap()

        for ent in self.world.getEntityByComponent( Components.Renderable, Components.Position ):
            ent.getComponent(Components.Renderable).draw( self.cameraX - self.hRW, self.cameraY - self.hRH )

        for panel in self.panels:
            panel[0]( panel[1] )

        tcod.console_flush()
