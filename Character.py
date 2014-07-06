_ = lambda arg, _def: karg[arg] if arg in karg else _def

class Character():
    def __init__( self, name, parent = None, **kargs ):
        if parent is not None:
            self.data = dict( parent.data )
            for n in kargs:
                self.data[ n ] = kargs[ n ]
        else:
            self.data = dict( kargs )

        self.name = name
        self.parent = parent

    def __str__( self ):
        return '[Character %s]' % ( [ str( self.data[n] ) for n in self.data ] )

    def __getattr__( self, key ):
        if key not in self.data:
            return None
        return self.data[ key ]


BaseStats = Character('Base', None,
    BaseHP = 10,

    MoveSpeed = 1.0,
    AttackSpeed = 1.0,

    AttackDamage = 1,
    TurnRandomRange = 0,
    )
