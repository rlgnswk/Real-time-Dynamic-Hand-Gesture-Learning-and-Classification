# -*- coding: utf-8 -*-
"""
Created on Mon Jan 27 19:20:12 2020

@author: rlgns
"""
import tkinter
from tkinter import filedialog
from tkinter import messagebox
from tkinter import *
import cv2
import PIL
from PIL import Image
from PIL import ImageTk

import class_server as Server
import class_ARTMAP as ARTMAP

from scipy.spatial import distance

class Myapp():
    def __init__(self, window):
        
        self.handData =[]
        self.x_points = []
        self.y_points = []
        self.forget_param_x = 0.95
        self.forget_param_y = 0.90
        self.pre_up=0.0
        self.pre_down=0.0 
        self.pre_right=0.0
        self.pre_left=0.0
        
        self.gesture_list = []  
        self.MODE_FLAG = 3
        
        self.window=window
        # 창 상단 프르그램 명 설정
        self.window.title("CSEE 316 project")
        # 창 크기 설정
        self.window.geometry("800x500")
        #크기 일단은 불변
        self.window.resizable(False, False)
        
         # 현재 상태 글귀 result_txt
        self.State_txt = tkinter.Label(self.window, text="현재 모드")
        self.State_txt.place(x=0,y=0)
        
        
        #현재 상태  출력 창  State
        self.State = tkinter.Entry(self.window, justify='center')
        self.State.place(x=0, y=20)
        
        # 인식 결과 글귀 result_txt
        self.result_txt = tkinter.Label(self.window, text="인식 결과")
        self.result_txt.place(x=0,y=40)
        
        #인식결과 출력 창 result_output
        self.result_output = tkinter.Entry(self.window, justify='center')
        self.result_output.place(x=0, y=60)
        
        self.Test = tkinter.Button(self.window, text="     Test     ", command=lambda:self.button_pressed_Test())
        self.Test.place(x=0,y=80)
        
        #Stop 버튼 생성 클릭 시 listbox에 등록
        
        self.Stop2 = tkinter.Button(self.window, text="     Stop     ", command=lambda:self.button_pressed_stop())
        self.Stop2.place(x=70,y=80) 
        
        #제스쳐명 글귀
        self.lbl = tkinter.Label(self.window, text="제스쳐 등록")
        self.lbl.place(x=0,y=110)
         
        #제스처 입력창 input_gesture
        self.input_gesture = tkinter.Entry(self.window, justify='center')
        self.input_gesture.place(x=0,y=130)
        
        #Train 버튼 생성 클릭 시 listbox에 등록
        self.Train = tkinter.Button(self.window, text="    Train     ", command=lambda:self.button_pressed_Train())
        self.Train.place(x=0,y=150)
        #Stop 버튼 생성 클릭 시 listbox에 등록
        
        self.Stop = tkinter.Button(self.window, text="    Stop     ", command=lambda:self.button_pressed_stop())
        self.Stop.place(x=70,y=150) 
        
        
        # 등록된 제스쳐 글귀
        self.lbl2 = tkinter.Label(self.window, text="등록된 제스쳐")
        self.lbl2.place(x=0,y=180)
        
        
        #등록된 제스쳐 목록 및 스크롤 바 설정
        self.frame=tkinter.Frame(self.window)
        
        self.scrollbar=tkinter.Scrollbar(self.frame)
        self.scrollbar.pack(side="right", fill="y")
        
        self.listbox=tkinter.Listbox(self.frame, yscrollcommand = self.scrollbar.set)
        self.listbox.pack(side="left")
        
        self.scrollbar["command"]=self.listbox.yview
        self.frame.place(x=0,y=200)
        
        # Reset ,및 delete 버튼 클릭시, listbox 초기화
        # reset button clear the listbox
        self.Reset = tkinter.Button(self.window, text="     Reset    ", command=self.button_pressed_Reset)
                                    
        self.Reset.place(x=70,y=380)
        
        # delete button
        self.btn2 = tkinter.Button(self.window, text="    Delete   ", command= self.delete_element)
        self.btn2.place(x=0,y=380)
        
        # screen 창 
        self.src = cv2.imread(r"hand_image.jpg")
        self.img = cv2.resize(self.src, (640, 480))
        self.canvas = tkinter.Canvas(window, width = 640, height = 480)
        self.photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(self.img))
        self.canvas.create_image(0, 0, image = self.photo, anchor = tkinter.NW)
        self.canvas.place(x=150, y=0)
        
        ##create ARTMAP class
        
        self.Artmap = ARTMAP.Fuzzy_ARTMAP()
        
        ##
        
        ##network connection
        
        self.server = Server.TCP_server()
        
        ##
        
        self.streaming_screen()
        self.window.mainloop()
    
    # delete the selected elemens in listbox
    def delete_element(self):
        sel = self.listbox.curselection()
        for index in sel[::-1]:
            self.listbox.delete(index)
        ## ARTMAP 정보에서도 delete 추가해야함 
        self.State.delete(0,'end')
        self.State.insert(0, "Stop")
        self.MODE_FLAG =3
            
    # add the typing in 제스처등록  to the listbox
    def button_pressed_Train(self):
        input_string = self.input_gesture.get()
        
        #print("gigi")
        if len(input_string) == 0:
            pass
        else:
            self.gesture_list.append(input_string)
            self.listbox.insert(tkinter.END, self.input_gesture.get())
        
        self.State.delete(0,'end')
        self.State.insert(0, "...Training...")
        
        self.MODE_FLAG = 1
    # stop train the artmap
    def button_pressed_stop(self):
        self.input_gesture.delete(0,'end')
        
        self.State.delete(0,'end')
        self.State.insert(0, "Stop")
        
        self.MODE_FLAG =3
        pass
    
    def button_pressed_Test(self):
        self.State.delete(0,'end')
        self.State.insert(0, "...Test...")
        
        self.MODE_FLAG = 2
        pass
    
    def button_pressed_Reset(self):
        self.listbox.delete(0,tkinter.END)
        self.Artmap.Reset()
        self.gesture_list.clear()
        
        self.State.delete(0,'end')
        self.State.insert(0, "Reset")
        
        self.MODE_FLAG = 3
        pass
    
    def jointdata_preprocessing(self, x_points, y_points):
    #관절 정보를 받아 적절한 인풋으로 변환
        try:
            #손 목과 손 중앙 정보 추출 for nomalize 
            # 4를 곱해줘서 다른 거리정보가 0~1 사이로 맵핑이 되도록 조정 
            normalize_info = 4 * distance.euclidean([x_points[0],y_points[0]], [x_points[1],y_points[1]])
            
            
            #1 or 2 손바닥 6 엄지 10 검지 14 중지 18약지 22새끼
            # 손바닥과 손가락간의 거리
            input_data1 = [distance.euclidean([x_points[0],y_points[0]], [x_points[i],y_points[i]])/normalize_info for i in [5, 9, 13, 17, 21]]
            # 엄지과 나머지 손가락간의 거리
            input_data2 = [distance.euclidean([x_points[5],y_points[5]], [x_points[i],y_points[i]])/normalize_info for i in [9, 13, 17, 21]]
            # 검지과 나머지 손가락간의 거리
            input_data3 = [distance.euclidean([x_points[9],y_points[9]], [x_points[i],y_points[i]])/normalize_info for i in [13, 17, 21]]
            # 중지과 나머지 손가락간의 거리
            input_data4 = [distance.euclidean([x_points[13],y_points[13]], [x_points[i],y_points[i]])/normalize_info for i in [17, 21]]
            # 약지- 새
            input_data5 = [distance.euclidean([x_points[17],y_points[17]], [x_points[21],y_points[21]])/normalize_info]
            
            # 손바닥 가운데 위치 변위에 관한 정보
            
            # 이전 프레임의 정보와 비교 
            if self.MODE_FLAG ==1 or self.MODE_FLAG == 2:
                self.x_differ = self.x_differ - x_points[1]
                self.y_differ = self.y_differ - y_points[1]
                if self.x_differ > 0 :
                    self.pre_right = self.forget_param_x*self.pre_right  + self.x_differ/640
                else:
                    self.pre_left =  self.forget_param_x*self.pre_left - self.x_differ/640
                    
                if self.y_differ > 0 :
                    self.pre_up =  self.forget_param_y*self.pre_up + self.y_differ/480
                else:
                    self.pre_down = self.forget_param_y*self.pre_down - self.y_differ/480
                    print("1.self.pre_up::",self.pre_up)
            else:
                self.pre_up=0.0
                self.pre_down=0.0 
                self.pre_right=0.0
                self.pre_left=0.0
                print("2.self.pre_up::",self.pre_up)
                
                            
            # 현재 프레임의 정보를 이전 프레임 정보로 pass
            
            self.x_differ = x_points[1]
            self.y_differ = y_points[1]
            
            dir_info = [self.pre_up, self.pre_down, self.pre_right, self.pre_left]
            
            return input_data1 + input_data2 + input_data3 + input_data4 + input_data5 + dir_info # 총 15개의 성분 list + 4개의 방향 변
        except ValueError:
            pass
        except AttributeError:
            pass
        except TypeError:
            pass
    # change the canvas periodically to show the image 
    
    def streaming_screen(self):
        try:
            #print("streaming...")
            frame, self.x_points, self.y_points = self.server.activate_network()
            self.handData =self.jointdata_preprocessing(self.x_points, self.y_points)
            
            if self.MODE_FLAG == 1 and self.handData is not None :
                _ = self.Artmap.Train(self.handData, self.gesture_list.index(self.gesture_list[-1]))
            
            elif self.MODE_FLAG == 2 and self.handData is not None:
                pred = self.Artmap.Test(self.handData)
                    
                self.result_output.delete(0,'end')
                self.result_output.insert(0,self.gesture_list[pred])
            
            else:
                pass
            
            # streaming to canvas
            self.photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(frame))
            self.canvas.create_image(0, 0, image = self.photo, anchor = tkinter.NW)
            self.window.after(15, self.streaming_screen)
            
        except ValueError:
            print("Val error")
            pass
        except AttributeError:
            print("Attr error")
            pass
       
        except IndexError:
            print("Type error")
            pass         

        

    

if __name__ == "__main__":
    print("module test")
    root = Myapp(tkinter.Tk())