
import curses
import pickle

def addChoiceNode(number, parent):
    story[number] = {'Parent': parent, 'text': [[" ".ljust(80) for i in range(20)]], 'options':{}}

def editChoiceText(number, choiceNum, newText):
    story[number]['options'][choiceNum] = newText

def findchoice():
    choicescount=1
    for node in story:
        for option in story[node]['options']:
            choicescount+=1
    return choicescount

def drawscreen(scr, story, node, page):   
    height,width=scr.getmaxyx()
    if height<24 or width<80:
        scr.move(0,0)
        scr.erase()
        curses.doupdate()
        return
    scr.hline(20,0,'-',width)

    commands=[["^C: Quit","^D: Save story", "^L: Load story", "^N: Nodes"],
              ["^P: Parent", "^I: Insert", "DEL: Delete"]]

    for r in range(2):
        ct=0
        for cmd in commands[r]:
            scr.addstr(21+r,ct*20+5,cmd,curses.A_REVERSE)
            ct+=1
    if width>80: #if we need to fill in the excess space to the right of the document...
        for row in range(height-4):
            scr.addstr(row,80," "*(width-80),curses.A_REVERSE)
    scr.move(0,0)

    c=0
    for line in story[node]['text'][page]:
        scr.addstr(c,0,line)
        c+=1
    pos_r,pos_c=curses.getsyx()
    scr.move(pos_r,pos_c)

def sizecheck(scr): 
    h,w=scr.getmaxyx()
    return h,w,h>=24 and w>=80

def main(scr):
    global current
    global story
    global page
    page=0
    story={
        1 : {
        'Parent': None,
        'text':[[" ".ljust(80) for i in range(20)]],
        'options':{}
        }
    }
    current =1
    drawscreen(scr, story,1,page)
    scr.move(0,0)
    s_height,s_width,enabled=sizecheck(scr)
    while True:
        c = scr.getch()
        if enabled:
            if c>=32 and c<=126: #Matches on any of the 'standard' printable characters.
                pos_r,pos_c=curses.getsyx()
                scr.addstr(pos_r,pos_c,chr(c))
                newText = story[current]['text'][page][pos_r][:pos_c]+chr(c)+story[current]['text'][page][pos_r][pos_c+1:]
                story[current]['text'][page][pos_r] = newText
                if pos_r>=19 and pos_c>=79:
                    scr.move(pos_r,pos_c)
            elif c==curses.KEY_BACKSPACE or curses.keyname(c)=='^H': #Backspace
                pos_r,pos_c=curses.getsyx()
                pos_c-=1
                if pos_c<0:
                    pos_c=s_width-1
                    pos_r-=1
                    if pos_r<0:
                        pos_r=0
                        pos_c=0
                scr.addch(pos_r,pos_c,32)
                scr.move(pos_r,pos_c)
            elif curses.keyname(c) == '^N': #ctrl+N Jump to node screen
                scr.clear()
                pos_r=0
                pos_c=0
                lst=[]
                for choice in story[current]['options']:
                    if choice in story: #implemented choice nodes
                        scr.addstr(pos_r,pos_c, str(pos_r+1)+"[ "+story[current]['options'][choice]+"]")
                        lst.append(choice)

                    else:   #Unimplemented choice nodes
                        scr.addstr(pos_r,pos_c, str(pos_r+1)+"< "+story[current]['options'][choice] +">")
                        lst.append(choice)
                    pos_r+=1
                scr.addstr(3,pos_c, "----")
                scr.addstr(4,pos_c, "1-3 to edit choices")
                scr.addstr(5,pos_c, "!-# to jump to choice node")
                scr.addstr(6,pos_c, ". to delete current node")
                scr.addstr(7,pos_c, "Backspace (or ^H) to return")
                
                while True:
                    c = scr.getch()

                    if c==curses.KEY_BACKSPACE or curses.keyname(c)=='^H':
                        scr.clear()
                        drawscreen(scr,story, current,page)
                        scr.move(0,0)
                        break

                    elif c>=49 and c<=51: #1-3
                        scr.clear()
                        scr.addstr(0,0, "Enter text for choice "+chr(c))
                        scr.move(1,0)
                        curses.echo()
                        textchoice = scr.getstr()
                        curses.noecho()
                        if not textchoice:
                            if (len(lst)==0) or (len(lst)<int(chr(c))):
                                del story[current]['options'][findchoice()+1]
                                if findchoice()+1 in story:
                                    del story[findchoice()+1]
                            else:
                                del story[current]['options'][lst[int(chr(c))-1]]
                                if lst[int(chr(c))-1] in story:
                                    del story[lst[int(chr(c))-1]]
                        else:
                            if (len(lst)==0) or (len(lst)<int(chr(c))):
                                story[current]['options'][findchoice()+1] = textchoice
                            else:
                                story[current]['options'][lst[int(chr(c))-1]] = textchoice
                                    
                        drawscreen(scr,story,current,page)
                        break

                    elif curses.keyname(c)=='!' and len(lst)!=0:
                        scr.clear()
                        if lst[0] not in story:
                            addChoiceNode(lst[0], current)
                        current = lst[0]
                        page=0
                        drawscreen(scr,story,current,page)
                        scr.move(0,0)
                        break
                        
                    elif curses.keyname(c)=='@' and len(lst)>1:
                        scr.clear()
                        if lst[1] not in story:
                            addChoiceNode(lst[1], current)
                        current = lst[1]
                        page=0
                        drawscreen(scr,story,current,page)
                        scr.move(0,0)
                        break

                        
                    elif curses.keyname(c)=='#' and len(lst)>2:
                        scr.clear()
                        if lst[2] not in story:
                            addChoiceNode(lst[2], current)
                        current = lst[2]
                        page=0
                        drawscreen(scr,story,current,page)
                        scr.move(0,0)
                        break
                            
                    elif curses.keyname(c) =='.':
                        if bool(story[current]['options'])==False:
                            tmpcurrent = story[current]['Parent']
                            del story[current]
                            current = tmpcurrent
                            drawscreen(scr, story, current, page)
                        else:
                            scr.addstr(10,0,"Nope, not going to orphan any choices!")
                        break
    
            elif c==curses.KEY_UP:
                pos_r,pos_c=curses.getsyx()
                pos_r=max(pos_r-1,0)
                scr.move(pos_r,pos_c)
            elif c==curses.KEY_DOWN:
                pos_r,pos_c=curses.getsyx()
                pos_r=min(pos_r+1,19)
                scr.move(pos_r,pos_c)
            elif c==curses.KEY_LEFT:
                pos_r,pos_c=curses.getsyx()
                pos_c=max(pos_c-1,0)
                scr.move(pos_r,pos_c)
            elif c==curses.KEY_RIGHT:
                pos_r,pos_c=curses.getsyx()
                pos_c=min(pos_c+1,79)
                scr.move(pos_r,pos_c)

            elif curses.keyname(c)=='^D': #ctrl+D - Binary save
                scr.clear()
                scr.addstr("Enter filename to Save")
                curses.echo()
                scr.move(1,0)
                filename = scr.getstr()
                f=open(filename,'w') #open in 'write' mode
                pickle.dump(story,f)
                f.close()
                curses.noecho()
                scr.clear()
                drawscreen(scr,story, current,page)
                scr.move(0,0)
                    
            elif curses.keyname(c)=='^L': #ctrl+l - Binary restore
                try:
                    scr.clear()
                    curses.echo()
                    scr.addstr("Enter filename to Load")
                    scr.move(1,0)
                    filename = scr.getstr()
                    f=open(filename,'r') #open in 'read' mode
                    story=pickle.load(f)
                    f.close()
                    curses.noecho()
                except IOError: #e.g. if the file doesn't exist yet
                    pass
                current=1
                scr.clear()
                drawscreen(scr,story,current,page)
                scr.move(0,0)
    
            elif curses.keyname(c) == '^P':
                scr.clear
                current = story[current]['Parent']
                if (current==None):
                    current = 1
                page=0
                drawscreen(scr,story,current,page)

            elif curses.keyname(c)=='^I': #Insert (add page)
                story[current]['text'].append([" ".ljust(80) for i in range(20)])
                page+=1
                drawscreen(scr,story,current,page)
                pos_r,pos_c=0,0
                scr.move(pos_r,pos_c)

            elif c==curses.KEY_PPAGE: #PGUP (previous page)
                if page==0:
                    page =0
                else:
                    page-=1
                drawscreen(scr,story,current,page)
                pos_r,pos_c=0,0
                scr.move(pos_r,pos_c)

            elif c==curses.KEY_NPAGE: #PGDN (next page)
                maxpage=-1
                for pages in story[current]['text']:
                    maxpage+=1
                if page<maxpage:
                    page+=1
                drawscreen(scr,story, current, page)
                pos_r,pos_c=0,0
                scr.move(pos_r,pos_c)

            elif c==curses.KEY_DC: #Delete (remove page)
                story[current]['text'].pop(page)
                if (len(story[current]['text'])<=0):
                    story[current]['text'].append([" ".ljust(80) for i in range(20)])
                    page=0
                    drawscreen(scr,story,current,page)
                    pos_r,pos_c=0,0
                    scr.move(pos_r,pos_c)
                elif page==0:
                    pass
                else:
                    page = ((page-1)+len(story[current]['text']))%len(story[current]['text'])
                drawscreen(scr,story,current,page)
                pos_r,pos_c=0,0
                scr.move(pos_r,pos_c)

            elif c==10: #linefeed
                pos_r,pos_c=curses.getsyx()
                pos_c=0
                pos_r=min(pos_r+1,19)
                scr.move(pos_r,pos_c)

            elif c==curses.KEY_HOME: #Jump to start of the current line
                pos_r,pos_c= curses.getsyx()
                pos_c=0
                scr.move(pos_r,pos_c)

            elif c==curses.KEY_END: #Jump to end of the current line
                pos_r,pos_c= curses.getsyx()
                pos_c=79
                scr.move(pos_r,pos_c)
            elif c==curses.KEY_RESIZE:
                s_height,s_width,enabled=sizecheck(scr)
                drawscreen(scr,story, current, page)
        else:
            if c==curses.KEY_RESIZE:
                s_height,s_width,enabled=sizecheck(scr)
                drawscreen(scr,story, current, page)

        curses.doupdate()

try:
    curses.wrapper(main) #We use this wrapper to ensure the terminal is restored to a 'normal' state, even if something crashes
    pass
except KeyboardInterrupt:
    pass
