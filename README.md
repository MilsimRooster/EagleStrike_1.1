# READ ME: Created on 2/23/2025 : for info contact info@milsimrooster.com

**DEV NOTE: This is an unstable Beta. I am currently working on Kill Streaks and High Scores, the ability to save them so they are persistent with each game run.  PS5 controller support is working, R2 fires, Share button pauses the game, Square button will quit the game, X button starts the game. The craft moves freely, the weapon pivots, currently, the weapon points one direction while the craft pivots into the opposite direction, I've been trying to work this out, however, pygame converts the degrees and it get's a little tricky, currently this is the best state. Another bug notices is with the bosses, they will stick to your craft and eat every life until game over if you allow them to get too close, Triangle button is supposed to knock them back, sometimes that will completely kill the boss leaving you stuck on the boss level since his death is what triggers the advancement to the next level.  GODSPEED!

# Eagle Strike README

## Overview
*Eagle Strike* is an action-packed, retro-inspired arcade shooter game developed using Python and Pygame. Players control the Eagle Strike dropship, navigating through increasingly challenging levels filled with alien enemies, including Terminids, Automatons, Illuminates, and Hunters, to rescue divers while collecting power-ups. The game supports both keyboard and PS5 controller inputs, offering a nostalgic arcade experience with vibrant visuals and immersive audio.

## Features
- **Dynamic Gameplay**: Battle waves of aliens across 20 unique planetary levels, facing bosses every fifth level. Progress by reaching score thresholds, with dual blasts (larger dropship) unlocking at Level 10.
- **Power-Ups**: Collect 13 power-ups, including Rate of Fire, Reinforce, Diver Pods, Resupply, Hellbomb, MG-94, EAT-17, Shield, Trishot, Quadshot, Burst, Eagle Sweat, and Battle Buddy, to enhance your ship’s abilities.
- **Stunning Backgrounds**: Features 100 twinkling stars for Level 1 and detailed planetary surfaces for Levels 2+ with forests, rivers, earth patches, bases (circles, rectangles, diamonds), and large meteors (20px, 1% chance per frame, 25 damage) for a retro arcade vibe.
- **Controls**:
  - **Keyboard**: Left/Right/Up/Down to move, Space to shoot, P to pause, B for Break-Free (push bosses without damage).
  - **PS5 Controller**: Left Stick to move, Right Stick to rotate, R2 to shoot, Options to pause, Triangle for Break-Free, Share to reset, Square to quit.
- **UI and Scoring**: Track points, high score, divers rescued (lives), level, and player health (200 HP max, no regeneration) on-screen. Save/load high scores to files.
- **Audio**: Immersive soundtrack and sound effects for shooting, hits, explosions, and power-ups, with a master volume slider in the pause menu.
- **Multi-Level Progression**: Start at any level (1–20) from the title screen, advancing through levels with increasing difficulty.

## Requirements
- Python 3.x
- Pygame library (`pip install pygame`)
- PS5 controller (optional, for enhanced control)
- Game assets (images, sounds, music) in the script directory:
  - Sprite files (`dropship*.png`, `terminid*.png`, `automaton*.png`, `illuminate*.png`, `hunter*.png`, `boss*.png`, `power_up*.png`, `start_screen.png`, `battle_buddy.png`, `intro*.png`)
  - Sound files (`shoot.wav`, `boom.wav`, `hit.wav`, `ship_hit.wav`, `thrust.wav`, `level_up.wav`, `boss_intro.wav`, `eagle_sweat_trigger.wav`, `battle_buddy.wav`, `power_up*.wav`, `intro_music.wav`, `background_music*.wav`)

## Installation
1. Clone or download this repository.
2. Ensure Python and Pygame are installed on your system.
3. Place all asset files in the same directory as `eagle_strike_new.py`.
4. Run the game with: `python eagle_strike_new.py`
5. For the exe version, right click and view properties, check the box to unblock, then double click the exe, the game will the execute.

## Gameplay
- Start the game from the title screen, selecting a starting level (1–20) using Up/Down (keyboard) or Left Stick (controller).
- Navigate the dropship to avoid enemies and their shots while shooting to destroy aliens and collect power-ups.
- Survive by managing health (200 HP, damaged by aliens/meteors) and divers (lives, lost on death but retain level progress).
- Use Break-Free (B/Triangle) to push bosses without killing, advancing levels.
- Pause with P/Options, reset with R/Share, or quit with Q/Square. Adjust volume and save/load scores in the pause menu.
- Share your final score on X.com from the game-over screen.

## Development
- **Coded by**: Grok
- **Creative Director**: MilsimRooster
- **Music by**: Colm R McGuinness, Jonathan Young, Boris Harizanov

## Known Issues
- Ensure all asset files are present to avoid fallback visuals/sounds.
- PS5 controller detection may fail if not properly connected—fall back to keyboard controls.
- Check `eagle_strike_log.txt` for runtime errors or performance issues.

## License
*Eagle Strike* is provided under a permissive license for personal and educational use. Assets are assumed to be royalty-free or user-provided—contact the creative director for commercial use permissions.
