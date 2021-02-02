import tkinter as tk
from tkinter.filedialog import askopenfilename
from PIL import ImageTk,Image
import numpy as np
import cv2
import time
from tkinter import messagebox as mb
import os.path
from datetime import date
from resizeimage import resizeimage

def pathMaker():
    pathMain = './Futurist/'
    os.mkdir(pathMain)
    path = './Futurist/outputs/'
    patPath = './Futurist/pattern/'
    os.mkdir(path)
    os.mkdir(patPath)

def timestamp():
    global current_time,Date,dateTime
    
    today = date.today()
    Date = today.strftime("%d_%m_%Y")
    
    t = time.localtime()
    current_time = time.strftime("%H_%M_%S", t)
    
    dateTime = 'IMG_'+str(Date)+'_'+str(current_time)
    
def openfilename():
    timestamp()    
    filename = askopenfilename(filetypes = (("jpeg files","*.jpg"),("png files","*.png")))
    return filename 

def import_img():
    open_img()
    
def open_img(): 
    global v,imgLoc
    # Select the Imagename  from a folder  
    imgLoc = openfilename()
    #print(imgLoc)
    v.set(imgLoc)
    # opens the image 
    img = Image.open(imgLoc) 
    # resize the image and apply a high-quality down sampling filter 
    img = img.resize((200, 200), Image.ANTIALIAS) 
    # PhotoImage class is used to add image to widgets, icons etc 
    img = ImageTk.PhotoImage(img) 
    # create a label 
    panel = tk.Label(root, image = img)
    # set the image as img  
    panel.image = img 
    panel.place(x=10,y=130)
    tk.Label(root,text = 'Selected Image',font=('Helvetica',10, 'bold'),fg="white", bg="blue",width=25).place(x=10,y=335)


p = False

imgLoc = ''

def extract():
    global result,close,ROI,gray,p

    if(v.get()):
        #Get Image & Convert To B/W
        image = cv2.imread(imgLoc)
        result = image.copy()
        image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        lower = np.array([90, 38, 0])
        upper = np.array([145, 255, 255])
        '''
        lower = np.array([90,90,0])
        upper = np.array([140,255,255])
        '''
        mask = cv2.inRange(image, lower, upper)
        
        #Morphing Signature Element
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
        opening = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
        cv2.imwrite('./Futurist/outputs/IMG_'+str(dateTime)+'_opening.png', opening)
        
        close = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel, iterations=2)
        cv2.imwrite('./Futurist/outputs/IMG_'+str(dateTime)+'_close.png', close)
        
        #Signature Detections Using Contours
        cnts = cv2.findContours(close, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = cnts[0] if len(cnts) == 2 else cnts[1]
        
        #Box Plotting Around Signature
        boxes = []
        for c in cnts:
            (x, y, w, h) = cv2.boundingRect(c)
            boxes.append([x,y, x+w,y+h])
        
        #Box Creation
        boxes = np.asarray(boxes)
        left = np.min(boxes[:,0])
        top = np.min(boxes[:,1])
        right = np.max(boxes[:,2])
        bottom = np.max(boxes[:,3])
        
        #Make Image In Rectangle i.e. Fitting Image To Retangle
        result[close==0] = (255,255,255)
        ROI = result[top:bottom, left:right].copy()
        cv2.rectangle(result, (left,top), (right,bottom),(255,255,255))
        
        #Convert To Gray
        gray = cv2.cvtColor(ROI, cv2.COLOR_BGR2GRAY)
        
        p = True
        
        if not os.path.exists('./Futurist/') :
            pathMaker()

        mb.showinfo("Futurist","Processing Done")

    else :
        mb.showinfo("Alert","No Image Selected\nSelect Image First")
        p = False
    #print('Prcessing Done \n %s seconds'% (time.time() - start_time))

def writeImg():
    #start_time = time.time()
    if p == False:
        mb.showinfo("Alert","No Signature Extraction Done.\nExtract Signature First.")
    else :
        #Save Images
        cv2.imwrite('./Futurist/outputs/'+str(dateTime)+'_result.png', result)
        cv2.imwrite('./Futurist/outputs/'+str(dateTime)+'_close.png',close)
        cv2.imwrite('./Futurist/outputs/'+str(dateTime)+'_ROI.png',ROI)
        cv2.imwrite('./Futurist/outputs/'+str(dateTime)+'_gray.png',gray)
        
        img = cv2.imread('./Futurist/outputs/'+str(dateTime)+'_ROI.png', cv2.IMREAD_UNCHANGED)
        
        width = 455
        height = 256
        dim = (width, height)
        # resize image
        resized = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
        cv2.imwrite('./Futurist/outputs/'+str(dateTime)+'_resized.png', resized)
        
        mb.showinfo("Futurist","Write & Resize Done")    
    #print('Writing Process Performed \n %s seconds'% (time.time() - start_time))


def genPatFile():
    #start_time = time.time()
    global arrImg
    
    if os.path.exists('./Futurist/outputs/'+str(dateTime)+'_gray.png'):
        f = True
        #print ("Extracted Image Exist")
    else : 
        f = False
        
    if f == True:
        img = Image.open('./Futurist/outputs/'+str(dateTime)+'_gray.png')
        arrImg = np.array(img)
        arrImg = arrImg-0
        
        with open('./Futurist/pattern/PAT_'+str(dateTime)+'_imgArr.txt', 'w') as outfile:
            #Shape
            outfile.write('# Array shape: {0}\n'.format(arrImg.shape))
            #2D Array Filling    
            for i in range(len(arrImg)):
                for j in range(len(arrImg[i])):
                    outfile.write(str(arrImg[i][j])+' ')
                outfile.write('\n')
                    
            outfile.write('# New slice\n')
        outfile.close()
        mb.showinfo("Futurist","Pattern File Generated")
    else :
        mb.showinfo("Alert", "Extracted Image Not Exist\nSave Images First.")

        
    #print('Generation Done \n %s seconds'% (time.time() - start_time))
 
def genPatImage():
    #start_time = time.time()
    if not os.path.exists('./Futurist/pattern/PAT_'+str(dateTime)+'_imgArr.txt'):
        mb.showinfo("Alert", "No Pattern File Generated .\nGenerate It First ....")
    else : 
        invimage = Image.fromarray(arrImg)
        invimage.save('./Futurist/outputs/'+str(dateTime)+'_patImage.png')
        mb.showinfo("Futurist","Pattern Image Generated")
    #print('Pattern Processing Done \n %s seconds'% (time.time() - start_time))
    
def open_images():
    global panel,l
    
    if os.path.exists('./Futurist/outputs/'+str(dateTime)+'_close.png') or os.path.exists('./Futurist/outputs/'+str(dateTime)+'_ROI.png') or os.path.exists('./Futurist/outputs/'+str(dateTime)+'_patImage.png') or os.path.exists('./Futurist/outputs/'+str(dateTime)+'_result.png'):
        img = Image.open('./Futurist/outputs/'+str(dateTime)+'_close.png') 
        img = img.resize((200, 200), Image.ANTIALIAS) 
        img = ImageTk.PhotoImage(img) 
        panel = tk.Label(root, image = img)
        panel.image = img 
        panel.place(x=300,y=172)
        l = tk.Label(root,text ='Cleaned Image',font=('Helvetica',10, 'bold'),fg="white", bg="blue", width=25)
        l.place(x=300,y=150)
        
        img = Image.open('./Futurist/outputs/'+str(dateTime)+'_result.png') 
        img = img.resize((200, 200), Image.ANTIALIAS) 
        img = ImageTk.PhotoImage(img) 
        panel = tk.Label(root, image = img)
        panel.image = img 
        panel.place(x=520,y=172)
        l = tk.Label(root,text ='Resultant Image',font=('Helvetica',10, 'bold'),fg="white", bg="blue",width=25)
        l.place(x=520,y=150)
    
        img = Image.open('./Futurist/outputs/'+str(dateTime)+'_ROI.png') 
        img = img.resize((200, 200), Image.ANTIALIAS) 
        img = ImageTk.PhotoImage(img) 
        panel = tk.Label(root, image = img)
        panel.image = img 
        panel.place(x=300,y=413)
        l = tk.Label(root,text = 'Final Image',font=('Helvetica',10, 'bold'),fg="white", bg="blue",width=25)
        l.place(x=300,y=390)
    
        img = Image.open('./Futurist/outputs/'+str(dateTime)+'_patImage.png') 
        img = img.resize((200, 200), Image.ANTIALIAS) 
        img = ImageTk.PhotoImage(img) 
        panel = tk.Label(root, image = img)
        panel.image = img 
        panel.place(x=520,y=413)
        l = tk.Label(root,text ='Pattern Image',font=('Helvetica',10, 'bold'),fg="white", bg="blue",width=25)
        l.place(x=520,y=390)
    else :
        mb.showinfo("Futurist","No Image Extracted & Saved.\nExtract Image & Save It First.")
    
def openPatTxt():
    os.system("notepad.exe " + './Futurist/pattern/PAT_'+str(dateTime)+'_imgArr.txt')
    
def about():
    mb.showinfo("About Us","Hello, Futurist Here")
    
def openclose():
    if os.path.exists('./Futurist/outputs/IMG_'+str(dateTime)+'_opening.png') and os.path.exists('./Futurist/outputs/IMG_'+str(dateTime)+'_close.png'):
        img = Image.open('./Futurist/outputs/IMG_'+str(dateTime)+'_opening.png') 
        img = img.resize((200, 200), Image.ANTIALIAS) 
        img = ImageTk.PhotoImage(img) 
        panel = tk.Label(root, image = img)
        panel.image = img 
        panel.place(x=740,y=172)
        l = tk.Label(root,text ='Opening Image',font=('Helvetica',10, 'bold'),fg="white", bg="blue",width=25)
        l.place(x=740,y=150)
        
        img = Image.open('./Futurist/outputs/IMG_'+str(dateTime)+'_close.png') 
        img = img.resize((200, 200), Image.ANTIALIAS) 
        img = ImageTk.PhotoImage(img) 
        panel = tk.Label(root, image = img)
        panel.image = img 
        panel.place(x=740,y=412)
        l = tk.Label(root,text ='Closing Image',font=('Helvetica',10, 'bold'),fg="white", bg="blue",width=25)
        l.place(x=740,y=390)
        
    else:
        mb.showinfo('Alert',"No Extraction Done\nPerform Extraction First")
        
root = tk.Tk()
root.title("Futurist - Signature Extractor And Recognizer")

menubar = tk.Menu(root)
# create more pulldown menus
helpmenu = tk.Menu(menubar, tearoff=0)
helpmenu.add_command(label="About",command=about)
menubar.add_cascade(label="Help", menu=helpmenu)
# display the menu
root.config(menu=menubar)
#root.iconbitmap("logo.ico")
root.geometry("1000x680+200+200")
root.configure(background="orange")

tk.Label(root, text='Image Path',font=('Helvetica',10, 'bold'),fg="white", bg="orange").place(x=10,y=10)
v = tk.StringVar()
entry = tk.Entry(root, textvariable=v, state='disabled').place(x=90,y=11)

tk.Button(root, text='Browse Image', command=import_img, font=('Helvetica',9),fg="white", bg="blue",width=14).place(x=10,y=50)
tk.Button(root, text='Open Extracted Images',command=open_images,font=('Helvetica',9),fg="white", bg="blue", width=30).place(x=10,y=90)

tk.Button(root, text='Extract Features',command=extract,font=('Helvetica',9),fg="white", bg="blue",width=21).place(x=300,y=10)
tk.Button(root, text='Save Processed Images',command=writeImg,font=('Helvetica',9),fg="white", bg="blue",width=21).place(x=300,y=45)
tk.Button(root, text='Generate Pattern File',command=genPatFile,font=('Helvetica',9),fg="white", bg="blue", width=21).place(x=300,y=80)
tk.Button(root, text='Generate Pattern Image',command=genPatImage,font=('Helvetica',9),fg="white", bg="blue", width=21).place(x=300,y=115)

tk.Button(root, text='Open Pattern File',command=openPatTxt,font=('Helvetica',9),fg="white", bg="blue",width=30).place(x=500,y=10)
tk.Button(root, text='Open Cleaned Images', command=openclose,font=('Helvetica',9),fg="white", bg="blue", width=30).place(x=500,y=45)


root.mainloop()

''' pyinstaller --noconsole --onefile -w -F -i"logo.ico" -n"Futurist Signare" signgui.pyw '''