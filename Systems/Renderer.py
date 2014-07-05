import Components
import libtcodpy as tcod

import Graphics.MapRenderer

class Renderer():
    def __init__( self, world, renderWidth, renderHeight ):
        self.world = world

        self._map = None
        self.renderTarget = None

        self.rW = renderWidth
        self.rH = renderHeight

        self.hRW = self.rW / 2
        self.hRH = self.rH / 2

        self.cameraX = 0
        self.cameraY = 0

    def setMap( self, _map ):
        self._map = _map

        self.renderTarget = Graphics.MapRenderer.Render( self._map, self.renderTarget )

    def setCamera( self, x, y ):
        self.cameraX = x
        self.cameraY = y
    def moveCamera( self, x, y ):
        self.cameraX += x
        self.cameraY += y

    def renderMap( self ):
        if self.renderTarget is not None:
            tcod.console_blit( self.renderTarget,
                    int(self.cameraX-self.hRW),
                    int(self.cameraY-self.hRH),
                    self.rW,
                    self.rH,
                    0, #Target map
                    0,0) #Target XY


    def render( self ):
        tcod.console_clear( 0 )
        self.renderMap()

        for ent in self.world.getEntityByComponent( Components.Renderable, Components.Position ):
            ent.getComponent(Components.Renderable).draw( self.cameraX - self.hRW, self.cameraY - self.hRH )
        tcod.console_flush()

