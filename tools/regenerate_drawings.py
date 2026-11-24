# SPDX-License-Identifier: OFL-1.1
"""Procedural glyph construction. Recreates a candidate glyphs.json from the construction components.
Coordinates: 1000 UPM; y up. Round strokes are expanded and united as curves.
"""
from pathlib import Path
import json
import unicodedata as ud
import pathops
from fontTools.pens.svgPathPen import SVGPathPen

import argparse

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--output", type=Path, default=Path("build/candidate-glyphs.json"))
args = parser.parse_args()
ROOT = Path(__file__).resolve().parents[1] / "sources"
components = json.loads((ROOT/'components.json').read_text())
G, A = {}, {}

from dotmemo_mijote.geometry import path, union, transform

def stroke(d, w=134):
    p = path(d); p.stroke(w, pathops.LineCap.ROUND_CAP, pathops.LineJoin.ROUND_JOIN, 4)
    p.convertConicsToQuads(0.1)
    return pathops.simplify(p)

def dot(x,y,r):
    k=r*.55228475
    return path(f'M{x+r} {y} C{x+r} {y+k} {x+k} {y+r} {x} {y+r} C{x-k} {y+r} {x-r} {y+k} {x-r} {y} C{x-r} {y-k} {x-k} {y-r} {x} {y-r} C{x+k} {y-r} {x+r} {y-k} {x+r} {y}Z')

def clipped_bar(d, width, outline):
    """A slash stays inside the bowl instead of creating external nubs."""
    shell=max(outline.contours,key=lambda p:abs(p.area))
    return pathops.op(stroke(d,width),shell,pathops.PathOp.INTERSECTION)

def add(c, advance, *parts):
    G[c] = union(*[path(p) if isinstance(p,str) else p for p in parts]); A[c] = advance

def pen(c, advance, d, width=134): add(c,advance,stroke(d,width))
def clone(c, base, sx=1, sy=1, dx=0, dy=0, advance=None):
    add(c,advance if advance is not None else A[base],transform(G[base],sx,sy,dx,dy))

# Regression: reflected and ordinary filled paths must merge, never cancel.
_probe=path('M0 0H100V100H0Z')
assert abs(abs(union(_probe,transform(_probe,sx=-1,dx=150)).area)-15000)<.01

for c,s in components['glyphs'].items():
    if c != 'acute': add(c,s['advance'],s['path'])
acute=path(components['glyphs']['acute']['path'])
add('é',A['e'],G['e'],acute)
# These three silhouettes are drawn as continuous contours. The earlier
# union of an oval and a capsule left shoulders and bumps on the right edge.
bowl_head='M258 -12 C121 -12 38 81 46 230 C54 384 147 497 281 496 C410 495 498 407 498 284 '
bowl_counter='M266 130 C322 129 354 181 361 247 C368 312 340 357 286 357 C229 357 191 307 183 243 C175 180 207 132 266 130Z'
add('a',560,bowl_head+'L498 63 C498 17 472 -10 432 -10 C402 -10 380 6 368 31 C337 3 300 -12 258 -12Z '+bowl_counter)
clone('b','d',sx=-1,dx=540,advance=560)
pen('c',510,'M410 405 C361 445 306 450 268 428 C180 398 129 322 122 242 C112 136 166 64 254 57 C309 52 360 74 401 110',138)
pen('f',370,'M133 61 L133 480 C133 600 162 651 235 651 C261 651 283 642 303 626 M48 433 L289 433',130)
add('g',570,bowl_head+'L498 -49 C498 -185 416 -260 285 -260 C219 -260 160 -241 115 -205 C84 -181 83 -145 104 -118 C124 -93 155 -93 182 -112 C211 -132 244 -143 280 -142 C334 -141 362 -111 362 -58 C362 -21 359 13 340 10 C320 -4 291 -12 258 -12Z '+bowl_counter)
add('h',550,G['n'],stroke('M124 380L124 630',134))
pen('ı',270,'M121 62L121 424',132)
add('i',270,G['ı'],dot(123,611,71))
pen('ȷ',290,'M169 425 L169 -70 C169 -158 123 -192 60 -187',132)
add('j',290,G['ȷ'],dot(171,611,71))
pen('k',548,'M124 62L124 630 M144 222L393 427 M240 300L414 61',132)
pen('l',290,'M123 631 L123 151 C123 89 140 59 184 60',132)
add('q',570,bowl_head+'L498 -170 C498 -212 472 -239 432 -239 C392 -239 365 -211 365 -170 L365 -20 C365 15 357 26 340 11 C317 -3 289 -12 258 -12Z '+bowl_counter)
clone('p','q',sx=-1,dx=540,advance=560)
pen('r',430,'M124 61L124 425 M129 293 C159 391 221 436 284 432 C315 430 339 419 361 400',132)
pen('s',507,'M399 405 C354 443 301 456 247 443 C172 425 124 379 135 325 C146 273 217 262 284 237 C362 210 410 179 386 119 C364 62 273 37 201 60 C170 70 145 86 125 104',127)
clone('u','n',sx=-1,sy=-1,dx=520,dy=486,advance=550)
pen('v',525,'M111 424 L250 60 Q260 41 270 67 L416 425',132)
pen('w',770,'M105 425 L199 61 Q205 41 216 67 L365 392 L480 68 Q491 42 502 64 L671 425',127)
pen('x',535,'M115 426L422 60 M415 425L111 61',132)
pen('y',535,'M109 426L262 67 M420 426L245 -56 C202 -147 176 -182 108 -185',132)
pen('z',510,'M116 424 L399 424 L108 61 L411 61',128)

# Capitals: rounded skeletons with optical overshoot and a generous cap height.
pen('A',690,'M117 64 L332 636 Q340 655 350 635 L571 64 M190 260 L493 260',144)
pen('B',657,'M126 65L126 635 L328 635 C443 635 510 582 508 500 C506 425 445 375 347 365 L128 365 M308 365 C457 374 533 313 533 218 C533 121 457 65 329 65 L126 65',139)
pen('C',665,'M545 569 C487 625 417 653 343 641 C197 618 118 506 115 352 C112 193 204 65 347 59 C424 56 493 84 549 137',145)
pen('D',680,'M127 65L127 635L277 635 C456 635 562 530 562 353 C562 169 452 65 277 65Z',142)
pen('E',592,'M483 635L126 635L126 65L493 65 M128 359L429 359',140)
pen('F',574,'M126 65L126 635L485 635 M129 365L426 365',140)
pen('G',700,'M552 575 C495 629 425 653 348 640 C201 617 116 501 115 350 C114 186 207 62 354 58 C434 56 504 89 552 142 L552 316L390 316',140)
pen('H',694,'M126 65L126 635 M564 65L564 635 M130 360L558 360',144)
pen('I',382,'M191 65L191 635 M111 635L271 635 M106 65L276 65',135)
pen('J',554,'M420 635L420 229 C420 111 369 58 274 58 C197 58 139 96 112 162 M311 635L420 635',142)
pen('K',660,'M125 65L125 635 M145 300L533 635 M292 431L548 65',142)
pen('L',563,'M126 635L126 65L472 65',144)
pen('M',858,'M125 65L125 631 Q125 658 142 626 L425 194 L709 629 Q729 657 729 630 L729 65',140)
pen('N',717,'M126 65L126 631 Q126 654 143 627 L571 75 Q589 49 589 73 L589 635',142)
pen('O',716,'M356 642 C211 646 113 524 112 352 C110 184 201 60 351 58 C502 55 605 182 605 352 C605 518 508 640 356 642Z',145)
add('P',637,stroke('M126 65L126 635 L324 635 C449 635 522 566 522 457 C522 345 451 281 322 281L130 281',140))
add('Q',736,G['O'],stroke('M405 218L596 -33',132))
add('R',665,G['P'],stroke('M330 280L550 65',142))
clone('S','s',sx=1.24,sy=1.39,dx=-4,dy=5,advance=626)
pen('T',630,'M315 65L315 635 M104 635L526 635',145)
pen('U',699,'M124 635L124 263 C124 129 206 58 347 58 C485 58 575 131 575 266L575 635',144)
pen('V',667,'M111 635L321 69 Q331 44 343 72 L558 635',145)
pen('W',956,'M112 635L252 68 Q261 44 274 72 L480 573 L674 72 Q685 46 696 70 L845 635',138)
pen('X',670,'M117 635L555 65 M548 635L112 65',142)
pen('Y',639,'M106 635L319 339L533 635 M319 339L319 65',143)
pen('Z',641,'M116 635L526 635L111 65L536 65',137)

# Figures share the cap rhythm; 0 stays narrower than O.
clone('0','O',sx=.83,advance=604)
pen('1',425,'M105 505L240 633L240 66 M111 65L353 65',134)
pen('2',592,'M116 523 C153 616 245 659 336 634 C430 608 482 536 455 454 C435 392 372 343 296 276L114 65L489 65',132)
pen('3',584,'M115 579 C172 631 246 655 321 637 C408 618 456 563 445 497 C432 420 354 377 277 363 M277 363 C390 369 467 311 465 218 C463 120 382 56 279 57 C208 58 150 80 108 126',130)
pen('4',610,'M423 65L423 635 M423 635L106 258L501 258',132)
pen('5',588,'M469 635L160 635L140 380 C196 401 241 409 286 402 C403 389 466 321 460 216 C455 111 378 55 280 57 C209 59 149 84 111 122',133)
pen('6',605,'M459 581 C411 624 354 652 297 636 C188 608 120 473 119 287 C118 142 176 60 292 59 C405 58 484 137 484 243 C484 345 414 413 319 407 C223 402 163 351 124 268',131)
pen('7',570,'M106 635L467 635L222 65',136)
pen('8',607,'M302 640 C196 642 130 583 134 501 C138 420 214 379 304 357 C406 333 478 284 475 200 C472 112 400 58 302 58 C199 58 126 114 127 199 C128 282 206 331 304 357 C393 380 465 424 467 504 C469 584 408 639 302 640Z',128)
clone('9','6',sx=-1,sy=-1,dx=605,dy=700,advance=605)

# Punctuation and symbols. Their strokes are a little lighter than letters.
add(' ',240,path(''))
clone('\u00a0',' '); add('\u202f',155,path(''));add('\u2009',155,path(''))
add('.',258,dot(123,62,70)); add(',',258,stroke('M142 81Q147 -11 77 -67',91))
add(':',258,dot(123,62,65),dot(123,387,65))
add(';',258,G[','],dot(123,387,65))
add('!',293,stroke('M146 265L146 637',120),dot(146,62,68))
add('?',525,stroke('M107 539 C137 618 209 650 287 636 C371 622 427 563 415 490 C405 427 347 391 298 354 C265 329 252 300 252 257',116),dot(252,62,68))
pen("'",206,'M110 635L96 482',90)
pen('’',211,'M133 652Q151 560 79 504',86)
clone('‘','’',sx=-1,sy=-1,dx=210,dy=1155)
add('"',354,stroke('M109 635L99 482',86),stroke('M251 635L241 482',86))
add('”',359,G['’'],transform(G['’'],dx=146))
add('“',359,G['‘'],transform(G['‘'],dx=146))
pen('-',400,'M102 260L299 260',105)
pen('–',620,'M96 260L523 260',100)
pen('—',930,'M96 260L833 260',100)
add('…',754,G['.'],transform(G['.'],dx=248),transform(G['.'],dx=496))
pen('(',353,'M251 700 C80 564 74 151 244 -39',97)
clone(')','(',sx=-1,dx=353)
pen('[',338,'M252 700L117 700L117 -39L252 -39',94)
clone(']','[',sx=-1,dx=338)
pen('{',400,'M290 700 C187 700 167 653 167 562L167 448 C167 368 149 340 83 330 C149 320 167 289 167 211L167 95 C167 7 187 -39 290 -39',91)
clone('}','{',sx=-1,dx=400)
pen('/',450,'M92 -80L356 710',96)
clone('\\','/',sx=-1,dx=450)
pen('|',262,'M131 -80L131 710',90)
pen('_',578,'M80 -97L497 -97',100)
pen('+',576,'M288 484L288 72 M82 278L494 278',103)
pen('=',575,'M92 378L483 378 M92 179L483 179',99)
pen('<',554,'M446 493L118 278L446 63',99)
clone('>','<',sx=-1,dx=554)
pen('«',565,'M278 446L113 276L278 108 M473 446L308 276L473 108',89)
clone('»','«',sx=-1,dx=565)
pen('‹',355,'M263 446L98 276L263 108',89)
clone('›','‹',sx=-1,dx=355)
pen('^',520,'M106 454L260 636L414 454',96)
pen('~',600,'M101 276 C180 399 256 354 304 315 C368 264 437 245 499 348',94)
pen('`',261,'M83 678L178 572',86)
pen('*',449,'M224 680L224 415 M98 588L351 507 M98 507L351 588',77)
pen('#',675,'M253 633L159 65 M516 633L423 65 M115 448L589 448 M85 249L559 249',92)
add('$',635,stroke('M495 570 C439 623 373 641 306 624 C213 599 153 535 166 460 C180 388 270 373 350 338 C447 297 506 253 476 169 C448 90 335 55 246 86 C207 100 175 123 149 148',132),stroke('M315 737L315 -37',60))
pen('%',811,'M126 65L681 635',90)
add('%',811,G['%'],transform(G['0'],sx=.36,sy=.36,dx=61,dy=438),transform(G['0'],sx=.36,sy=.36,dx=514,dy=3))
pen('&',730,'M600 65 L264 417 C168 516 173 625 285 640 C387 652 458 555 408 477 C372 422 261 372 205 328 C124 265 101 179 160 107 C230 21 360 51 440 131 C495 187 544 263 578 344',120)
add('@',920,transform(G['a'],sx=.74,sy=.8,dx=259,dy=128),stroke('M604 472L604 248 C604 164 698 177 738 226 C818 324 793 511 703 602 C578 729 360 713 221 592 C68 456 66 211 207 75 C329 -43 565 -48 706 37',87))
add('€',692,G['C'],stroke('M145 427L433 427 M145 277L402 277',83))
add('£',620,'M109 380 L163 380 L160 458 C155 600 232 705 356 705 C425 705 484 676 535 626 C560 600 557 562 531 538 C507 516 474 519 450 541 C422 568 394 582 359 581 C316 580 287 542 288 463 L291 380 L405 380 C439 380 462 358 462 328 C462 298 439 276 405 276 L292 276 C293 219 278 169 250 129 L497 129 C536 129 561 104 561 65 C561 26 536 0 497 0 L112 0 C74 0 51 25 51 65 C51 95 75 110 97 128 C124 151 174 222 166 276 L109 276 C74 276 52 285 52 328 C52 359 74 380 109 380Z')
add('¥',640,stroke('M106 635L319 390L533 635 M319 390L319 65',139),stroke('M133 285L504 285 M133 145L504 145',72))
add('¢',516,G['c'],stroke('M280 568L280 -70',68))
add('°',340,stroke('M170 675C105 675 70 634 70 580C70 522 111 483 170 483C230 483 271 524 271 580C271 634 232 675 170 675Z',72))
add('·',259,dot(129,279,61))
add('•',360,dot(180,280,101))
add('×',575,stroke('M129 439L447 121 M446 440L128 122',103))
add('÷',575,stroke('M92 278L483 278',99),dot(287,481,53),dot(287,75,53))
add('±',575,G['+'],stroke('M92 -68L483 -68',93))
add('−',575,stroke('M92 278L483 278',99))
pen('¬',575,'M91 378L483 378L483 186',91)
add('¡',293,stroke('M146 62L146 434',120),dot(146,637,68))
clone('¿','?',sx=-1,sy=-1,dx=525,dy=700)
ring=dot(425,350,308)
ring.stroke(76,pathops.LineCap.ROUND_CAP,pathops.LineJoin.ROUND_JOIN,4)
ring.convertConicsToQuads(.1)
for c,base in [('©','C'),('®','R')]:
    add(c,850,ring,transform(G[base],sx=.48,sy=.48,dx=425-A[base]*.24,dy=182))
add('™',895,transform(G['T'],sx=.48,sy=.48,dx=30,dy=384),transform(G['M'],sx=.48,sy=.48,dx=368,dy=384))
pen('†',455,'M228 -46L228 697 M91 425L364 425',83)
add('‡',455,G['†'],stroke('M91 196L364 196',83))
add('‰',1110,G['%'],transform(G['0'],sx=.36,sy=.36,dx=811,dy=3))
pen('§',548,'M409 596 C352 646 244 652 183 605 C125 560 154 491 251 442 L345 392 C448 337 430 259 357 222 M190 469 C91 407 102 331 203 275 L300 222 C399 168 422 99 361 53 C301 9 189 16 131 66',96)
pen('¶',660,'M395 -45L395 635L278 635 C157 635 103 576 103 485 C103 393 163 337 283 337L395 337 M547 635L547 -45',112)
add('¦',262,stroke('M131 -80L131 240 M131 390L131 710',90))
pen('¯',490,'M100 658L390 658',80)
add('¤',650,stroke('M325 503C211 503 142 430 142 327C142 225 212 151 325 151C437 151 508 226 508 327C508 430 437 503 325 503Z M115 536L186 463 M464 465L536 538 M115 117L184 189 M465 189L535 117',82))

# Extended letters and ligatures. They are separate designed glyphs, not text substitutions.
ligature_outer='M270 -12 C126 -12 38 81 46 230 C54 385 153 497 293 496 C381 496 427 452 455 391 C468 364 487 364 501 391 C541 458 588 496 653 496 C765 496 838 421 829 326 C823 266 789 235 724 231 L536 225 C536 168 563 130 617 129 C658 128 692 143 723 162 C741 174 758 172 773 159 C802 136 808 104 783 76 C737 22 671 -12 600 -12 C553 -12 514 25 482 62 C469 85 451 85 442 68 C395 20 337 -12 270 -12Z'
ligature_eye='M548 321 L691 325 C711 326 718 339 708 356 C695 379 670 391 642 390 C599 389 567 361 548 321Z'
oval_counter='M276 130 C334 129 365 181 372 247 C379 312 350 357 294 357 C236 357 196 307 188 243 C180 180 215 132 276 130Z'
ae_counter='M263 130 C319 130 349 176 352 235 L352 292 C351 334 327 357 286 357 C229 357 191 307 183 243 C175 180 207 132 263 130Z'
add('æ',877,ligature_outer+' '+ligature_eye+' '+ae_counter)
add('œ',877,ligature_outer+' '+ligature_eye+' '+oval_counter)
pen('Æ',1010,'M115 65L442 635L571 635L571 65 M285 270L568 270 M574 635L903 635 M574 359L853 359 M574 65L912 65',138)
add('Œ',1075,'M350 -12 C165 -12 40 71 40 350 C40 525 164 706 350 706 L965 706 C1005 706 1034 676 1034 636 C1034 596 1005 566 965 566 L620 566 L620 429 L917 429 C957 429 984 400 984 359 C984 318 957 289 917 289 L620 289 L620 135 L974 135 C1014 135 1043 105 1043 65 C1043 25 1014 -5 974 -5 L606 -5 C523 -12 439 -12 350 -12Z M350 131 C447 131 507 220 507 350 C507 482 449 566 350 566 C234 566 184 482 184 350 C184 220 234 131 350 131Z')
add('ø',550,G['o'],clipped_bar('M110 12L449 482',72,G['o']))
add('Ø',716,G['O'],clipped_bar('M150 17L565 679',82,G['O']))
pen('ß',584,'M123 61L123 474 C123 605 179 670 274 666 C365 663 417 598 406 530 C395 457 316 428 288 386 C264 346 328 323 386 280 C447 235 475 170 433 110 C397 58 322 41 263 71',125)
add('ð',570,'M270 -12 C126 -12 38 81 46 230 C54 385 153 497 293 496 C326 496 355 487 382 473 C395 467 408 476 404 493 C382 549 339 590 275 610 C256 620 238 626 217 629 C186 636 169 658 174 687 C179 716 207 733 237 727 C416 687 520 537 518 311 C518 293 518 271 516 248 C505 96 405 -12 270 -12Z '+oval_counter,stroke('M155 625L385 665',64))
add('Ð',680,G['D'],stroke('M45 354L332 354',95))
add('þ',560,G['b'],stroke('M116 60L116 -170',134))
pen('Þ',637,'M126 65L126 635 M126 527L324 527 C449 527 522 458 522 349 C522 237 451 173 322 173L130 173',140)
add('µ',572,'M463 424 C465 469 437 495 396 494 C356 493 329 467 329 422 L329 206 C328 152 300 122 262 123 C218 124 197 157 197 209 L197 424 C197 470 169 496 127 494 C85 492 60 463 60 418 L60 -164 C60 -209 88 -237 128 -237 C169 -237 197 -209 197 -164 L197 -26 C197 10 211 15 238 9 C276 11 309 25 335 48 C340 9 362 -10 398 -9 C437 -8 463 19 463 59Z')

# Accent components: anchor origin at x=0, y=0 (lowercase accent zone).
acc={
 '\u0301':transform(acute,dx=-315,dy=-570),
 '\u0300':stroke('M-70 125L55 24',82),
 '\u0302':stroke('M-119 28L0 125L119 28',77),
 '\u0308':union(dot(-87,69,46),dot(87,69,46)),
 '\u0303':stroke('M-128 46C-81 116 -32 100 8 69C49 38 92 25 130 93',66),
 '\u030a':stroke('M0 156C-55 156 -85 127 -85 84C-85 42 -54 12 0 12C54 12 85 42 85 84C85 127 54 156 0 156Z',51),
 '\u0327':stroke('M15 -9L-17 -79C55 -76 90 -111 73 -152C55 -192 -13 -198 -62 -175',62)
}
for code in range(0xC0,0x100):
    c=chr(code)
    if c in G: continue
    decomposition=ud.normalize('NFD',c)
    if len(decomposition)==2 and decomposition[0] in G and decomposition[1] in acc:
        base,mark=decomposition
        # Removing the i/j dot avoids collisions with the added accent.
        outline=G['ı'] if base=='i' else G['ȷ'] if base=='j' else G[base]
        zone=775 if base.isupper() else 570
        ax=121 if base=='i' else 169 if base=='j' else A[base]/2+(51 if base=='e' else 0)
        component=transform(acc[mark],dx=ax,dy=zone)
        if mark=='\u0327': component=transform(acc[mark],dx=A[base]/2,dy=0)
        add(c,A[base],outline,component)
add('Ÿ',A['Y'],G['Y'],transform(acc['\u0308'],dx=A['Y']/2,dy=775))
# Keep the reference é exactly, including its accent placement.
add('é',A['e'],G['e'],acute)
for c,mark in [('´','\u0301'),('¨','\u0308'),('ˆ','\u0302'),('˜','\u0303'),('˚','\u030a'),('¸','\u0327')]:
    add(c,380,transform(acc[mark],dx=190,dy=570 if mark!='\u0327' else 0))
for mark,p in acc.items(): add(mark,0,p)
for c,base in [('¹','1'),('²','2'),('³','3')]:
    add(c,338,transform(G[base],sx=.52,sy=.52,dx=10,dy=368))
for c,base in [('ª','a'),('º','o')]:
    add(c,348,transform(G[base],sx=.55,sy=.55,dx=10,dy=360))
for c,num,den in [('¼','1','4'),('½','1','2'),('¾','3','4')]:
    add(c,865,transform(G[num],sx=.5,sy=.5,dx=8,dy=354),stroke('M237 28L620 677',72),transform(G[den],sx=.5,sy=.5,dx=519,dy=0))
add('⁄',335,stroke('M-5 28L349 677',72))
add('\u00ad',400,G['-'])

data={'family':'dotmemo mijote','style':'Bold','version':'0.100','unitsPerEm':1000,'slant':.105,'glyphs':{},'kerning':components['kerning']}
for c in sorted(G,key=ord):
    out=SVGPathPen(None); G[c].draw(out)
    data['glyphs'][c]={'advance':A[c],'path':out.getCommands()}
args.output.parent.mkdir(parents=True, exist_ok=True)
args.output.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
print(f'Drawn {len(G)} Unicode glyphs from source curves.')
