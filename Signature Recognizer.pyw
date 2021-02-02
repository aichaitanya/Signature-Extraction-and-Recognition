#packages

import tkinter as tk
from tkinter.filedialog import askopenfilename
from PIL import ImageTk,Image
import numpy as np
import cv2
import time
from tkinter import messagebox as mb
import os.path
from datetime import date

# TensorFlow and tf.keras
import tensorflow as tf
from tensorflow import keras
# Helper libraries
from sklearn.model_selection import train_test_split

#for writing Excel sheet
import xlwt 
from xlwt import Workbook 
# Reading an excel file using Python 
import xlrd
#for creating csv
import pandas as pd

#------------------------Constants---------------------------------------------------------------------------------

p = False
e = False
b = False
en=''
imgLoc = ''
imgACLoc = ''
global imlist
imlist = []
aclist = []
global c
c=int(0)

#---------------------------------------------------------------------------------------------------------

def pathMaker():
    pathMain = './Futurist/'
    os.mkdir(pathMain)
    path = './Futurist/outputs/'
    resPath = './Futurist/resized/'
    act = './Futurist/actual/'
    os.mkdir(act)
    newSignPath = './Futurist/actual/extracted/'
    csvLoc = './Futurist/csv/'
    actRes = './Futurist/actual/resized/'
    model = './Futurist/model/'
    os.mkdir(path)
    os.mkdir(resPath)
    os.mkdir(newSignPath)
    os.mkdir(csvLoc)
    os.mkdir(actRes)
    os.mkdir(model)

#----------------------Timestamp-----------------------------------------------------------------------------------

def timestamp():
    global current_time,Date,dateTime
    
    today = date.today()
    Date = today.strftime("%d_%m_%Y")
    
    t = time.localtime()
    current_time = time.strftime("%H_%M_%S", t)
    
    dateTime = 'IMG_'+str(Date)+'_'+str(current_time)

#--------------------------------------Select Image Selection Folder-------------------------------------------------------------------

def openfilename():
   
    filename = askopenfilename(filetypes = (("jpeg files","*.jpg"),("png files","*.png")))
    return filename 

import string

def openfilename2():
    from tkinter import filedialog as fd    
    files = fd.askopenfilenames(parent=root,title='Choose a file',filetypes = (("jpeg files","*.jpg"),("png files","*.png")))
    filename = root.tk.splitlist(files)
    return filename
#-------------------------------------Append Selected Images To List--------------------------------------------------------------------

def open_img():
    global listLen
    
    b=True
    
    if len(en)!=0:
        
        global v,imgLoc
        # Select the Imagename  from a folder  
        imgLoc = openfilename2()
        v.set(imgLoc)
        # opens the image 
        for i in range(0,len(imgLoc)):
            img = Image.open(imgLoc[i]) 
            # resize the image and apply a high-quality down sampling filter 
            img = img.resize((200,200), Image.ANTIALIAS)
            # PhotoImage class is used to add image to widgets, icons etc 
            img = ImageTk.PhotoImage(img)
        
            imlist.append(imgLoc[i])
        # create a label 
        panel = tk.Label(root, image = img)
        # set the image as img  
        panel.image = img 
        panel.place(x=10,y=130)
        tk.Label(root,text = 'Selected Image',font=('Helvetica',10, 'bold'),fg="white", bg="turquoise4",width=25).place(x=10,y=315)
        c = ctr.get()
        c=int(c)+len(imgLoc)
        counter.set(str(c))
        listLen = len(imlist)
        clear['state'] = tk.NORMAL

        col = 400
        row = 10

        for i in range(0,len(imlist)):
            pl = Image.open(imlist[i]) 
            # resize the image and apply a high-quality down sampling filter 
            pl = pl.resize((100,100), Image.ANTIALIAS)
            # PhotoImage class is used to add image to widgets, icons etc 
            pl = ImageTk.PhotoImage(pl)
            panel = tk.Label(root, image = pl)
            # set the image as img  
            panel.image = pl
            panel.place(x=row,y=col)
            row += 103
            if (row > 1010):
                row = 10
                col += 103

    else :
        b = False
        mb.showinfo("Alert","Please Enter Name First")
        
def import_img():
    open_img()
    acu.set(str('00.00')+' %')

#---------------------------------------------------------------------------------------------------------

def extract():
    # constants
    global result,close,ROI,gray,p,filen

    # classification accuracy
    acu.set(str('00.00')+' %')

    # create 'futurist' folder on drive
    if not os.path.exists('./Futurist/') :
        pathMaker() #call function to create folder and subfolders

    # folder inside 'futurist' .. for storing resized i.e. fixed dimension image
    directoryPath = './Futurist/resized/'
    filen = len(os.listdir(directoryPath)) # check folder length

    # if folder is not empty then data is present
    if len(imlist) != 0 :

        #check if images are selected or not
        if counter.get() !='0' :

            # lets extract every image inside loop .. 'imlist' contains 
            for i in range(len(imlist)):

                # just for confirmation .. checking if images are actually selectede or not
                if(v.get()):
                    
                    #Get Image & Convert To B/W
                    image = cv2.imread(imlist[i]) #read image path from list
                    result = image.copy() #create copy of image and store in variable
                    image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV) #converting image color space from rgb to hsv

                    # color detection : lowest color which should be detected is (lower) color code & highest color which should be detected is (upper) color code
                    # it also specifies range of color code .. so every color inside that common shared range can be detected 
                    
                    lower = np.array([90, 38, 0])
                    upper = np.array([145, 255, 255])

                    # detect color inside image
                    mask = cv2.inRange(image, lower, upper)
                    
                    #Morphing Signature Element using Erosion & Dilation Process
                    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
                    opening = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
                    cv2.imwrite('./Futurist/outputs/'+str(en)+'_'+str(i)+'_opening.png', opening)
                    
                    close = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel, iterations=2)
                    cv2.imwrite('./Futurist/outputs/'+str(en)+'_'+str(i)+'_close.png', close)
                    
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
                    
                    writeImg(i)
                    
                    e = True
            
                else :
                    p = False
                    e = False
    else :
        e = False # Folder 'Futurist' is empty
        
    if e == True: # if folder is not empty
        excel_csv() # write image data to user_data.xls & user_classes.csv
        msg = "Extraction & Write Done\nTotal Images Extracted : "+str(i+1)
        mb.showinfo("Futurist",msg)

        
    else :
        mb.showinfo("Alert","No Image Selected\nSelect Image First")
            
    imlist.clear() # clear list of selected image

    # set number of image selected to zero .. as all images are successfully extracted
    c=int(0)
    counter.set(0)
    # disable extraction & clear list button
    clear['state'] = tk.DISABLED
    vall['state'] = tk.DISABLED
 
def writeImg(i):
    if p == True:
        #Save Images
        cv2.imwrite('./Futurist/outputs/'+str(en)+'_'+str(i)+'_result.png', result)
        cv2.imwrite('./Futurist/outputs/'+str(en)+'_'+str(i)+'_close.png',close)
        cv2.imwrite('./Futurist/outputs/'+str(en)+'_'+str(i)+'_ROI.png',ROI)
        cv2.imwrite('./Futurist/outputs/'+str(en)+'_'+str(i)+'_gray.png',gray)

        #read cleaned image
        img = cv2.imread('./Futurist/outputs/'+str(en)+'_'+str(i)+'_ROI.png', cv2.IMREAD_UNCHANGED)

        # resize cleaned image and store it again
        width = 455
        height = 256
        dim = (width, height)
        directoryPath = './Futurist/resized/'
        filen = len(os.listdir(directoryPath))
        # resize image
        resized = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
        cv2.imwrite('./Futurist/resized/'+str(filen)+'.jpg', resized)
       
#---------------------------------------------------------------------------------------------------------

def acOpenImg():
    
    global bb
    bb=True
    
    if len(en)!=0:
        
        global ac,imgACLoc
        # Select the Imagename  from a folder  
        imgACLoc = openfilename()
        ac.set(imgACLoc)
        # opens the image 
        img = Image.open(imgACLoc) 
        # resize the image and apply a high-quality down sampling filter 
        img = img.resize((200, 200), Image.ANTIALIAS)
        # PhotoImage class is used to add image to widgets, icons etc 
        img = ImageTk.PhotoImage(img)
        
        # create a label 
        panel = tk.Label(root, image = img)
        # set the image as img  
        panel.image = img 
        panel.place(x=530,y=130)
        tk.Label(root,text = 'Selected Image',font=('Helvetica',10, 'bold'),fg="white", bg="turquoise4",width=25).place(x=530,y=315)
        
    else :
        bb = False
        mb.showinfo("Alert","Please Enter Name First")
        
       
def acImportImg():
    acOpenImg()
    aclist.insert(0,imgACLoc)
    extact['state'] = tk.NORMAL
    
def extact():
    global result,close,ROI,gray,pp,ee
    
    timestamp()
    
    if not os.path.exists('./Futurist/') :
        pathMaker()
    
    if len(aclist) != 0 :        
        if len(ac.get()) != 0:
            #Get Image & Convert To B/W
            image = cv2.imread(aclist[0])
            result = image.copy()
            image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
                    
            lower = np.array([90, 38, 0])
            upper = np.array([145, 255, 255])

            mask = cv2.inRange(image, lower, upper)
                    
            #Morphing Signature Element
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
            opening = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
            cv2.imwrite('./Futurist/actual/extracted/'+str(en)+'_opening.png', opening)
                
            close = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel, iterations=2)
            cv2.imwrite('./Futurist/actual/extracted/'+str(en)+'_close.png', close)
                    
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
                    
            pp = True
            writeAcImg()
            ee = True
            
        else :
            pp = False
            ee = False
    else :
        ee = False
        
    if ee == True:
        msg = "Extraction & Write Done\Image Extracted Successfully"
        mb.showinfo("Futurist",msg) 
    else :
        mb.showinfo("Alert","No Image Selected\nSelect Image First")
    recognize['state'] = tk.NORMAL
    
def writeAcImg():
    if pp == True:
        #Save Images
        cv2.imwrite('./Futurist/actual/extracted/'+str(en)+'_result.png', result)
        cv2.imwrite('./Futurist/actual/extracted/'+str(en)+'_close.png',close)
        cv2.imwrite('./Futurist/actual/extracted/'+str(en)+'_ROI.png',ROI)
        cv2.imwrite('./Futurist/actual/extracted/'+str(en)+'_gray.png',gray)
        
        img = cv2.imread('./Futurist/actual/extracted/'+str(en)+'_ROI.png', cv2.IMREAD_UNCHANGED)
        
        width = 455
        height = 256
        dim = (width, height)
        directoryPath = './Futurist/actual/resized/'
        filen = len(os.listdir(directoryPath))
        # resize image
        resized = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
        cv2.imwrite('./Futurist/actual/resized/IMG_'+str(en.upper())+'.jpg', resized)
       
#---------------------------------------------------------------------------------------------------------

def nameDis():
    global en
    en = entryname.get()
    en=en.upper()
    if len(en)!=0:
        mb.showinfo("Futurist","Welcome To Futurist, "+en)
        entryname.config(state='disabled')
        done['state'] = tk.DISABLED
        change['state'] = tk.NORMAL
        browse['state'] = tk.NORMAL
        extract['state'] = tk.NORMAL
        acbrowse['state'] = tk.NORMAL
        extact['state'] = tk.DISABLED
        classify['state'] = tk.NORMAL
        recognize['state'] = tk.DISABLED
        
    else :
        mb.showinfo("Alert","Please Enter Your Name ")
        
    
def changeName():
    if len(en)!=0:
        entryname.config(state='normal')
        done['state']=tk.NORMAL
        change['state'] = tk.DISABLED
        browse['state'] = tk.DISABLED
        extract['state'] = tk.DISABLED
        acbrowse['state'] = tk.DISABLED
        extact['state'] = tk.DISABLED
        classify['state'] = tk.DISABLED
        recognize['state'] = tk.DISABLED
        clear['state'] = tk.DISABLED
        aclist.clear()
        imlist.clear()
        c=int(0)
        counter.set(str(c))
    else:
        mb.showinfo("Alert","Please Enter Your Name")

#--------------------------------------------------------------------------------------------------------------------------------
        
def about():
    if len(en) != 0:
        mb.showinfo("About Us","Hello "+en+", Futurist LLC Here")
    else:
        mb.showinfo("About Us","Hello User, Futurist LLC Here")
 
def listToString(s):
    # initialize an empty string 
    str1 = ""  
    # traverse in the string   
    for ele in s:  
        str1 += ele   
    return str1
       
def excel_csv():
    global existing_classes,existing_images,classes,no_of_images_excel,images,usernames,UserName,no_of_images
    
    
    
    if len(os.listdir('./Futurist/csv/')) == 0:
        wb_w = Workbook() 
         
        # add_sheet is used to create sheet. 
        sheet1 = wb_w.add_sheet('Sheet 1',cell_overwrite_ok=True) 
        style = xlwt.easyxf('font: bold 1') 
        sheet1.write(0,0,0)
        sheet1.write(0,1,0)
        sheet1.write(1,0,'User Name',style)
        sheet1.write(1,1,'No. of Images',style)
        sheet1.write(1,2,'Images',style)
        sheet1.write(1,3,'Class_Id',style)
        wb_w.save('./Futurist/csv/user_data.xls')
        
    # Give the location of the file 
    loc = ("./Futurist/csv/user_data.xls") 
      
    # To open Workbook 
    wb_r = xlrd.open_workbook(loc) 
    sheet = wb_r.sheet_by_index(0) 
      
    # For row 0 and column 0 
    existing_classes=int(sheet.cell_value(0, 0)) 
    existing_images=int(sheet.cell_value(0, 1))     
    # Workbook is created 
    wb_w = Workbook() 
     
    # add_sheet is used to create sheet. 
    sheet1 = wb_w.add_sheet('Sheet 1',cell_overwrite_ok=True) 
    style = xlwt.easyxf('font: bold 1') 
    
    sheet1.write(1,0,'User Name',style)
    sheet1.write(1,1,'No. of Images',style)
    sheet1.write(1,2,'Images',style)
    sheet1.write(1,3,'Class_Id',style)
    
    
    #writing existing data into new excel file
    for i in range(2,sheet.nrows):
        old_user_name=str(sheet.cell_value(i, 0))
        old_No_of_images=int(sheet.cell_value(i, 1))
        old_Images=str(sheet.cell_value(i, 2))
        old_class_ID=str(sheet.cell_value(i,3))
        sheet1.write(i,0,str(old_user_name))
        sheet1.write(i,1,int(old_No_of_images))
        sheet1.write(i,2,str(old_Images))
        sheet1.write(i,3,str(old_class_ID))
    
    #for checking if there exist same user
    classes=list()
    no_of_images_excel=list()
    images=list()
    usernames=list()
    
    for i in range(2,sheet.nrows):
        classes.append(sheet.cell_value(i, 3))
        no_of_images_excel.append(sheet.cell_value(i, 1))
        images.append(sheet.cell_value(i, 2))
        usernames.append(sheet.cell_value(i, 0))
    
    for i in range(len(classes)):
        classes[i]=int(float(str(classes[i])))
        no_of_images_excel[i]=int(float(str(no_of_images_excel[i])))
    
    UserName=en
    no_of_images=listLen
    
    global filenames_l,filepath,index_user,filename
    
    #checking if the use exists or not
    if UserName in usernames :
        index_user=usernames.index(UserName)
        filenames_l=list()
        filepath=list()
        
        for i in range(existing_images,existing_images+no_of_images):
            filenames_l.append(str(i)+',')
            filepath.append(str(i))
            
        filenames_s=listToString(filenames_l)
        string=str(images[index_user])+filenames_s  
        images[index_user]=string
        no_of_images_excel[index_user]+=no_of_images
        
        for i in range(2,sheet.nrows):
            sheet1.write(i,0,str(usernames[i-2]))
            sheet1.write(i,1,int(no_of_images_excel[i-2]))
            sheet1.write(i,2,str(images[i-2]))
            sheet1.write(i,3,str(classes[i-2]))
            
        #saving existing_classes
        sheet1.write(0,0,int(existing_classes),style)
        #saving existing_images
        sheet1.write(0,1,int(existing_images+no_of_images),style)
        wb_w.save('./Futurist/csv/user_data.xls')
    else:
        sheet1.write(sheet.nrows,0,UserName)
        sheet1.write(sheet.nrows,1,no_of_images)
        filenames_l=list()
        filepath=list()
        
        for i in range(existing_images,existing_images+no_of_images):
            filenames_l.append(str(i)+',')
            filepath.append(str(i))
            
        filenames_s=listToString(filenames_l)
        sheet1.write(sheet.nrows,2,filenames_s)
        sheet1.write(sheet.nrows,3,int(existing_classes)+1)
        #saving existing_classes
        sheet1.write(0,0,int(existing_classes)+1,style)
        #saving existing_images
        sheet1.write(0,1,int(existing_images+no_of_images),style)
        wb_w.save('./Futurist/csv/user_data.xls')
    
    #verifying data write
    wb_v = xlrd.open_workbook(loc) 
    sheet = wb_v.sheet_by_index(0) 
    

    #creating csv file from excel sheet
    classes=list()
    no_of_images_excel=list()
    images=list()
    usernames=list()
    
    existing_classes=int(sheet.cell_value(0, 0)) 
    existing_images=int(sheet.cell_value(0, 1)) 
    
    for i in range(2,sheet.nrows):
        classes.append(sheet.cell_value(i, 3))
        no_of_images_excel.append(sheet.cell_value(i, 1))
        images.append(sheet.cell_value(i, 2))
        usernames.append(sheet.cell_value(i, 0))
    
    for i in range(len(classes)):
        classes[i]=int(float(str(classes[i])))
        no_of_images_excel[i]=int(float(str(no_of_images_excel[i])))
    global classes_df,usernames_df,string_image_name,filelist,fileextension,labels_list
    
    classes_df=list()
    
    #creating classes list for creation of dataframe
    for i in range (len(classes)):
        for j in range(no_of_images_excel[i]):
            classes_df.append(classes[i])
    
    usernames_df=list()
    for k in range(len(classes_df)):
        m=classes_df[k]-1
        usernames_df.append(usernames[m])
    
    #splitting and storing filenames
    filelist=list()
    for i in range(len(images)):
        string_image_name=images[i]
        x=string_image_name.split(',')
        if(x[len(x)-1]==''):
            x.pop()
        for j in range(len(x)):
            filelist.append(x[j])
    
    fileextension=list()
    for i in range (len(filelist)):
        fileextension.append(filelist[i]+'.jpg')
    
    #creation of data frame
    
    data={'username':usernames_df,'classes':classes_df,'image':filelist,'filepath':fileextension}
    
    df = pd.DataFrame(data) 
          
    #writing of csv file
    df.to_csv(r'./Futurist/csv/user_classes.csv',index=False)
    
    #reading csv
    dataframe=pd.read_csv('./Futurist/csv/user_classes.csv') 
    
    labels_list=dataframe['classes'].tolist()
    filename=dataframe['filepath'].tolist()
        
'''
#-------------------------------************************************------------------------------------------
#-----------------------************************MATCHING******************-----------------------------------------------------------------
#-----------------------************************MATCHING******************-----------------------------------------------------------------
#-----------------------************************MATCHING******************-----------------------------------------------------------------
#-----------------------************************MATCHING******************-----------------------------------------------------------------
#-----------------------************************MATCHING******************-----------------------------------------------------------------
#-----------------------************************MATCHING******************-----------------------------------------------------------------
#-----------------------************************MATCHING******************-----------------------------------------------------------------
#-----------------------************************MATCHING******************-----------------------------------------------------------------
#-----------------------************************MATCHING******************-----------------------------------------------------------------
'''
        
def classify():

    # if folder is not present create folder
    if not os.path.exists('./Futurist'):
        pathMaker()

    # if folder is empty .. ask user to first extract image before classification
    if len(os.listdir('./Futurist/csv/')) == 0:
        mb.showinfo("Alert","Hello "+en+"\nPlease Extract Images First")
    else :    
        # specifying path of xls file & creating it ...
        loc = ("./Futurist/csv/user_data.xls") 
          
        # To open Workbook 
        wb_r = xlrd.open_workbook(loc) 
        sheet = wb_r.sheet_by_index(0) 
          
        # For row 0 and column 0 
        existing_classes=int(sheet.cell_value(0, 0)) 
        existing_images=int(sheet.cell_value(0, 1)) 

        #for checking if there exist same user
        classes=list()
        no_of_images_excel=list()
        images=list()
        usernames=list()
        
        for i in range(2,sheet.nrows):
            classes.append(sheet.cell_value(i, 3))
            no_of_images_excel.append(sheet.cell_value(i, 1))
            images.append(sheet.cell_value(i, 2))
            usernames.append(sheet.cell_value(i, 0))
        
        for i in range(len(classes)):
            classes[i]=int(float(str(classes[i])))
            no_of_images_excel[i]=int(float(str(no_of_images_excel[i])))
        
        
        # taking username from inputbox
        UserName=en
        
        #checking if the use exists or not
        if not UserName in usernames :
            mb.showinfo("Futurist","New User Detected\nPlease Extract Your Signatures First")
        else:
            #creating csv file from excel sheet
            classes=list()
            no_of_images_excel=list()
            images=list()
            usernames=list()
            
            existing_classes=int(sheet.cell_value(0, 0)) 
            existing_images=int(sheet.cell_value(0, 1)) 
            
            for i in range(2,sheet.nrows):
                classes.append(sheet.cell_value(i, 3))
                no_of_images_excel.append(sheet.cell_value(i, 1))
                images.append(sheet.cell_value(i, 2))
                usernames.append(sheet.cell_value(i, 0))
            
            for i in range(len(classes)):
                classes[i]=int(float(str(classes[i])))
                no_of_images_excel[i]=int(float(str(no_of_images_excel[i])))
            
            classes_df=list()
            
            #creating classes list for creation of dataframe
            for i in range (len(classes)):
                for j in range(no_of_images_excel[i]):
                    classes_df.append(classes[i])
            
            usernames_df=list()
            for k in range(len(classes_df)):
                m=classes_df[k]-1
                usernames_df.append(usernames[m])
            
            #splitting and storing filenames
            filelist=list()
            for i in range(len(images)):
                string_image_name=images[i]
                x=string_image_name.split(',')
                if(x[len(x)-1]==''):
                    x.pop()
                for j in range(len(x)):
                    filelist.append(x[j])
            
            fileextension=list()
            for i in range (len(filelist)):
                fileextension.append(filelist[i]+'.jpg')
    
            #creation of data frame        
            
            data={'username':usernames_df,'classes':classes_df,'image':filelist,'filepath':fileextension}
            
            df = pd.DataFrame(data) 
              
            #writing of csv file
            df.to_csv(r'./Futurist/csv/user_classes.csv',index=False)
            
            #reading csv
            dataframe=pd.read_csv('./Futurist/csv/user_classes.csv') 
            
            labels_list=dataframe['classes'].tolist()
            filename=dataframe['filepath'].tolist()
            
            directory='./Futurist/resized/'
            extention='.jpg'
            
            width=455
            height=256
            dimension=(width,height)
            
            dataset_list=list()
            
            global class_names 
            
            class_names=usernames
            no_of_classes=len(class_names)+1
            labels=np.array(labels_list)
            
            for i in range(0,len(labels_list)):
                path=directory+filename[i]
                image = cv2.imread(path)
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                resized_gray=cv2.resize(gray,dimension,interpolation=cv2.INTER_AREA)
                imagei = cv2.bitwise_not(resized_gray)
          
                array=np.array(imagei)
                dataset_list.append(array)
            dataset=np.array(dataset_list)

            # split existing images into train & test set
            images_train, images_test, labels_train, labels_test = train_test_split(dataset, labels, test_size=0.25)
         
            train_dataset = images_train

            train_images=train_dataset/255.0
            
            x=int(images_train.shape[0]/5)+1

            # CNN model creation using keras Sequential Convolutional Neural Network using Relu activation function ... 
            model = keras.Sequential([
                keras.layers.Flatten(input_shape=(height,width)),
                keras.layers.Dense(256, activation='relu'),
                keras.layers.Dense(256, activation='relu'),
                keras.layers.Dense(256, activation='relu'),
                keras.layers.Dense(no_of_classes)
            ])

            model.compile(optimizer='adam',
                          loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
                          metrics=['accuracy'])

            # fit data into model and iterate BCNN upto 20 iterations
            model.fit(images_train, labels_train, epochs=20,verbose=0)

            # get test results .. loss & accuracy
            test_loss, test_acc = model.evaluate(images_test, labels_test, verbose=0)
            global probability_model

            # run model with softmax activation function
            probability_model = tf.keras.Sequential([model, 
                                                     tf.keras.layers.Softmax()])

            # predict incoming input i.e. actual image which is to be tested against collection of existing images
            predictions = probability_model.predict(images_test)
            
            sequence=labels_test.shape[0]
            #predictions
            for z in range(sequence):
                predictions[z]
                prediction_class=np.argmax(predictions[z])
    
            # Save the weights of CNN & hence model
            model.save('my_checkpoint')

            # load the saved model again ...
            new_model = tf.keras.models.load_model('my_checkpoint')
            
            # Evaluate the restored model
            loss, acc = new_model.evaluate(images_test, labels_test, verbose=0) # evaluate accuarcy and loss again over loaded model
            acrate = round(100*acc,2)
            acu.set(str(acrate)+' %') # set accuarcy value into inputbox
            mb.showinfo("Futurist","Classification Done Successfully") # classsification has been done successfully
            
#-----------------------************************MATCHING******************-----------------------------------------------------------------
#-----------------------************************MATCHING******************-----------------------------------------------------------------
#-----------------------************************MATCHING******************-----------------------------------------------------------------
#-----------------------************************MATCHING******************-----------------------------------------------------------------
#-----------------------************************MATCHING******************-----------------------------------------------------------------
#-----------------------************************MATCHING******************-----------------------------------------------------------------
#-----------------------************************MATCHING******************-----------------------------------------------------------------
#-----------------------************************MATCHING******************-----------------------------------------------------------------
#-----------------------************************MATCHING******************-----------------------------------------------------------------

def recognition():

    # load saved model
    new_model = tf.keras.models.load_model('my_checkpoint')

    # run model with softmax activation function
    probability_model = tf.keras.Sequential([new_model, tf.keras.layers.Softmax()])
            
    actual_image_path='./Futurist/actual/resized/IMG_'+str(en.upper())+'.jpg' # reading resized image of actual image from folder

    # if xls file is not created or user is new then show alert 'User data not found'
    if len(os.listdir('./Futurist/csv')) == 0: 
        mb.showinfo("Alert","No Existing Data Found\nExtract Images First")
    else : # if exist then read xls data
        loc = ("./Futurist/csv/user_data.xls") 
    
        dataset_actual_list=list()
        #ACCEPT image through GUI

        # open user_data.xls file
        wb_v = xlrd.open_workbook(loc) 
        sheet = wb_v.sheet_by_index(0) 

        # read usernames
        users = list()
        for i in range(2,sheet.nrows):
            users.append(sheet.cell_value(i, 0))
        
        class_names=users

        # read actual image i.e. test image, & convert it from rgb to gray & again convert image to numeric array using np.array
        image = cv2.imread(actual_image_path)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        imagei = cv2.bitwise_not(gray)
        array=np.array(imagei)
        dataset_actual_list.append(array)
        dataset_actual=np.array(dataset_actual_list)
    
        #predicting actual image .. against train set images
        predictions_single = probability_model.predict(dataset_actual)
                
        np.argmax(predictions_single[0])
        
        sequence=dataset_actual.shape[0]
        #predicting class name iteratively 
        for z in range(sequence):
            predictions_single[z]
            prediction_class=np.argmax(predictions_single[z])
            predicted = class_names[prediction_class-1]            
        
        if predicted == en: # if predicted class name is matched with username then signature is genuine, else it is forged ...
            mb.showinfo("Futurist Signare","Dear "+en+"\n\nYour Sign Has Been Recognized")
        else :
            mb.showwarning("Futurist Signare","Dear "+en+"\n\nYour Sign Maybe Forged")

        # disable classify & extract buttons
        classify['state'] = tk.DISABLED
        extact['state'] = tk.DISABLED
        
        aclist.clear() # clearing list in which actual i.e. test image path is appended
'''
#-----------------------*****************RECOGNITION*******************-------------------------------------------------
#-----------------------*****************RECOGNITION*******************-------------------------------------------------
#-----------------------*****************RECOGNITION*******************-------------------------------------------------
#-----------------------*****************RECOGNITION*******************-------------------------------------------------
#-----------------------*****************RECOGNITION*******************-------------------------------------------------
#-----------------------*****************RECOGNITION*******************-------------------------------------------------
#-----------------------*****************RECOGNITION*******************-------------------------------------------------
#-----------------------*****************RECOGNITION*******************-------------------------------------------------
#-----------------------*****************RECOGNITION*******************-------------------------------------------------
#-----------------------*****************RECOGNITION*******************-------------------------------------------------

'''

def clearsel():
    imlist.clear()
    c=int(0)
    counter.set(0)

#-----------------------------------------------------------------------------------------------------------------------

# constants
global root,tk

# creating root of window
root = tk.Tk()
root.title("Futurist Signare")

root.iconbitmap("logo.ico")

menubar = tk.Menu(root)
# create more pulldown menus
helpmenu = tk.Menu(menubar, tearoff=0)
helpmenu.add_command(label="About Us",command=about)
menubar.add_cascade(label="Futurist", menu=helpmenu)
# display the menu
root.config(menu=menubar)

# window size
root.geometry("1111x720+200+200")
root.configure(background="dark turquoise")

# inputbox for accepting username
tk.Label(root, text='Enter Name',font=('Helvetica',10, 'bold'),fg="white", bg="dark turquoise").place(x=10,y=10)
name = tk.StringVar()
entryname = tk.Entry(root, textvariable=name, font=('Helvetica',10, 'bold'), width = 32)
entryname.place(x=90,y=11)

# done button for saving username to variable and xls,csv
done = tk.Button(root,text="Done",command=nameDis,font=('Helvetica',10),bd=0,fg="white", bg="turquoise4",width=14)
done.place(x=10,y=36)

#  in case if user wants to change name
change = tk.Button(root,text="Change",state='disabled',command=changeName,font=('Helvetica',10),bd=0,fg="white", bg="turquoise4",width=14)
change.place(x=134,y=36)

# inputbox which shows path of all images
tk.Label(root, text='Image Path',font=('Helvetica',10, 'bold'),fg="white", bg="dark turquoise").place(x=10,y=68)
v = tk.StringVar()
entry = tk.Entry(root, textvariable=v,font=('Helvetica',10, 'bold'), state='disabled',width = 32).place(x=90,y=68)

# browse button for selecting images for classification process
browse = tk.Button(root, text='Browse Image',state='disabled',command=import_img, font=('Helvetica',10),bd=0,fg="white", bg="turquoise4",width=16)
browse.place(x=10,y=95)

# inputbox which shows count of number of images selected
tk.Label(root, text='Selected',font=('Helvetica',10, 'bold'),fg="white", bg="dark turquoise").place(x=150,y=98)
counter = tk.IntVar()
counter.set(0)
ctr = tk.Entry(root,textvariable=counter,font=('Helvetica',10, 'bold'),state='disabled',width = 3)
ctr.place(x=215,y=98)

# button for extraction of images
extract = tk.Button(root, text='Extract Features',state='disabled',command=extract,font=('Helvetica',10),bd=0,fg="white", bg="turquoise4",width=21)
extract.place(x=330,y=10)

# button for cleaing the selected image list in case if selected any other image mistakenly
clear = tk.Button(root, text='Clear Selection',command=clearsel,state='disabled',font=('Helvetica',10),bd=0,fg="white", bg="turquoise4",width=21)
clear.place(x=330,y=70)

# inputbox which shows path of actual image .. i.e. test image
tk.Label(root, text='Actual Image',font=('Helvetica',10, 'bold'),fg="white", bg="dark turquoise").place(x=530,y=10)
ac = tk.StringVar()
acentry = tk.Entry(root, textvariable=ac,font=('Helvetica',10, 'bold'), state='disabled',width = 32).place(x=625,y=10)

# browse actual i.e. test image
acbrowse = tk.Button(root, text='Actual Image',command=acImportImg,state='disabled', font=('Helvetica',10),bd=0,fg="white", bg="turquoise4",width=16)
acbrowse.place(x=530,y=36)

# button for extraction of actual (test) image
extact = tk.Button(root, text='Extract Actual',command=extact,state='disabled',font=('Helvetica',10),bd=0,fg="white", bg="turquoise4",width=16)
extact.place(x=670,y=36)

# button for Recognition using Saved BCNN Model which will show Siganture is Genuine or Forged
recognize = tk.Button(root, text='Recongnition',command=recognition,state='disabled',font=('Helvetica',10),bd=0,fg="white", bg="turquoise4",width=16)
recognize.place(x=670,y=66)

# button for Classification of Images (train image set) using BCNN uses 20 epochs (iteration) for backpropagation 
classify = tk.Button(root, text='Classify',command=classify,state='disabled',font=('Helvetica',10),bd=0,fg="white", bg="turquoise4",width=21)
classify.place(x=330,y=40)

# inputbox which shows accuracy of classification of model
classacc = tk.Label(root, text='Accuracy',font=('Helvetica',10, 'bold'),fg="white", bg="dark turquoise")
classacc.place(x=250,y=98)
acu = tk.StringVar()
acu.set('00.00 %')
accuracy = tk.Entry(root, textvariable=acu,font=('Helvetica',10, 'bold'), state='disabled',width = 10)
accuracy.place(x=320,y=98)

# run window continuously
root.mainloop()

    
    
    
    
    
