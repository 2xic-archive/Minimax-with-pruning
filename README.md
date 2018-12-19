# Checkers

**Built upon work done by Carson Wilcox**  
**This is under the Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported (CC BY-NC-SA 3.0)**  
**This license can be viewed or obtained at http://creativecommons.org/licenses/by-nc-sa/3.0/**  

I was watching [MIT OpenCourseWare](https://www.youtube.com/watch?v=STjW3eH0Cik) on the minimax algorithm and wanted to play with the algorithm. I found a working implementation [https://github.com/codeofcarson/Checkers](https://github.com/codeofcarson/Checkers) (which this mini-project is built upon). However it was lacking some features to make it into a good implementation for playing with the minimax algorithm, I have tried to fix that with this mini-project.

Some of the changes I have done includes implementation of alpha-beta pruning to make the minimax algorithm more effective, made the game more like a traditional checkers game (implemented kings and the game will now play as long as there are legal moves that can be played) and made a simple web interface to make things more user friendly. 

**Demo**  
<img src="/demo.gif" width="250px" />

**Dependencies**  
* Flask  

**To run the code**  
> python main.py
