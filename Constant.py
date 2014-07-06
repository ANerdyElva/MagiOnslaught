from libtcodpy import Color

BLOCKED = 1
TRANSPARENT = 2

WaterOrb = 0
FireOrb = 1
EarthOrb = 2
AirOrb = 3
SteamOrb = 4
LightningOrb = 5

RotateDist = 7

spawnableOrbs = {
        1: WaterOrb,
        2: FireOrb,
        3: EarthOrb,
        4: AirOrb,
        }
orbNames = {
        WaterOrb: "Water",
        FireOrb: "Fire",
        EarthOrb: 'Earth',
        AirOrb: 'Air',
        SteamOrb: 'Steam',
        LightningOrb: 'Lightning',
        }
orbColors = {
        WaterOrb: ( Color( 0, 0, 255 ), chr( 7 ) ),
        FireOrb: ( Color( 255, 0, 0 ), chr( 15 ) ),
        EarthOrb: ( Color( 142, 63, 26), chr( 7 ) ),
        AirOrb: ( Color( 150, 150, 200 ), chr( 15 ) ),
        SteamOrb: ( Color( 200, 200, 200 ), chr( 15 ) ),
        LightningOrb: ( Color( 145,30,139 ), chr( 0x2A ) ),
        }

orbDamage = {
        WaterOrb: 2,
        EarthOrb: 7,
        FireOrb: 4,
        AirOrb: 3,
        SteamOrb: 5,
        LightningOrb: 6,
        }
EnemyCollisionId = -1
StopCollisionId = -2 #For when the velocity of an orb is close to 0
WallCollisionId = -3 #For collision with a wall
