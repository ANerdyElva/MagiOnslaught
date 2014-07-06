MagiOnslaught
=============

Creator: Kevin van der Velden

Platform: Python 3 and libTCOD

Based on game: Magicka from Paradox Interactive

Hey people, my first game I made for a game jam! :D

I liked the mechanic in Magicka where you could combine elements to create different spells, but I thought it could be improved a bit. You press the buttons 1 through 4 to create an orb (Water, Fire, Earth, Air). You launch these orbs by clicking where you want them to go.

If they collide with an enemy, the enemy get's hurt. If they collide with you... so do you! But if they collide with a different orb there's a reaction, Fire and Air hitting each other creates Lightning orbs, Lightning and Earth hitting each other... destroys both of the orbs.

This is a turn based game, think about where to send your orbs and where to step to avoid getting hit, it gets hectic quite fast.

The objective of the game is to... survive, your orbs aren't peculiar about who they hurt and your HP is limited, try to get a high score! - I can't really get over 200.

A gif of me playing the game

There's plenty more orb options to build in, and a lot of tidying up, which I might get to sometime after the jam, but for now I think it's done.

The py2exe windows version is available via Dropbox: https://dl.dropboxusercontent.com/u/1193507/MagiOnslaught.zip

I've put the code on github and if anyone wants to help they're welcome: https://github.com/KevinVDVelden/MagiOnslaught

The version on github uses cygwin and has version 1.5.2 of libtcod, the py2exe version uses the MSVC build of libtcod which is version 1.5.1. The github version should work on linux if you install libtcod.

