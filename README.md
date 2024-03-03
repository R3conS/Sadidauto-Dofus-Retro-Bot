![GitHub last commit](https://img.shields.io/github/last-commit/ephell/Sadidauto-Dofus-Retro-Bot)

<p align="center">
    <img src="https://i.imgur.com/WWzi4PF.png" alt="Sadidauto-Banner">
</p>

# 🤖 Sadidauto - What is it?
Sadidauto is a bot tailored for the Sadida class in Dofus Retro. It is specifically designed to capitalize on the Sadida's monster farming prowess when using a **damage set** as well as the **Earthquake + Poisoned Wind + Sylvan Power** spell combination. Sadidauto employs various visual detection techniques to determine its actions and uses the mouse and keyboard to interact with the official game client just like a genuine player would. The client doesn't get modified in any way.

## Key features
- Find and kill monsters.
- Bank collected loot.
- Recover HP.
- Decline any invites or offers from other players.
- Activate fight lock.
- Disable spectator mode.
- Utilize Recall potions.
- Reconnect to the game in case of a disconnect.
- Simple UI.
- Detailed logs.

## Supported farming area and basic logic loop
Sadidauto is currently capable of farming the **Astrub Forest** area which encompasses 13 farmable maps. Once a map is cleared it continues on to the next, navigating the forest in a continuous circular pattern (clockwise or counterclockwise) until the pods limit is reached. Upon reaching this threshold, Sadidauto heads to the bank (utilizing a Recall potion if available) to deposit all gathered resources and items. Once banking is complete - Sadidauto returns to hunting. Visual representations of the hunting paths:

Clockwise             |  Counterclockwise
:-------------------------:|:-------------------------:
![Clockwise](https://i.imgur.com/2IHYxCG.png)  |  ![Counterclockwise](https://i.imgur.com/nWCkfOY.png)

## Demo
[![Demo-Video](https://i.imgur.com/MNq2RTO.jpeg)](https://www.youtube.com/watch?v=kXMIF0KDwcs "Demo-Video")

## Limitations
- Only for Windows. Tested on Windows 10 and 11.
- Given that Sadidauto employs the mouse and keyboard to interact with the game, it's impossible to use your computer for other tasks simultaneously unless Sadidauto operates within a Virtual Machine.
- A minimum of 4GB RAM and a 2-core CPU is recommended to smoothly run the game alongside Sadidauto.
- May experience frequent crashes when playing Dofus on a laggy and unstable internet connection (>300 ping).

## Logic flow
Sadidauto is governed by a central controller, overseeing two primary states: **In Combat** and **Out of Combat**. These states, in turn, are managed by dedicated controllers, each handling specific sub-states: **Preparing**, **Fighting** and **Hunting**, **Banking** respectively. In the event of a recoverable exception a designated recovery procedure is initiated. If the recovery succeeds, control is returned to the main controller; otherwise, Sadidauto exits. A visual representation of this logic flow is provided below:
<p align="center">
    <img src="https://i.imgur.com/9UjOpfB.png" alt="Sadidauto-Flowchart">
</p>

## Installation & Usage
See the [Wiki](https://github.com/ephell/Sadidauto-Dofus-Retro-Bot/wiki).

## License
[MIT](LICENSE)