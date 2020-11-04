
import curses
import pickle


'''Method to add a choice node'''
def addChoiceNode(number, parent):
    story[number] = {'Parent': parent, 'text': [[" ".ljust(80) for i in range(20)]], 'options':{}}

'''Method to edit a choice node'''
def editChoiceText(number, choiceNum, newText):
    story[number]['options'][choiceNum] = newText

'''Method to return the number of choices associated with a story node'''
def findchoice():
    choicescount=1
    for node in story:
        for option in story[node]['options']:
            choicescount+=1
    return choicescount

'''Method to draw out the screen'''
def drawscreen(scr, story, node, page):
    height,width=scr.getmaxyx()
    if height<24 or width<80:
        scr.move(0,0)
        scr.erase()
        curses.doupdate()
        return
    scr.clear()
    pagecount=0
    for pages in story[current]['text']:
        pagecount+=1
    pagenumber =str(page+1)+"/"+str(pagecount)
    pagenumber = (80-len(pagenumber))*" " + pagenumber
    scr.addstr(0,80-len(pagenumber),pagenumber, curses.A_REVERSE)

    commands=[["^C: Quit","^R: Restart story", "^L: Load story"],
              ["1-3: Select choice"]]
    if (page!=len(story[current]['text'])-1):
        scr.hline(21,0,'-',width)
        for r in range(2):
            ct=0
            for cmd in commands[r]:
                scr.addstr(22+r,ct*20+5,cmd,curses.A_REVERSE)
                ct+=1

    if (page==len(story[current]['text'])-1):
       options = story[current]['options']
       r=0
       for key in story[current]['options']:
           if key in story:
            scr.addstr(21+r,0, str(r+1)+". "+story[current]['options'][key], curses.A_UNDERLINE)
            r+=1


    if width>80: #if we need to fill in the excess space to the right of the document...
        for row in range(height-4):
            scr.addstr(row,80," "*(width-80),curses.A_REVERSE)
    scr.move(0,0)

    c=1
    for line in story[node]['text'][page]:
        scr.addstr(c,0,line)
        c+=1
    pos_r,pos_c=curses.getsyx()
    scr.move(pos_r,pos_c)

'''Method to ensure screen size'''
def sizecheck(scr):
    h,w=scr.getmaxyx()
    return h,w,h>=24 and w>=80

'''Method to check if there are 0 options in the story node. Considers yet unimplemented actions as well'''
def checknodeinstory(story, current):
    for option in story[current]['options']:
        if option in story:
            return True
    return False

def printcommands(scr,width):
    commands=[["^C: Quit","^R: Restart story", "^L: Load story"],
              ["1-3: Select choice", "^D: Save story to txt file"]]
    scr.hline(21,0,'-',width)
    for r in range(2):
        ct=0
        for cmd in commands[r]:
            scr.addstr(22+r,ct*20+5,cmd,curses.A_REVERSE)
            ct+=1

def main(scr):
    global current
    global story
    global page
    fullstory = [] #For printing to txt file
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
        if (page==len(story[current]['text'])-1) and (bool(story[current]['options'])==False or checknodeinstory(story,current)==False):
            printcommands(scr,s_width)
        c = scr.getch()
        if enabled:
            
            if (page==len(story[current]['text'])-1)  and (bool(story[current]['options'])==False or checknodeinstory(story,current)==False):
                if curses.keyname(c) == '^D':
                    scr.clear()
                    scr.addstr(0,0,"Enter file name to save")
                    scr.move(1,0)
                    curses.echo()
                    endfile = scr.getstr()
                    curses.noecho()
                    for pages in story[current]['text']:
                        for text in pages:
                            fullstory.append(text)
                    text_file = open(endfile, "w")
                    for i in fullstory:
                        text_file.write(i)
                    text_file.close()
                    scr.clear()
                    scr.addstr(0,0, "YOUR STORY HAS BEEN SAVED...")
                    printcommands(scr,s_width)
        
                elif curses.keyname(c)=='^L': #ctrl+l - Load file
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
                    page=0
                    scr.clear()
                    drawscreen(scr,story,current,page)
                    scr.move(0,0)

                elif curses.keyname(c)=='^R':
                    current=1
                    page=0
                    drawscreen(scr,story,current,page)

            elif (c>=49 and c<=51) and (page==len(story[current]['text'])-1): #1-3 choice selection
                scr.clear()
                pos_r=0
                pos_c=0
                lst=[]
                for pages in story[current]['text']:
                    for text in pages:
                        fullstory.append(text)
                
                for choice in story[current]['options']:
                    if choice in story:
                        lst.append(choice)
                        
                    if c==49 and len(lst)!=0:
                        scr.clear()
                        current = lst[0]
                        page=0
                        drawscreen(scr,story,current,page)
                        scr.move(0,0)
                        break

                    elif c==50 and len(lst)>1:
                        scr.clear()
                        current = lst[1]
                        page=0
                        drawscreen(scr,story,current,page)
                        scr.move(0,0)
                        break

                    elif c==51 and len(lst)>2:
                        scr.clear()
                        current = lst[2]
                        page=0
                        drawscreen(scr,story,current,page)
                        scr.move(0,0)
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


            elif curses.keyname(c)=='^L': #ctrl+l - Load file
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
                page=0
                scr.clear()
                drawscreen(scr,story,current,page)
                scr.move(0,0)


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

            elif c==curses.KEY_HOME: #Jump to start of the current line
                pos_r,pos_c= curses.getsyx()
                pos_c=0
                scr.move(pos_r,pos_c)

            elif c==curses.KEY_END: #Jump to end of the current line
                pos_r,pos_c= curses.getsyx()
                pos_c=79
                scr.move(pos_r,pos_c)

            elif c==curses.KEY_RESIZE: #As odd as it sounds, resizing the terminal is treated like any other character
                s_height,s_width,enabled=sizecheck(scr)
                drawscreen(scr,story, current, page)
                    
            elif c==curses.KEY_RESIZE:
                s_height,s_width,enabled=sizecheck(scr)
                drawscreen(scr,story, current, page)
                    
            elif curses.keyname(c)=='^R':
                current=1
                page=0
                fullstory = []
                drawscreen(scr,story,current,page)
        else:
            if c==curses.KEY_RESIZE:
                s_height,s_width,enabled=sizecheck(scr)
                drawscreen(scr,story, current, page)

        curses.doupdate()

    print(story)
def newwindow(scr):
    scr.clear()
    begin_x = 20; begin_y = 7
    height = 5; width = 40
    win = curses.newwin(height, width)
    win.addstr(0,0, "Hello im a new window!")
    scr.refresh()
    win.refresh()

try:
    curses.wrapper(main) #We use this wrapper to ensure the terminal is restored to a 'normal' state, even if something crashes
    pass
except KeyboardInterrupt:
    pass
