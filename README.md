# Description of the task

We have 6 categories of items. 
For each categories, we want to present 6 items 10 times. 
Each item is presented as words and images (6 categories * 6 instances * 10 presentations * 2 modalities = 720 presentations of stim)
All the items are ordered in different sequences of 6 items, and cannot appear in two sequences. 
Within a sequence, the 6 categories are represented. 
In total we need to present 120 sequences


- block design
In each block, 3 sequences * 2 modalities * 3 times are presented
Each block allows 36 presentations (out of the 720 neeeded) -> we need 20 blocks
In a block, a stimuli is presented 3 times (out of the 10 wanted). 

If we do this 3seq * 2mod * 3rep block org, we can't do 10 presentations per stim. We need to go with 9 or 12.  

Why 3seq * 2mod * 3rep = 18, but 120/18 = 6.66 blocks. I am retarded? No that's right right. We have only 6 unique sequences in total. 

Concrete examples to understand better : 

----------------------
In 2 block, all items can be presented once.

- block 1 : a, b, c, a', b', c', a, b, c, a', b', c', a, b, c, a', b', c' (108)
- block 2 : d, e, f, d', e', f', d, e, f, d', e', f', d, e, f, d', e', f' (108) -> total 216 stims 
- block 3 : 
- block 4 :
- block 5 :
- block 6 : -> total 648
- block 7 : -> total 756

----------------------
In each block, there are 3 avaible slots because images and words are presented in the same blocks. 
In this scenario, each sequence is presented 9 times instead of 10, which makes 648 presentations. 
If we want to go for 12 presentations, we need to add two blocks.  

- block 1 : a, b, c
- block 2 : d, e, f
- block 3 : a, e, f
- block 4 : b, c, d
- block 5 : a, c, f
- block 6 : b, e, d
- (block 7 : a, b, c)
- (block 8 : d, e, f)

----------------------
1 block = ~ 00:04:30 
8 block without counting the breaks : 36 minutes. Good enough. 

----------------------
Stim list : 

- shapes : carré, triangle, cercle, étoile, losange, ovale. (6*2 syllables)
- colors : rouge, bleu, vert, jaune, orange, violet. (4*1 syllable, 2*2). If we go 6*1, we could compare these with body parts. 
- animals : chat, chien, souris, vache, chameau, elephant. (3*1, 2*2, 1*3)
- landscapes : plage, montagnes, forêt, desert, collines, lac. (2*1, 4*2)
- bodyparts : bras, jambe, doigt, main, pied, oreille, (cou). (5*1, 1*2)
- characters : Shrek, Elsa, Pinochio, Cruella, Alladin, Alice. (1*1, 3*2, 3*3)

if more needed : 

- shapes : rectangle, parralelogram, trapèze, hexagone, anneau, pyramide, cube, cylindre, sphère
- colors : gris, brun, beige, magenta, turquoise, rose, 
- animals : zèbre, cerf, ours, loup, renard, chèvre, cochon
- landscapes : savane, jungle, prairie, clairière, oasis, marécage, île
- bodyparts : épaule, genoux, coude, ventre, cheville, torse
- characters : Gandalf, Hermione, Ariel, Mulan, Frodon, Zorro, Rambo, Tintin

# reward sounds were taken from :
    https://pixabay.com/sound-effects/search/level-up/