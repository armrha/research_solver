# research_solver

A simple dumb script to save me time when having to do R&D in SS13.

Just simply reads over the relevant directories, searches through them to find req_tech / origin_tech, outputs text like this to show you a build order.

Output looks like this:
```
With no mat restrictions (all mats)
circuit board (portable generator)
circuit board (advanced portable generator)
circuit board (super portable generator)
exosuit module circuit board (ballistic weapon systems)
large power transmission circuit
phoron bolt modulator
metabolic siphon
decloner modulator
phoron loading KA cell
phoron core KA power converter
combat hardsuit control module assembly
bluespace inhaler cartridge
subspace transmitter
photonic processor
combat hardsuit control and targeting board
bag of holding
combat hardsuit control and targeting board
With default mats... (steel / glass)
circuit board (portable generator)
circuit board (advanced portable generator)
circuit board (super portable generator)
exosuit module circuit board (ballistic weapon systems)
large power transmission circuit
metabolic siphon
circuit board (radioisotope thermoelectric generator)
photonic processor
ai shell control module
combat hardsuit central circuit board
pico-manipulator
standard exosuit remote upgrade
weapon firing mechanism
combat hardsuit control and targeting board
combat hardsuit control and targeting board
{'TECH_MATERIAL': [6, 4375], 'TECH_ENGINEERING': [7, 21625], 'TECH_MAGNET': [6, 3125], 'TECH_PHORON': [4, 125], 'TECH_POWER': [7, 20250], 'TECH_BIO': [6, 3125], 'TECH_BLUESPACE': [4, 125], 'TECH_COMBAT': [7, 32000], 'TECH_DATA': [8, 256175], 'TECH_ARCANE': [0, 0], 'TECH_ILLEGAL': [0, 0]}
```

You can adjust the prohibited techs or do whatever. Or make my fitness function actually good, it's not amazing right now but it works roughly
