DO NOT USE THIS CODE! 
I made it as a quick and dirty proof of concept that I was able to implement the core set of functionnalities for an online game in a couple of days. But the code is unsecure and very inefficient. Actually it allows for remote code execution on the server. Do not run it through internet! On the plus side it will also limit the attacker's possibilities as it eats all the CPU cycles it can get its hands on (for no particularily good reason)

MudExcuse
=========
Every old family has a skeleton in a closet. Every programmer has an abandonned MORPG in his archives. It is hard to admit but I have several. This one is a simple one but it does have a complete small set of functionalities. For several bad reasons, some things, even inside the source, are written in French. I hate people who do that, I'll try to translate most of it. 

Basic idea
==========
It is more of a graphical MUD where you pickup objects, walk around rooms and fight monsters.

The original plan was to be semi-tactical and realtime. The idea is that your actions can be fast in any room where no one is in fight mode (called "Baston", French slang for "brawl"). If someone is, all actions, including movement, are subjected to a timer.

There is a slight notion of positioning as rooms contain several lines where players, monsters and objects can be. You have to be in the same line as another thing in order to interact with it.

How to use
==========
Start the server : python server.py

Start the client : python clientSDL.py
Log in using Iv/123

Status
======
I considered it originally as a proof of concept for me to test how easily I could make a basic graphical MUD in python. The architecture is therefore a bit poor but it is working. I don't really have plans to continue it, but maybe some days when I don't really feel motivation to work on my regular projects, I'll try to improve this one.

![Screenshot](https://i.imgur.com/u2T6jF8.png)

License
=======
I used graphical items from various sources, it is mentionned in img/COPYRIGHT

The source code is licensed under the GNU Affero General Public License ( http://www.gnu.org/licenses/agpl.html ) 
